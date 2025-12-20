#!/usr/bin/env python3

import requests
import sqlite3
import time, datetime
from bs4 import BeautifulSoup
import sys
import html
import json
import re
import json
import requests
from bs4 import BeautifulSoup
from common import *

def parse(URL, headers):
    keyAge = "years of age"
    keyPay = "pay"

    results = {
        "age": 0,
        "pay": ""
    }

    try:
        r = requests.get(url=URL, headers=headers)
    except Exception as e:
        print("ERROR: Request failed:", e)
        return results

    if r.status_code != 200:
        print("ERROR: HTTP Response code", r.status_code)
        print("Status:", r.status_code)
        print("Headers:", r.headers)
        print("First 500 chars of body:\n", r.text[:500])
        return results

    time.sleep(1)

    # Unescape HTML entities like &lt;, &gt;, etc.
    s = html.unescape(r.text)

    # Split the text into lines
    lines = s.split('\n')

    # --- Look for age ---
    for line in lines:
        if keyAge.lower() in line.lower():
            # Try to find the number preceding "years of age"
            words = line.split()
            for i, word in enumerate(words):
                if word.isdigit() and i+1 < len(words) and "year" in words[i+1].lower():
                    results["age"] = int(word)
                    break
            if results["age"]:
                break

    # --- Look for pay ---
    for line in lines:
        if keyPay.lower() in line.lower():
            # match any valid pay expression
            m = re.search(r"\$([\d\.]+)", line)

            if m:
                # group(1) = the number after the first $
                min_pay = float(m.group(1))
                results["pay"] = min_pay
            else:
                results["pay"] = 0

            break
    return results

def parseList(url, headers):
    print("parseList: ", url)
    resultList = []
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # 1. Locate the <script> tag that contains "phApp.ddo"
    script_with_ddo = None
    for script in soup.find_all("script"):
        if script.string and "phApp.ddo" in script.string:
            script_with_ddo = script.string
            break

    if script_with_ddo is None:
        raise RuntimeError("Could not find script containing phApp.ddo")

    # 2. Extract the JSON assigned to phApp.ddo
    match = re.search(
        r"phApp\.ddo\s*=\s*({.*?});\s*phApp\.experimentData",
        script_with_ddo,
        re.DOTALL
    )

    if not match:
        raise RuntimeError("Could not extract phApp.ddo JSON")

    ddo_json_str = match.group(1)

    # 3. Convert to Python dict
    ddo = json.loads(ddo_json_str)

    # 4. Extract job list
    jobs = ddo["eagerLoadRefineSearch"]["data"]["jobs"]

    for job in jobs:
        id = "Panera:" + job["jobId"]
        title = job['title']
        cityState = job['cityState']
        iturl = job['applyUrl']
        postdate = job['postedDate']
        address =  job['address']
        address = address.split(',', 1)[0].strip()
        latitude = job['latitude']
        longitude = job['longitude']

        if not existsId(id, cursor):
            results = parse(iturl, headers)  # This gives you age and pay
            time.sleep(0.1)
            age = results["age"]

            if not isValidAge(age):
                continue  # skip this job if age is invalid

            results.update({"title": title})
            results.update({"id": id})
            results.update({"address": address})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"cityState": cityState})
            results.update({"url": iturl})
            results.update({"postdate": postdate})
            resultList.append(results)
            updateSQL(results, cursor, 'Panera')
        else:
            print("Job ", id, " already exists", iturl)

    return resultList


headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}
if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("Usage: %s <start> <num-pages>" % (sys.argv[0]))
    exit(1)

print(80 * "-")
print("Running at: ", datetime.now())
print("command: ", sys.argv[0], sys.argv[1], sys.argv[2])

connection = openInitDb()
cursor = connection.cursor()


master = []

y = int(sys.argv[1])
for x in range(int(sys.argv[2])):
    link = "https://careers.panerabread.com/global/en/c/restaurant-team-members-jobs?from="+ str(y*10) + "&s=1"
    time.sleep(0.3)
    results = parseList(link, headers)
    master += results
    y += 1
    connection.commit()

jobs = 0
count16 = 0
count18 = 0
for item in master:
    if item["age"] == 16:
        count16 += 1
    elif item["age"] == 18:
        count18 += 1
    jobs += 1

print("Total added jobs: ", jobs)
print("Jobs for 16 yr olds: ", count16)
print("Jobs for 18 yr olds: ", count18)

print("ID    Title    City    State     Age    Pay    URL")
for item in master:
    print("%s %-32s %-15s %d %-13s %s" % (item["id"], item["title"], item["cityState"], item["age"], item["pay"], item["url"][61:]))



connection.commit()
connection.close()

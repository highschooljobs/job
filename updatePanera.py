#!/usr/bin/env python3

import requests
import sqlite3
import re
import time, datetime
import sys
import json
import html
from common import *

def parse(URL):
    keyTitle = '"title" : '
    keyAge = "years old"
    keyPay = "pay"

    results = {
        "age": 0,
        "pay": "",
    }

    try:
        r = requests.get(url=URL)
    except Exception as e:
        print("ERROR: Request failed:", e)
        return results

    if r.status_code != 200:
        print("ERROR: HTTP Response code", r.status_code)
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
        m = re.search(r"\$\s*(\d+(?:\.\d{1,2})?)", line)
        if m:
            pay_value = m.group(1)
            break  # stop at first dollar amount
        else:
            results["pay"] = 0
            break
    return results



def parseList(URL, payload, header):
    print("parseList: ", URL)
    resultList = []
    r = requests.post(url=URL, headers = header, data = json.dumps(payload))
    if r.status_code != 200:
        print("ERROR: HTTP Response code  " + r.status_code)
    data = r.json()
    jobs = data["eagerLoadRefineSearch"]["data"]["jobs"]

    for i in jobs:
        title = i["title"]
        id = i["reqId"]
        id = str(id)
        iturl = i['applyUrl']
        cityState = i["cityState"]
        latitude = i["latitude"]
        longitude = i["longitude"]
        address = i["address"]  
        
        if not existsId("Panera:" + id, cursor):
            results = parse(iturl)  # This gives you age and pay
            age = results["age"]

            if not isValidAge(age):
                continue  # skip this job if age is invalid

            results.update({"title": title})
            results.update({"id": "Panera:" + id})
            results.update({"address": address})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"cityState": cityState})
            results.update({"url": iturl})
            results.update({"postdate": datetime.today().strftime("%Y.%m.%d")})
            resultList.append(results)
            updateSQL(results, cursor, 'Panera')
        else:
            print("Job ", id, " already exists", iturl)



    return resultList



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
    payload = {
    "lang": "en_global",
    "deviceType": "desktop",
    "country": "global",
    "pageName": "search-results",
    "ddoKey": "eagerLoadRefineSearch",
    "sortBy": "Most recent",
    "subsearch": "",
    "from": 0,
    "jobs": True,
    "counts": True,
    "all_fields": ["category", "state", "city", "timeType", "phLocSlider"],
    "size": 10,
    "clearAll": False,
    "jdsource": "facets",
    "isSliderEnable": True,
    "pageId": "page" + str(y),
    "siteType": "external",
    "keywords": "",
    "global": True,
    "selected_fields": {"category": ["Restaurant Team Members"]},
    "sort": {"order": "desc", "field": "postedDate"},
    "locationData": {
        "sliderRadius": 15,
        "aboveMaxRadius": True,
        "LocationUnit": "miles"
        },
    "s": "1"
    }

    headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://careers.panerabread.com",
    "Referer": "https://careers.panerabread.com/global/en/search-results",
    "User-Agent": "Mozilla/5.0"
    }

    link = url = "https://careers.panerabread.com/widgets"

    results = parseList(link, payload, headers)
    master += results
    y += 1

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

#!/usr/bin/env python3
import requests
import sqlite3
import time
from datetime import datetime
import sys
import json
import html
from bs4 import BeautifulSoup
from common import *


def parseList(URL, headers):
    print("parseList: ", URL)
    resultList = []

    r = requests.get(url=URL, headers=headers)
    if r.status_code != 200:
        print("ERROR: HTTP Response code ", r.status_code)
        return resultList

    joblist = json.loads(r.text)
    html_str = joblist.get("postings", "")
    soup = BeautifulSoup(html_str, 'html.parser')
    time.sleep(1)

    for article in soup.find_all("article", class_="result"):
        link_tag = article.find("a")
        title_tag = article.find("h4")
        addr_tag = article.find("address")
        ref_tag  = article.find("p")

        if not (link_tag and title_tag and addr_tag and ref_tag):
            continue

        title = title_tag.get_text(strip=True)

        full_address_str = addr_tag.get_text(strip=True)

        no_zip = full_address_str.rsplit(" ", 1)[0]

        # 2. Split into "street + city" and "state"
        street_and_city, state = no_zip.split(",", 1)
        street_and_city = street_and_city.strip()
        state = state.strip().upper()
        if len(state) > 2:
            state = get_state_abbreviation(state)

        # 3. Split street vs city (last token = city)
        street_only, city = street_and_city.rsplit(" ", 1)
        address = street_only.title().strip()
        city = city.title().strip()

        # Final formatted city/state
        cityState = f"{city}, {state}"

        # Reference → numeric part only
        reference_full = ref_tag.get_text(strip=True)
        ref_num = reference_full.split("Reference Number")[-1].strip()
        id = "Wendys:" + ref_num

        # Link
        rel_link = link_tag.get("href", "")
        iturl = f"https://wendys-careers.com{rel_link}"

        # Post date
        postdate = datetime.today().strftime("%Y-%m-%d")

        # PAY LOOK UP
        pay = 0
        keyPay = "<strong>Pay Range:"
        time.sleep(5)
        r = requests.get(url=iturl, headers=headers)
        if r.status_code == 200:
            s = html.unescape(r.text)
            lines = s.split('\n')
            for line in lines:
                if keyPay.lower() in line.lower():
                    loco = line.find("$")
                    subline = line[loco:]
                    end = line.find("-", loco)
                    pay_str = line[loco:end].strip(" ")
                    pay = float(pay_str.replace("$", ""))
                    break

        age = 16

        # ---- Now check if already in DB ----
        if not existsId(id, cursor):
            results = {}
            results.update({"id": id})
            results.update({"age": age})
            results.update({"pay": pay})
            results.update({"address": address})
            results.update({"title": title})
            results.update({"cityState": cityState})
            results.update({"url": iturl})
            results.update({"postdate": postdate})
            resultList.append(results)
            updateSQL(results, cursor, 'Wendys')
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
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
}
    url = "https://wendys-careers.com/wp-content/themes/wendys/get-jobs.php?ajax=1&keyword=&location=&category=crew&city=&state=&zip=&country=US&spage=" + str(y) + "&lang=&"
    results = parseList(url, headers)
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

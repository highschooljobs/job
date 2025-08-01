#!/usr/bin/env python3

import requests
import sqlite3
import time, datetime
import sys
import json
import html
from common import *

def parse(URL):
    keyAge = "years of age"
    keyPay = "pay"

    results = {
        "age": 0,
        "pay": ""
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
        if keyPay.lower() in line.lower():
            if "$" in line:
                loco = line.find("$")
                subline = line[loco:]

                # Only keep valid characters: $, digits, -, space
                valid_chars = "$0123456789-–. "
                pay_str = ""
                for ch in subline:
                    if ch in valid_chars:
                        pay_str += ch
                    else:
                        break  # stop at tag/quote/etc.

                # Normalize and clean pay string
                pay_str = (
                    pay_str.replace("–", "-")  # normalize en-dash
                            .replace(" -", "-")
                            .replace("- ", "-")
                            .strip()
                )

                results["pay"] = pay_str
                break  # stop after first match
            else:
                results["pay"] = "Competitive"
                break

    return results



def parseList(URL):
    print("parseList: ", URL)
    resultList = []
    r = requests.get(url=URL)
    if r.status_code != 200:
        print("ERROR: HTTP Response code  " + r.status_code)
    joblist = json.loads(r.text)

    for i in joblist['entries']:
        id = i["id"]
        id = str(id)
        iturl = i['apply_url']
        title = i["categories"][0]["name"]
        cityState = i["locations"][0]["canonical_name"]
        latitude = i["locations"][0]["lat"]
        longitude = i["locations"][0]["lng"]
        address = i["locations"][0]["street_address"]  
        
        if isValidAge(age):
            if not existsCityState(cityState, cursor):
                print(id)
                if len(cityState) < 4:
                    print("job " + str(id) + " skipped because has invalid cityState " + cityState)
                    continue
                citylat, citylong = getLatLong(cityState)
                command1 = "INSERT INTO cityState (cityState, latitude, longitude) VALUES ('" + str(cityState) + "', '" + str(citylat) + "', '" + str(citylong) + "')"
                cursor.execute(command1)
            else:
                cursor.execute("""
                UPDATE cityStates 
                SET job_count = job_count + 1
                WHERE cityState = ?
                """, (cityState,))

        if not existsId("Panera:" + id, cursor):
            results = parse(iturl)
            results.update({"id": "Panera:" + id})
            results.update({"address": address})
            results.update({"title": title})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"cityState": cityState})
            results.update({"url": iturl})
            results.update({"postdate": datetime.today().strftime("%Y.%m.%d")})
            resultList.append(results)
            updateSQL(results, cursor, 'Panera')
            print("Job ", id, " added", iturl)
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
    link = "https://app.careerarc.com/api/job_maps/150/job_postings?zoom=4&q=&&page=" + str(y) + "&per_page=25&bounds%5Bsouth%5D=6.0253846386907846&bounds%5Bwest%5D=-114.5425058528781&bounds%5Bnorth%5D=60.443442512139285&bounds%5Beast%5D=-78.5073496028781"

    results = parseList(link)
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

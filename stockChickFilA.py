#!/usr/bin/env python3
import json
import requests
import sqlite3
import time, datetime
from datetime import datetime
import sys
from common import *

def parseList(URL):
    print("parseList: ", URL)
    r = requests.get(url=URL)
    if r.status_code != 200:
        print(f"ERROR: HTTP Response code {r.status_code}")
    time.sleep(1)
    
    joblist = json.loads(r.text)
    resultList = [] 
         
    for i in joblist['response']['results']:
        id = i['data']['id']
        try:
            if not existsId("ChickFilA:" + id, cursor):
                title = i['data']['name']
                if "Front of House Team Member" in title:
                    age = 16
                else:
                    age = 0

                applyurl = i['data']['applicationUrl']
                cityState = i["data"]["c_jobCity"] + ", " + i['data']["c_jobState"]

                try:
                    pay = i['data']['c_payRange']
                    pay = pay.replace('$', '')
                except KeyError:
                    pay = "Competitive"

                address = i['data']['c_jobAddressLine1']

                results = {}
                results.update({"company": "Chick-Fil-A"})
                results.update({"title": title})
                results.update({"age": age})
                results.update({"pay": pay})
                results.update({"id": "ChickFilA:" + id})
                results.update({"address": address})
                results.update({"cityState": cityState})
                results.update({"url": applyurl})
                results.update({"postdate": datetime.today().strftime("%Y-%m-%d")})

                resultList.append(results)
                updateSQL(results, cursor, 'Chick-Fil-A')

            else:
                print("Job", id, "already exists")

        except Exception as e:
            print("Skipping due to error:", e)
            continue

    return resultList


if len(sys.argv) < 1 or len(sys.argv) > 1:
    print("Usage: %s just let it run" % (sys.argv[0]))
    exit(1)

print(80 * "-")
print("Running at: ", datetime.now())
print("command: ", sys.argv[0])

connection = openInitDb()
cursor = connection.cursor()



command3 = "SELECT * FROM cityStates"
cursor.execute(command3)
rows = cursor.fetchall()
master = []

for row in rows:
    time.sleep(1)
    raw = row[0]
    cityStateEncoded = raw.replace(" ", "+").replace(",", "%2C")
    link = "https://prod-cdn.us.yextapis.com/v2/accounts/me/search/vertical/query?experienceKey=cfa-jobs-experience&api_key=71620ba70d81b48c7c72331e25462ebc&v=20220511&version=PRODUCTION&locale=en&input=" + cityStateEncoded + "&verticalKey=jobs&limit=50&offset=0&retrieveFacets=true&facetFilters=%7B%7D&skipSpellCheck=false&sessionTrackingEnabled=false&sortBys=%5B%5D&source=STANDARD"

    results = parseList(link)
    master += results
    jobs = 0
    count16 = 0
    count18 = 0

    for item in results:
        if item["age"] == 16:
            count16 += 1
        jobs += 1
    print("-"*80)
    print("CityState: " + raw)
    print("Total added jobs: ", jobs)
    print("Jobs for 16 yr olds: ", count16)

    print("ID    Title    City    State     Age    Pay    URL")
    for item in results:
        print("%s %-20s %-15s %d %-13s %s" % (item["id"], item["title"], item["cityState"], item["age"], item["pay"], item["url"]))
    connection.commit()
    print("committing...")


for item in master:
    if item["age"]==16:
        count16+= 1
    jobs += 1
print("FINAL TOTAL ADDED JOBS: ", jobs)
print("Jobs for 16 yr olds: ", count16)

connection.commit()
connection.close()

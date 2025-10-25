#!/usr/bin/env python3

import requests
import sqlite3
import time, datetime
import sys
import json
import html
from urllib.parse import parse_qs 
from common import *



def parseList(URL, payload):
    print("parseList: ", URL)
    resultList = []
    parsed = parse_qs(payload)
    cleaned = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    r = requests.post(url=url, data = cleaned)
    if r.status_code != 200:
        print("ERROR: HTTP Response code  " + r.status_code)
    joblist = json.loads(r.text)
    time.sleep(0.5)
    for i in joblist['results']:

        full_address = i['document']['jobaddress']
        parts = [p.strip() for p in full_address.split(",")]
        address = parts[0]  
        cityState = ", ".join(parts[1:])
        longitude = i['document']['longitude']
        latitude = i['document']['latitude']
        postdate = i['document']['dateposted'][:10]
        pay = i['document']['basepaymin']
        id = "Target:" + i['document']['requisitionid']
        title = i['document']['title']
        if isTooSenior(title):
            break
        iturl = 'https://corporate.target.com' + str(i['document']['url'])
        if pay == None:
            time.sleep(0.5)
            r = requests.get(url=iturl)
            s = r.text
            lines = s.split('\n')
            for line in lines:
                if "$" in line.lower():
                    loco = line.find("$")
                    end = line.find(" ", loco)
                    pay_str = line[loco:end].strip(" ")
                    pay = float(pay_str.replace("$", ""))
        age = 16

        if not existsId(id, cursor):
            results = {}
            results.update({"id": id})
            results.update({"age": age})
            results.update({"pay": pay})
            results.update({"address": address})
            results.update({"title": title})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"cityState": cityState})
            results.update({"url": iturl})
            results.update({"postdate": postdate})
            resultList.append(results)
            updateSQL(results, cursor, 'Target')
        else:
            print("Job ", id, " already exists", iturl)
            break



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
    payload = "currentPage=" + str(y) + "&q=&hierarchy=Stores&remotetype=&jobcategories=&workersubtype=&scheduletype=&basepayfrequency=&organization=&locationname=&jobaddress=&profiles=&city=&state=&country=&internshipType=&jobfamily=Store%20Hourly%20-%20Sales%20Floor%7C%7CStore%20Hourly%20-%20Food%7C%7CStore%20Hourly%20-%20Front%20End&subFamilies=&culture=en-us&filtercondition=&compgrade="
    url = 'https://corporate.target.com/api/jobsearch'
    results = parseList(url, payload)
    master += results
    y += 1
    connection.commit()
    print("committing...", flush=True)


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

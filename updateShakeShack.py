#!/usr/bin/env python3

import requests
import sqlite3
import time, datetime
import sys
from common import *


def parse(URL, cursor):
    keyTitle = '<title>'
    keyAge = "or older"
    keyPays = [
    '"og:description" content="Pay Range - ',
    'content="Hourly Rate:'
]
    keyCity = '"addressLocality":"'


    results = {
        "title" : "",
        "age": 0,
        "pay": "",
        "cityState" : ""
    }

    r = requests.get(url=URL)
    if r.status_code != 200:
        print("ERROR: HTTP Response code  " + str(r.status_code))
    time.sleep(1)
    s = r.text

    # Split the text into lines
    lines = s.split('\n')

    # find the title
    for line in lines:
        if keyTitle.lower() in line.lower():
            loco = line.find(keyTitle)
            title_str = parseTerm(s, keyTitle, "|", loco)
            try:
                results["title"] = title_str
            except ValueError:
                pass
    


    # look for the age
    for line in lines:
        if keyAge.lower() in line.lower():
            loco = line.lower().find(keyAge.lower())
            assert loco > -1, "could not find age"
            loco -= 9

            age_str = line[loco:loco + 3].strip()
            try:
                results["age"] = int(age_str)
            except ValueError:
                pass
    # look for the pay
    for line in lines:
        for keyPay in keyPays:
            if keyPay.lower() in line.lower():
                if "$" in line.lower():
                    loco = line.find("$")
                    end = line.find(" ", loco)
                    pay_str = line[loco:end].strip(' ')
                    if "/" in pay_str:
                        pay_str = pay_str.split("/")[0].strip()
                else:
                    pay_str = "Competitive"
                try:
                    results["pay"] = pay_str
                except ValueError:
                    pass

    # look for the city and state
    
    for line in lines:
        if keyCity.lower() in line.lower():
            loco = line.find(keyCity) - len(keyCity)
            city = parseTerm(s, 'addressLocality":"', '"', loco)
            state = parseTerm(s, 'addressRegion":"', '"', loco)

            cityState = city + ", " + state
            results["cityState"] = cityState

            if not existsCityState(cityState, cursor):
                latitude, longitude = getLatLong(cityState)
                command1 = "INSERT INTO cityState (cityState, latitude, longitude) VALUES ('" + str(cityState) + "', '" + str(latitude) + "', '" + str(longitude) +  "')"
                cursor.execute(command1)
    return results

def updateSQL(dictionary, cursor):
    command1 = "INSERT INTO jobs (company, title, id, age, pay, address, cityState, longitude, latitude, url) VALUES ('Shake Shack', '" + str(dictionary["title"]) + "', '" + str(dictionary["id"]) + "', '" + str(dictionary["age"]) + "', '" + str(dictionary["pay"]) + "', '" + str(dictionary["address"]) + "', '" + str(dictionary["cityState"]) + "', '" + str(dictionary["longitude"]) + "', '" + str(dictionary["latitude"]) + "', '<a href=\"" + str(dictionary["url"]) + "\" target=\"_blank\"> Apply</a>')"
    cursor.execute(command1)




def parseList(URL):
    print("parseList: ", URL)
    resultList = []
    r = requests.get(url=URL)
    if r.status_code != 200:
        print("ERROR: HTTP Response code  " + str(r.status_code))
    time.sleep(1)
    s = r.text


    pos = s.find('href="https://shake-shack.daliajobs.com/job/', 0)
    i = 0
    while pos != -1:

        # look for job ID
        id = parseTerm(s, 'href="https://shake-shack.daliajobs.com/job/', '/', pos)
        # look for latitude
        latitude = 0
        # look for job address
        address = parseTerm(s, 'text-capitalize ms-2 job-location text-grey">', '<', pos)
        comma_index = address.find(',')
        address = address[comma_index + 2:]
        address = address.split(',', 1)[0]
        # look for url
        iturl = parseTerm(s, 'href="https://shake-shack.daliajobs.com/job/', '"', pos)
        iturl = "https://shake-shack.daliajobs.com/job/" + iturl
        print("url: ", iturl, flush = True)      
        # look for longitude
        longitude = 0

        # loop back to find the next ID
        pos = s.find('href="https://shake-shack.daliajobs.com/job/', pos + 10)

        i += 1
        


        if not existsId("ShakeShack:" +  id,  cursor):
            results = parse(iturl, cursor)
            results.update({"id": "ShakeShack:" +  id})
            latitude, longitude = getLatLong(address + ", " + results["cityState"])
            results.update({"address": address})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"url": iturl})
            resultList.append(results)
            updateSQL(results, cursor)
            print("  ", i, " Job ", id, " added", iturl)
        else:
            print("  ", i, "Job ", id, " already exists", iturl)



    return resultList


if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("Usage: %s <start> <num-pages>" % (sys.argv[0]))
    exit(1)

print(80 * "-")
print("Running at: ", datetime.datetime.now())
print("command: ", sys.argv[0], sys.argv[1], sys.argv[2])

connection = sqlite3.connect("/var/lib/db/jobs.db")
cursor = connection.cursor()

command1 = "CREATE TABLE IF NOT EXISTS jobs (company TEXT, title TEXT, id TEXT, age TEXT, pay TEXT, address TEXT, cityState TEXT, longitude FLOAT, latitude FLOAT, url TEXT)"
cursor.execute(command1)

command2 = "CREATE TABLE IF NOT EXISTS cityState (cityState TEXT, latitude FLOAT, longitude FLOAT)"
cursor.execute(command2)

master = []

y = int(sys.argv[1])
for x in range(int(sys.argv[2])):
    link = "https://shake-shack.daliajobs.com/job-search?page=" + str(y)
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

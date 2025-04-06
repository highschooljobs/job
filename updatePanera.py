#!/usr/bin/env python3

import requests
import sqlite3
import time, datetime
import sys

def parse(URL):
    keyTitle = '"title" : '
    keyAge = "years of age"
    keyPay = "pay"


    results = {
        "title" : "",
        "age": 0,
        "pay": ""
    }

    r = requests.get(url=URL)
    if r.status_code != 200:
        print("ERROR: HTTP Response code  " + r.status_code)
    time.sleep(1)
    s = r.text

    # Split the text into lines
    lines = s.split('\n')

    # find the title
    for line in lines:
        if keyTitle.lower() in line.lower():
            loco = line.find(keyTitle) + len(keyTitle) + 1
            title_str = line[loco: - 2].strip()
            try:
                results["title"] = title_str
            except ValueError:
                pass
    


    # look for the age
    for line in lines:
        if keyAge.lower() in line.lower():
            loco = line.lower().find(keyAge.lower())
            assert loco > -1, "could not find age"
            loco -= 3

            age_str = line[loco:loco + 2].strip()
            try:
                results["age"] = int(age_str)
            except ValueError:
                pass
    # look for the pay
    for line in lines:
        if keyPay.lower() in line.lower():
            if "$" in line.lower():
                loco = line.find("$")
                end = line.find(" ", loco)
                pay_str = line[loco:end].strip(" ")
            else:
                pay_str = "Competitive"
            try:
                results["pay"] = pay_str
            except ValueError:
                pass

    return results



def parseTerm(s, keyStart, keyEnd, lastIndex):
    pos = s.find(keyStart, lastIndex)
    start = pos + len(keyStart)
    end = s.find(keyEnd, start)
    
    term = s[start:end].strip()

    return term

def existsCityState(cityState, cursor):
    command1 = 'SELECT EXISTS(SELECT 1 FROM cityState WHERE cityState="' + str(cityState) + '")'
    cursor.execute(command1)
    result = cursor.fetchone()

    return result[0]

def existsId(jobId, cursor):
    command1 = 'SELECT EXISTS(SELECT 1 FROM jobs WHERE id="' + str(jobId) + '")'
    cursor.execute(command1)
    result = cursor.fetchone()

    return result[0]

def updateSQL(dictionary, cursor):
    command1 = "INSERT INTO jobs (company, title, id, age, pay, cityState, longitude, latitude, url) VALUES ('Panera', '" + str(dictionary["title"]) + "', '" + str(dictionary["id"]) + "', '" + str(dictionary["age"]) + "', '" + str(dictionary["pay"]) + "', '" + str(dictionary["cityState"]) + "', '" + str(dictionary["longitude"]) + "', '" + str(dictionary["latitude"]) + "', '<a href=\"" + str(dictionary["url"]) + "\" target=\"_blank\"> Apply</a>')"
    cursor.execute(command1)


def parseList(URL):
    print("parseList: ", URL)
    resultList = []
    r = requests.get(url=URL)
    if r.status_code != 200:
        print("ERROR: HTTP Response code  " + r.status_code)
    time.sleep(1)
    s = r.text


    pos = s.find('"reqId":"JR', 0)
    i = 0
    while pos != -1:

        # look for job ID
        id = parseTerm(s, '"reqId":"JR', '"', pos)
        # look for latitude
        latitude = parseTerm(s, '"latitude":"', '"', pos)
        # look for job address
        address = parseTerm(s, '"address":"', '"', pos)
        # look for url
        iturl = parseTerm(s, '"applyUrl":"', "/apply", pos)
        #print("url: ", iturl, flush = True)      
        # look for longitude
        longitude = parseTerm(s, '"longitude":"', '"', pos)
        # look for the cityState
        cityState = parseTerm(s, '"cityState":"', '"', pos)

        # loop back to find the next ID
        pos = s.find('"reqId":"JR', pos + 10)

        i += 1
        
        if not existsCityState(cityState, cursor):
            command1 = "INSERT INTO cityState (cityState) VALUES ('" + str(cityState) + "')"
            cursor.execute(command1)

        if not existsId(id, cursor):
            results = parse(iturl)
            results.update({"id": id})
            results.update({"address": address})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"cityState": cityState})
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

command1 = "CREATE TABLE IF NOT EXISTS jobs (company TEXT, title TEXT, id TEXT, age TEXT, pay TEXT, cityState TEXT, longitude TEXT, latitude TEXT, url TEXT)"
cursor.execute(command1)

command2 = "CREATE TABLE IF NOT EXISTS cityState (cityState TEXT)"
cursor.execute(command2)

master = []

y = int(sys.argv[1])
for x in range(int(sys.argv[2])):
    link = "https://careers.panerabread.com/global/en/search-results?keywords=&from=" + str(y) + "0&s=1"
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

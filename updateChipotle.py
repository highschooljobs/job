#!/usr/bin/env python3

import requests
import sqlite3
import time, datetime
import sys
from common import *

def parse(URL, cursor):
    keyTitle = '"title":"'
    keyAge = " years"
    keyPay = "SalaryRange-$"
    keyCity = '"addressLocality":"'


    results = {
        "title" : "",
        "age": 0,
        "pay": "",
        "cityState": ""
    }
    r = requests.get(url=URL)
    if r.status_code != 200:
        print(f"ERROR: HTTP Response code {r.status_code}")
    time.sleep(1)
    s = r.text

    # Split the text into lines
    lines = s.split('\n')

    # find the title
    for line in lines:
        if keyTitle.lower() in line.lower():
            loco = line.find(keyTitle) + len(keyTitle)
            title_str = parseTerm(s, '"title":"', '"', loco)
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

            age_str = line[loco:loco + 3].strip()
            try:
                results["age"] = int(age_str)
            except ValueError:
                pass


    # look for the pay
    for line in lines:
        if keyPay.lower() in line.lower():
            if "$" in line.lower():
                loco = line.find("$")
                end = line.find("-/", loco)
                pay_str = line[loco:end].strip(" ")
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
            state = get_state_abbreviation(state)
            cityState = city + ", " + state
            results["cityState"] = cityState

            if not existsCityState(cityState, cursor):
                latitude, longitude = getLatLong(cityState)
                command1 = "INSERT INTO cityState (cityState, latitude, longitude) VALUES ('" + str(cityState) + "', '" + str(latitude) + "', '" + str(longitude) +  "')"
                cursor.execute(command1)
            else:
                cursor.execute("""
                UPDATE cityStates
                SET job_count = job_count + 1
                WHERE cityState = ?
                """, (cityState,))

    return results



def parseList(URL) :
    print("parseList: ", URL)
    resultList = []
    r = requests.get(url=URL)
    if r.status_code != 200:
        (f"ERROR: HTTP Response code {r.status_code}")
    time.sleep(1)
    s = r.text

    pos = s.find('href=\\"/job', 0)
    i = 0
    while pos != -1:
        # look for job ID
        id = parseTerm(s, 'data-job-id=\\"', '\\', pos)
        # look for job address
        address = parseTerm(s, 'address\\">', ',', pos)
        # look for url
        iturl = parseTerm(s, 'href=\\"/job', "\\", pos)
        iturl = "https://jobs.chipotle.com/job/" + iturl
        #print("url: ", iturl, flush = True)      
        #look for latitude and longitude

        # loop back to find the next ID
        pos = s.find('href=\\"/job', pos + 12)

        i += 1


        if not existsId("Chipotle:" + id, cursor):
            results = parse(iturl, cursor)
            latitude, longitude = getLatLong(address + ", " + results["cityState"])
            results.update({"id": "Chipotle:" + id})
            results.update({"address": address})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"url": iturl})
            results.update({"postdate": datetime.today().strftime("%Y.%m.%d")})
            resultList.append(results)
            updateSQL(results, cursor, 'Chipotle')
            print("  ", i, " Job ", id, " added", iturl)
        else:
            print("  ", i, "Job ", id, " already exists", iturl)

 


    return resultList


if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("Usage: %s <start> <num-pages>" % (sys.argv[0]))
    exit(1)

print(80 * "-")
print("Running at: ", datetime.now())
print("command: ", sys.argv[0], sys.argv[1], sys.argv[2])

connection = sqlite3.connect("/var/lib/db/jobs.db")
cursor = connection.cursor()
command1 = "CREATE TABLE IF NOT EXISTS jobs (company TEXT, title TEXT, id TEXT, age INTEGER, pay FLOAT, address TEXT, cityState TEXT, longitude FLOAT, latitude FLOAT, url TEXT, postdate TEXT, lastverify TEXT, count INTEGER)"
cursor.execute(command1)

command2 = "CREATE TABLE IF NOT EXISTS cityState (cityState TEXT, latitude FLOAT, longitude FLOAT, job_count INTEGER)"
cursor.execute(command2)

master = []

y = int(sys.argv[1])
for x in range(int(sys.argv[2])):
    link = "https://jobs.chipotle.com/search-jobs/results?ActiveFacetID=0&CurrentPage=" + str(y) +  "&RecordsPerPage=10&TotalContentResults=&Distance=50&RadiusUnitType=0&Keywords=&Location=&ShowRadius=False&IsPagination=False&CustomFacetName=&FacetTerm=&FacetType=0&FacetFilters%5B0%5D.ID=6252001-5332921&FacetFilters%5B0%5D.FacetType=3&FacetFilters%5B0%5D.Count=456&FacetFilters%5B0%5D.Display=California%2C+United+States&FacetFilters%5B0%5D.IsApplied=true&FacetFilters%5B0%5D.FieldName=&SearchResultsModuleName=Search+Results&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=0&SearchType=5&PostalCode=&ResultsType=0&fc=&fl=&fcf=&afc=&afl=&afcf=&TotalContentPages=NaN"
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
    print("%s %-20s %-15s %d %-13s %s" % (item["id"], item["title"], item["cityState"], item["age"], item["pay"], item["url"]))




connection.commit()
connection.close()

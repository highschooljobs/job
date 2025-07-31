#!/usr/bin/env python3
import json
import requests
import sqlite3
import time, datetime
import sys
from common import *



def updateSQL(dictionary, cursor):
    command1 = """
    INSERT INTO jobs 
    (company, title, id, age, pay, address, cityState, longitude, latitude, url) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        dictionary["company"],
        dictionary["title"],
        dictionary["id"],
        dictionary["age"],
        dictionary["pay"],
        dictionary["address"],
        dictionary["cityState"],
        dictionary["longitude"],
        dictionary["latitude"],
        f'<a href="{dictionary["url"]}" target="_blank"> Apply</a>'
    )

    cursor.execute(command1, values)


def parseList(URL):
    print(URL)
    r = requests.get(url=URL)
    if r.status_code != 200:
        print(f"ERROR: HTTP Response code {r.status_code}")
    
    joblist = json.loads(r.text)
    resultList = [] 
         
    for i in joblist['response']['results']:
        time.sleep(1)
        id = i['data']['id']
        if not existsId("ChickFilA:" + id, cursor):
            try:
                title = i['data']['name'] 
                if title == "Front of House Team Member":
                    age = 16
                else:
                    continue
                applyurl = i['data']['applicationUrl']
                cityState = i["data"]["c_jobCity"] + ", " + i['data']["c_jobState"]
                try:
                    pay = i['data']['c_payRange']
                except KeyError:
                    pay = "Competitive"
                address = i['data']['c_jobAddressLine1']
                latitude, longitude = getLatLong(address + ", " + cityState)
            except:
                continue
            results = {}


            results.update({"company": "Chick-Fil-A"})
            results.update({"title": title})
            results.update({"age": age})
            results.update({"pay": pay})
            results.update({"id": "ChickFilA:" + id})
            results.update({"address": address})
            results.update({"cityState": cityState})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"url": applyurl})
            resultList.append(results)
            print("results: ",  results)
            print()
            updateSQL(results, cursor)
            print( "Job ", id, " added", applyurl)

            if not existsCityState(cityState, cursor):
                latitude, longitude = getLatLong(cityState)
                command1 = "INSERT INTO cityState (cityState, latitude, longitude) VALUES ('" + str(cityState) + "', '" + str(latitude) + "', '" + str(longitude) +  "')"
                cursor.execute(command1)
        else:
            print("Job already added")
    return resultList



if len(sys.argv) < 3 or len(sys.argv) > 3:
    print("Usage: %s <start-index-citystates> <num-citystates>" % (sys.argv[0]))
    exit(1)

print(80 * "-")
print("Running at: ", datetime.datetime.now())
print("command: ", sys.argv[0], sys.argv[1])

connection = sqlite3.connect("/var/lib/db/jobs.db")
cursor = connection.cursor()

command1 = "CREATE TABLE IF NOT EXISTS jobs (company TEXT, title TEXT, id TEXT, age TEXT, pay TEXT, address TEXT, cityState TEXT, longitude FLOAT, latitude FLOAT, url TEXT)"
cursor.execute(command1)

command2 = "CREATE TABLE IF NOT EXISTS cityState (cityState TEXT, latitude FLOAT, longitude FLOAT)"
cursor.execute(command2)




start_index = int(sys.argv[1])  # e.g., 5
count = int(sys.argv[2])        # e.g., 10

command3 = "SELECT * FROM cityState"
cursor.execute(command3)
rows = cursor.fetchall()

selected_rows = rows[start_index:start_index + count]
master = []
for row in selected_rows:
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
    for item in master:
        print("%s %-20s %-15s %d %-13s %s" % (item["id"], item["title"], item["cityState"], item["age"], item["pay"], item["url"]))

for item in master:
    if item["age"]==16:
        count16+= 1
    jobs += 1
print("FINAL TOTAL ADDED JOBS: ", jobs)
print("Jobs for 16 yr olds: ", count16)

connection.commit()
connection.close()

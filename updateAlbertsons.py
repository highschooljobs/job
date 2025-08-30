#!/usr/bin/env python3
import json
import requests
import sqlite3
import time, datetime
import sys
from common import *



def parseList(URL):
    print(URL)
    r = requests.get(url=URL)
    if r.status_code != 200:
        print(f"ERROR: HTTP Response code {r.status_code}")
    time.sleep(1)
    
    joblist = json.loads(r.text)
    resultList = [] 
    
    for i in joblist['items'][0]['requisitionList']:
        id = i["Id"]
        postdate = i['PostedDate']
        if not existsId("Albertsons:" + id, cursor): 
             
            r = requests.get(url="https://eofd.fa.us6.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitionDetails?expand=all&onlyData=true&finder=ById;Id=%22" + id + "%22,siteNumber=CX_1001")
            time.sleep(1)
            if r.status_code != 200:
                print(f"ERROR: HTTP Response code {r.status_code}")
            time.sleep(1)

            
            jobdata = json.loads(r.text)
            title = i["Title"]
            if isTooSenior(title):
                break
            id =  i["Id"]
            applyurl = "https://eofd.fa.us6.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/" + id
            print(applyurl)
            banner =  jobdata['items'][0]['requisitionFlexFields'][0]['Value']
            if "18 years of age" not in jobdata['items'][0]['ExternalDescriptionStr']:
                age = 16
            else:
                age = 18
            location =  jobdata['items'][0]['PrimaryLocation']
            cityState = location.replace(", United States", "")
            if len(jobdata['items'][0]['workLocation']) > 0:
               address =  jobdata['items'][0]['workLocation'][0]['AddressLine1']
            else:
                continue
            latitude = jobdata['items'][0]['workLocation'][0]['Latitude']
            longitude =  jobdata['items'][0]['workLocation'][0]['Longitude']
            if len(jobdata['items'][0]['requisitionFlexFields']) == 3:
                pay =  str(jobdata['items'][0]['requisitionFlexFields'][1]['Value'])
                pay = pay.replace('$', '')
            elif len(jobdata['items'][0]['requisitionFlexFields']) == 2:
                pay = jobdata['items'][0]['requisitionFlexFields'][1]['Value']
            else:
                pay = "Competitive"
            results = {}
    
            results.update({"company": banner})
            results.update({"title": title})
            results.update({"age": age})
            results.update({"pay": pay})
            results.update({"id": "Albertsons:" + id})
            results.update({"address": address})
            results.update({"cityState": cityState})
            results.update({"latitude": latitude})
            results.update({"longitude": longitude})
            results.update({"url": applyurl})
            results.update({"postdate": postdate})
            resultList.append(results)
            print("results: ",  results)
            print()
            updateSQL(results, cursor, banner)
            print( "Job ", id, " added", applyurl)

            if isValidAge(age): 
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
        else:
            print("Job already added")
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
    link = 'https://eofd.fa.us6.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList.workLocation,requisitionList.otherWorkLocations,requisitionList.secondaryLocations,flexFieldsFacet.values,requisitionList.requisitionFlexFields&finder=findReqs;siteNumber=CX_1001,facetsList=LOCATIONS%3BWORK_LOCATIONS%3BWORKPLACE_TYPES%3BTITLES%3BCATEGORIES%3BORGANIZATIONS%3BPOSTING_DATES%3BFLEX_FIELDS,limit=25,lastSelectedFacet=LOCATIONS,selectedCategoriesFacet=300000034963805,selectedLocationsFacet=300000002736067,sortBy=POSTING_DATES_DESC,offset=' + str(int(y)*25)
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

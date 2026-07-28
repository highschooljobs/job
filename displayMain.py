#!/usr/bin/env python3
import os.path
import sqlite3
import requests
import json
import os
from urllib.parse import parse_qs
from common import *

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
def load_template(filename):
    with open(os.path.join(TEMPLATE_DIR, filename), "r") as f:
        return f.read()

def isBadCity(city):
    return any(char in city for char in ["'", '"', ";", "--", "<", ">", "\\"])

def IP2LatLong(ip):
    url =  "https://api.ipgeolocation.io/v2/ipgeo?apiKey=78e184f3697b437f933f83d4419f8712&ip=" + str(ip)
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)

    usr_lat = data['location']['latitude']
    usr_long = data['location']['longitude']
    return usr_lat, usr_long

def findLatLong(cursor, citySelected, city, arguments, usr_lat, usr_long):
    lat = long = None
    if citySelected:
        if city == "current" and "lat" in arguments and "long" in arguments:
            lat = float(arguments["lat"][0])
            long = float(arguments["long"][0])
        else:
            cursor.execute('SELECT latitude, longitude FROM cityStates WHERE cityState = ?', (city,))
            latLong = cursor.fetchall()
            lat = float(latLong[0][0])
            long = float(latLong[0][1])
    else:
        # Use IP-based location
        lat = float(usr_lat)
        long = float(usr_long)
    return lat, long

def getJobsInBox(cursor, lat, long, deg, citySelected, city, dbg):
    minLong = long - deg
    maxLong = long + deg
    minLat = lat - deg
    maxLat = lat + deg

    citymatch = f'cityState = "{city}" OR' if citySelected else ""
    inbox     = f' (latitude > {minLat} AND latitude < {maxLat} AND longitude > {minLong} AND longitude < {maxLong})'
    geocond   = ' AND ( ' + citymatch + inbox + ')'

    # Build SQL query regardless of method used
    if citySelected or dbg or (lat is not None and long is not None):
        select = 'SELECT company, title, id, age, pay, address, cityState, latitude, longitude, url FROM jobs WHERE age > 0 AND age < 18' + geocond
        cursor.execute(select)
        jobsRaw = cursor.fetchall()
    else:
        jobsRaw = []
    return jobsRaw

def sortByDist(jobsRaw, lat, long):
    jobs = []
    for row in jobsRaw:
        job = []
        distance = calcDistance(lat, long, row[7], row[8]) if lat is not None and long is not None else 0
        for x in row:
            job.append(x)
        job.insert(0, str(round(distance, 1)))
        urlidx = len(job)-1
        atag = job[urlidx]
        url = atag[9:-28]
        fulltag = '<a href="' + url + '"  ping="https://mangohub.app/ping?joburl=' + url + '" target="_blank"> Apply</a>'
        job[urlidx] = fulltag
        jobs.append(job)
    jobs.sort(key=lambda x : float(x[0]))
    return jobs

def format_pay(value):
    s = str(value).replace("$", "").strip()
    if s in ("0.0", "0", ""):
        return 0  # signal "no pay listed"
    if "-" in s:
        return s
    try:
        return f"{float(s):.2f}"
    except ValueError:
        return s

# Connect to the database
if not os.path.exists(dbpath):
    print("Error: jobs.db not found!")
    exit()

conn = sqlite3.connect(dbpath)
cursor = conn.cursor()

cursor.execute('''
    SELECT cityState, job_count, latitude, longitude
    FROM cityStates
    WHERE job_count > 2
    ORDER BY cityState
''')
cityStateData = cursor.fetchall()
cities = [row[0] for row in cityStateData]  # list of city names
nJobsInCity = {row[0]:row[1] for row in cityStateData}  # dictionary of (cityState, job_count)
cityState = [(row[0], row[2], row[3]) for row in cityStateData]  # list of (cityState, lat, long)
cities.sort()

#find current number of jobs
cursor.execute('SELECT COUNT(1) FROM jobs WHERE AGE < 18 AND AGE > 0')
currentJobs = cursor.fetchone()[0]

# this is to find if user is looking for a cityState
query_string = os.environ.get("QUERY_STRING", "")
arguments = parse_qs(query_string)

#set up debug mode
dbg_mode = "dbg" in arguments
dbg = dbg_mode and arguments["dbg"][0]  == '1'

cityFound = "cityState" in arguments
city = arguments["cityState"][0] if cityFound else ""

# checks whether the user selected a valid city
citySelected = cityFound and not isBadCity(city) and (city in cities or city == "current")

#check if user is on a phone
phone = "Phone" in os.environ["HTTP_USER_AGENT"] or "Mobile" in os.environ["HTTP_USER_AGENT"]

#get the ip address of user
ip = os.environ["REMOTE_ADDR"]
usr_lat, usr_long = IP2LatLong(ip)

lat, long = findLatLong(cursor, citySelected, city, arguments, usr_lat, usr_long)
    
jobsRaw = getJobsInBox(cursor, lat, long, 0.1, citySelected, city, dbg)

jobs = sortByDist(jobsRaw, lat, long)

columns = ["distance", "company", "title", "id", "age", "pay", "address", "cityState", "latitude", "longitude", "url"]
exclude = ["id", "longitude", "latitude"]

conn.close()


# change the style if your on mobile view vs computer
style = load_template("style.html")
navigator = load_template("navigator.html")

print("Content-type:text/html")
print(style)
print("  <body>")
print('''
<div class="header-background">
  <h1>mangohub.app</h1>
  <p>Find Jobs for Highschool Teens</p>
  <p> 16 years old and 17 years old</p>
  <p>Current Job Count: ''')
print(f"{currentJobs:,d}") 
print('''</p>
</div>
''')
print(navigator)
if dbg:
    print("City Selected: " + str(citySelected) +  "</br>")
    print("City: '" + city + "'</br>")
    for i in arguments.keys():
        print(i + " '" +  arguments[i][0] + "'</br>")


# Search bar with Enter key support
# Replace the existing datalist section with this:

print('''
<div style="text-align: center; margin-top: 20px;">
  <label for="citySearch">Search City: </label>
  <input
    list="cities"
    id="citySearch"
    oninput="handleInput()"
    placeholder="Start typing..."
    onkeydown="handleKey(event)"
    onfocus="this.select()"   
    ''')
if citySelected:
    print(f'''
    value="{city}"
    ''')
print('''
    onkeydown="handleKey(event)"
  />
  <button onclick="useCurrentLocation()" title="Use Current Location"><i class="fas fa-location-crosshairs"></i></button>
  <datalist id="cities">
    <!-- Options will be populated by JavaScript -->
  </datalist>
</div>
''')

print("<script>")
print("const cityData = [")
for city in cities:
    count = nJobsInCity[city]
    print(f'  {{name: "{city}", display: "{city} ({count})"}},')
print("];")
print("</script>")
print('<script src="/script.js"></script>')


# PRINT TABLE
# JOBS TABLE
if not jobs and not dbg:
    print("<p style='text-align: center; margin-top: 20px;'>Please select a city to view jobs.</p>")
if jobs or dbg:
    print("    <table>")
    print("      <tr>")
    if dbg:
        print("        <th>Distance</th>")
        print("        <th>Company</th>")
        print("        <th>Title</th>")
        print("        <th>Id</th>")
        print("        <th>Age</th>")
        print("        <th>Pay</th>")
        print("        <th>Address</th>")
        print("        <th>cityState</th>")
        print("        <th>Latitude</th>")
        print("        <th>Longitude</th>")
        print("        <th>url</th>")
    else:
        if phone:
            print("<th> Jobs </th>")
        else:
            print("        <th>Distance</th>")
            print("        <th>Company</th>")
            print("        <th>Title</th>")
            print("        <th>Age</th>")
            print("        <th>Pay</th>")
            print("        <th>Address</th>")
            print("        <th>cityState</th>")
            print("        <th>url</th>")

    print("      </tr>")
    if dbg:
        for i in jobs:
            print("      <tr>")
            for idx, x in enumerate(i):
                if idx == 0:
                    print("<td style='text-align: center;'>" + str(x) + " mi </td>")
                elif idx == 5:
                    pay = format_pay(x)
                    print("<td style='text-align: center;'> - </td>" if pay is None else f"<td style='text-align: center;'>${pay}</td>")
                else:
                    print("<td>" + str(x) + "</td>")
            print("      </tr>")
    else:
        if phone:
            for job in jobs:
                pay = format_pay(job[5])
                pay_display = "-" if pay is None else f"${pay}"
                print("<tr>")
                print("<td>")
                print(job[1] + ", " +  str(job[2]) + "<br> ")
                print(job[6] + ", " + str(job[7]) + "<br>")
                print(job[0] + " mi, "  + str(job[4]) + "yo, " + pay_display + " " + job[10])
                print("</td>")
                print("</tr>")
        else:
            for i in jobs:
                print("      <tr>")
                for idx, value in enumerate(i):
                    if columns[idx] not in exclude:
                        if value == i[0]:
                            print("<td style='text-align: center;'>" + str(value) + " mi</td>")
                        elif idx == 5:
                            pay = format_pay(value)
                            print("<td style='text-align: center;'> - </td>" if pay is None else f"<td style='text-align: center;'>${pay} </td>")
                        else:
                            print("<td>" + str(value) + "</td>")
                print("      </tr>")

    print("    </table>")
if dbg:
    print("Total jobs: ", len(jobs), "<br>")
    print(jobs)
    print ("<font size=+1>Environment</font><br>")
    for param in os.environ.keys():
        print("<b>%20s</b>: %s<br>" % (param, os.environ[param]))
    print(lat, long, "<br>")
    print(select, "<br>")

print("  </body>")

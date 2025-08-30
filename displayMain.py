#!/usr/bin/env python3
import os.path
import sqlite3
import requests
import json
import os
from urllib.parse import parse_qs
from common import *

#this is the jobpath to the database
jobpath = "/var/lib/db/jobs.db"

# function to determine if cityState is valid or not
def isBadCity(city):
    return any(char in city for char in ["'", '"', ";", "--", "<", ">", "\\"])
# Connect to the database
conn = sqlite3.connect(jobpath)
cursor = conn.cursor()

cursor.execute('''
    SELECT cityState, job_count, latitude, longitude
    FROM cityStates
    WHERE job_count > 4
    ORDER BY cityState
''')
cityStateData = cursor.fetchall()
validCities = {row[0] for row in cityStateData}  # set of city names
cityStateCounts = [(row[0], row[1]) for row in cityStateData]  # list of (cityState, job_count)
cityState = [(row[0], row[2], row[3]) for row in cityStateData]  # list of (cityState, lat, long)
cityState.sort(key=lambda x: x[0])

#find current amount of jobs
cursor.execute('SELECT COUNT(1) FROM jobs WHERE AGE < 18 AND AGE > 0')
currentJobs = cursor.fetchone()[0]


query_string = os.environ.get("QUERY_STRING", "")
arguments = parse_qs(query_string)

cityFound = "cityState" in arguments
city = arguments["cityState"][0] if cityFound else ""

citySelected = cityFound and not isBadCity(city) and (city in validCities or city == "current")

#check if user is on a phone
phone = "Phone" in os.environ["HTTP_USER_AGENT"] or "Mobile" in os.environ["HTTP_USER_AGENT"]

#get the ip address of user
ip = os.environ["REMOTE_ADDR"]

#using ip address, get lat and long of user
url =  "https://api.ipgeolocation.io/v2/ipgeo?apiKey=78e184f3697b437f933f83d4419f8712&ip=" + str(ip)
payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)
data = json.loads(response.text)

usr_lat = data['location']['latitude']
usr_long = data['location']['longitude']


dbg_mode = "dbg" in arguments
dbg = True if dbg_mode and arguments["dbg"][0]  == '1' else False


if not os.path.exists(jobpath):
    print("Error: jobs.db not found!")
    exit()



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
    
minLong = long - 0.1
maxLong = long + 0.1
minLat = lat - 0.1
maxLat = lat + 0.1

citymatch = f'cityState = "{city}" OR' if citySelected else ""
inbox     = f' (latitude > {minLat} AND latitude < {maxLat} AND longitude > {minLong} AND longitude < {maxLong})'
geocond   = ' AND ( ' + citymatch + inbox + ')'

# Build SQL query regardless of method used
if citySelected or dbg or (lat is not None and long is not None):
    select = 'SELECT company, title, id, age, pay, address, cityState, latitude, longitude, url FROM jobs WHERE age = 16' + geocond
    cursor.execute(select)
    jobsRaw = cursor.fetchall()
else:
    jobsRaw = []

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

columns = ["distance", "company", "title", "id", "age", "pay", "address", "cityState", "latitude", "longitude", "url"]
exclude = ["id", "longitude", "latitude"]

conn.close()


# change the style if your on mobile view vs computer
style = """
        <head>
        <link rel="icon" href="/mangohub.png" type="image/png">
       <title>MangoHub - Jobs for High School Teens</title>
        <meta name="description" content="Find local jobs for high school students. MangoHub helps teens discover part-time work opportunities near them.">
        <meta name="keywords" content="teen jobs, high school jobs, part-time jobs, local jobs, student employment">
        <meta name="author" content="MangoHub">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta property="og:title" content="MangoHub - Jobs for High School Teens">
        <meta property="og:description" content="Find local jobs for high school students.">
        <meta property="og:image" content="https://mangohub.app/mangohub.png">
        <meta property="og:url" content="https://mangohub.app/">
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-725428PR4P"></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'G-725428PR4P');
        </script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
        table {
        margin-top: 20px;
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }

        body{
        font-family: arial, sans-serif;
        }

        select, input{
        font-family: arial, sans-serif;
        font-size: 110%;
        }
        td, th {
          border: 1px solid #e0e0e0;
          text-align: left;
          padding: 12px 16px;
          vertical-align: middle;
        }

        td:nth-child(2) {
          max-width: 300px;
          word-wrap: break-word;
        }

        tr:nth-child(even) {
          background-color: #f9f9f9;
        }

        tr:hover {
          background-color: #f0f4ff;
          transition: background-color 0.2s ease-in-out;
        }

        th {
          background-color: #f2f2f2;
          font-weight: bold;
          color: #333;
        }

        table {
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        }

        button i {
        font-size: 20px;
        }
        button {
        background: none;
        border: none;
        cursor: pointer;
        }
        .header-background {
        background-image: url('https://mangohub.app/mangobackground.png');
        background-size: auto;
        background-repeat: repeat -x;
        background-position: center -50px;
        text-align: center;
        padding: 60px 0;
        color: black;
        }
        .header-background h1, .header-background p {
        margin: 0;
        padding: 0;
        }       

        @media only screen and (max-width: 1000px) {
        /* Phone-specific styles here */
        body {
        font-size: 100%;
        }
        table {
        font-size: 110%;
        }

        </style>
        </head>
        """

navigator = """
<hr>
<style>
  .nav-link {
    text-decoration: none;
    font-weight: normal;
    color: black;
  }

  .nav-link:hover {
    font-weight: bold;
  }

  .active {
    font-weight: bold;
    color: black;
    text-decoration: none;
  }

  .nav-container {
    text-align: center;
  }
</style>

<div class="nav-container">
  <p>
    <a href="index.html" class="active">Home</a> |
    <a href="about.html" class="nav-link">About</a> |
    <a href="blog.html" class="nav-link">Blog</a>
  </p>
</div>
<hr>
"""
print("Content-type:text/html")
print(style)
print("  <body>")
print('''
<div class="header-background">
  <h1>mangohub</h1>
  <p>Find Jobs for Highschool Teens</p>
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
print('''
<div style="text-align: center; margin-top: 20px;">
  <label for="citySearch">Search City: </label>
  <input
    list="cities"
    id="citySearch"
    oninput="handleInput()"
    placeholder="Start typing..."
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
''')
for city, count in cityStateCounts:
    print(f"<option value='{city} ({count})'></option>")
print('</datalist>')
print('</div>')


#java script
print('''
<script>
  // Dynamically injected valid city list from Python
  const knownCities = [
''')
for i in cityState:
    print(f'    "{i[0]}",')
print('''
  ];

  const params = new URLSearchParams(window.location.search);
  let city = params.get("cityState");

  // If cityState is invalid, clean the URL
  if (city && !knownCities.includes(city)) {
    params.delete("cityState");
    params.delete("lat");
    params.delete("long");
    const newUrl = window.location.pathname + (params.toString() ? "?" + params.toString() : "");
    window.history.replaceState({}, "", newUrl);
  }
</script>
''')

# JavaScript
print('''
<script>
function goToCity() {
  let city = document.getElementById("citySearch").value;
  const validCities = Array.from(document.querySelectorAll("#cities option")).map(opt => opt.value);
  const dbg = window.location.href.includes("dbg=1") ? "&dbg=1" : "";
  if (validCities.includes(city)) {
      city = city.split(" (")[0].trim();
    window.location.href = "https://mangohub.app/?cityState=" + encodeURIComponent(city) + dbg;
  } else {
    alert("Please select a valid city from the list.");
  }
}

function useCurrentLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      const lat = position.coords.latitude;
      const long = position.coords.longitude;
      const dbg = window.location.href.includes("dbg=1") ? "&dbg=1" : "";
      window.location.href = `https://mangohub.app/?cityState=current&lat=${lat}&long=${long}${dbg}`;
    }, function(error) {
      alert("Geolocation failed: " + error.message);
    });
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

function handleKey(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    goToCity();
  }
}
function handleInput() {
  const input = document.getElementById("citySearch").value;
  const validCities = Array.from(document.querySelectorAll("#cities option")).map(opt => opt.value);
  if (validCities.includes(input)) {
    goToCity();
  }
}
</script>
''')

# PRINT TABLE
# JOBS TABLE
if not jobs and not dbg:
    print("<p style='text-align: center; margin-top: 20px;'>Please select a city to view jobs.</p>")
if jobs or dbg:
    print("    <table>")
    print("      <tr>")
    if dbg:
        print("        <th>Distance (mi)</th>")
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
            print("        <th>Distance (mi)</th>")
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
            for x in i:
                if x == i[0]:
                    print("<td style='text-align: center;'>" + str(x) + "</td>")
                else:
                    print("<td>" + str(x) + "</td>")
            print("      </tr>")
    else:
        if phone:
            for job in jobs:
                print("<tr>")
                print("<td>")
                print(job[1] + ", " +  str(job[2]) + "<br> ")
                print(job[6] + ", " + str(job[7]) + "<br>")
                print(job[0] + " mi, "  + str(job[4]) + "yo, " + str(job[5])  +  " " + job[10])
                print("</td>")
                print("</tr>")
        else:
            for i in jobs:
                print("      <tr>")
                for idx, value in enumerate(i):
                    if columns[idx] not in exclude:
                        if value == i[0]:
                            print("<td style='text-align: center;'>" + str(value) + "</td>")
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

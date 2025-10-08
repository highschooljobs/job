#!/usr/bin/env python3
import os.path
import sqlite3
import requests
import json
import os
from urllib.parse import parse_qs
from common import *

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

# Replace the existing JavaScript section with this updated version:

print('''
<script>
  // Dynamically injected valid city list from Python
  const cityData = [
''')
for city in cities:
    count = nJobsInCity[city]
    print(f'    {{name: "{city}", display: "{city} ({count})"}},')
print('''
  ];

  const params = new URLSearchParams(window.location.search);
  let city = params.get("cityState");
  const validCityNames = cityData.map(c => c.name);

  // If cityState is invalid, clean the URL
  if (city && !validCityNames.includes(city)) {
    params.delete("cityState");
    params.delete("lat");
    params.delete("long");
    const newUrl = window.location.pathname + (params.toString() ? "?" + params.toString() : "");
    window.history.replaceState({}, "", newUrl);
  }

  function updateDropdown(inputValue) {
    const datalist = document.getElementById("cities");
    datalist.innerHTML = ""; // Clear existing options
    
    const searchTerm = inputValue.trim().toLowerCase();
    
    if (searchTerm === "") {
      // If input is empty, show all cities
      cityData.forEach(city => {
        const option = document.createElement("option");
        option.value = city.display;
        datalist.appendChild(option);
      });
    } else {
      // Filter cities that start with the input value (case insensitive)
      const filtered = cityData.filter(city => 
        city.name.toLowerCase().startsWith(searchTerm)
      );
      
      filtered.forEach(city => {
        const option = document.createElement("option");
        option.value = city.display;
        datalist.appendChild(option);
      });
      
      // Debug: log if no results found
      if (filtered.length === 0) {
        console.log("No cities found starting with:", inputValue);
        console.log("Available cities:", cityData.map(c => c.name));
      }
    }
  }

  function goToCity() {
    let city = document.getElementById("citySearch").value.trim();
    const dbg = window.location.href.includes("dbg=1") ? "&dbg=1" : "";

    if (city === "") {
      // If input is empty, go back to main page
      window.location.href = "https://mangohub.app/";
      return;
    }

    // Extract city name from "CityName (count)" format if present
    const cityName = city.includes(" (") ? city.split(" (")[0].trim() : city;
    
    // Check if the city name is valid
    if (validCityNames.includes(cityName)) {
      window.location.href = "https://mangohub.app/?cityState=" + encodeURIComponent(cityName) + dbg;
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
    const inputValue = document.getElementById("citySearch").value;
    
    // Debug logging
    console.log("Input value:", inputValue);
    console.log("Searching for cities starting with:", inputValue.toLowerCase());
    
    updateDropdown(inputValue);
    
    // Auto-navigate if exact match is found
    const exactMatch = cityData.find(city => city.display === inputValue);
    if (exactMatch) {
      goToCity();
    }
  }

  // Initialize dropdown when page loads
  document.addEventListener("DOMContentLoaded", function() {
    updateDropdown("");
  });
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
                elif idx == 5 and x == 0.0:
                    print("<td style='text-align: center;'> - </td>")
                elif idx == 5 and x != 0.0:
                    print("<td style='text-align: center;'>$" + str(x) + "</td>")
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
                print(job[0] + " mi, "  + str(job[4]) + "yo, $" + str(job[5])  +  " " + job[10])
                print("</td>")
                print("</tr>")
        else:
            for i in jobs:
                print("      <tr>")
                for idx, value in enumerate(i):
                    if columns[idx] not in exclude:
                        if value == i[0]:
                            print("<td style='text-align: center;'>" + str(value) + " mi</td>")
                        elif idx == 5 and value == 0.0:
                            print("<td style='text-align: center;'> - </td>")
                        elif idx == 5 and not value == 0.0:
                            formatted = f"{value:.2f}"
                            print("<td style='text-align: center;'>$" + str(formatted) + " </td>")
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

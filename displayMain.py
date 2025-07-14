#!/usr/bin/env python3
import os.path
import sqlite3
import cgi
from common import *

arguments = cgi.FieldStorage()
citySelected = "cityState" in arguments
city = arguments["cityState"].value if citySelected else ""

# Check if user is on a phone
phone = "Phone" in os.environ["HTTP_USER_AGENT"]

dbg_mode = "dbg" in arguments
dbg = True if dbg_mode and arguments["dbg"].value == '1' else False

jobpath = "/var/lib/db/jobs.db"

if not os.path.exists(jobpath):
    print("Error: jobs.db not found!")
    exit()

# Connect to the database
conn = sqlite3.connect(jobpath)
cursor = conn.cursor()

cursor.execute('SELECT cityState, latitude, longitude FROM cityState')
cityState = cursor.fetchall()
cityState.sort(key=lambda x: x[0])
cityState.sort()

lat = long = None
if citySelected:
    if city == "current" and "lat" in arguments and "long" in arguments:
        lat = float(arguments["lat"].value)
        long = float(arguments["long"].value)
    else:
        cursor.execute('SELECT latitude, longitude FROM cityState WHERE cityState = ?', (city,))
        latLong = cursor.fetchall()
        lat = float(latLong[0][0])
        long = float(latLong[0][1])

    minLong = long - 0.1
    maxLong = long + 0.1
    minLat = lat - 0.1
    maxLat = lat + 0.1

# Execute SELECT statement
inBox = '" OR (latitude > ' + str(minLat) + ' AND latitude < ' + str(maxLat) + ' AND longitude > ' + str(minLong) + ' AND longitude < ' + str(maxLong) + '))' if citySelected and lat is not None else ""
addcity = ' AND (cityState = "' + city + inBox if citySelected and lat is not None else ""
if citySelected or dbg:
    select = 'SELECT company, title, id, age, pay, address, cityState, latitude, longitude, url FROM jobs WHERE age = 16' + addcity
    cursor.execute(select)
    jobsRaw = cursor.fetchall()
else:
    jobsRaw = []

jobs = []
for row in jobsRaw:
    job = []
    distance = calcDistance(lat, long, row[7], row[8]) if citySelected and lat is not None else 0
    for x in row:
        job.append(x)
    job.insert(0, str(round(distance, 1)))
    jobs.append(job)
jobs.sort(key=lambda x: float(x[0]))

columns = ["distance", "company", "title", "id", "age", "pay", "address", "cityState", "latitude", "longitude", "url"]
exclude = ["id", "longitude", "latitude"]

conn.close()

# Mobile vs Desktop style
if phone:
    style = """
    <head>
    <style>
    table {
    border-collapse: collapse;
    width: 100%;
    font-family: Arial, sans-serif;
    margin-top: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    border: 1px solid #ddd;
    }
    body {
     font-family: arial, sans-serif;
     font-size: 200%;
    }
    select, input {
     font-family: arial, sans-serif;
     font-size: 110%;
    }
    th {
    background-color: #f9fafb;
    color: #333;
    font-weight: 600;
    padding: 12px 15px;
    border: 1px solid #ddd;
    text-align: left;
    font-size: 16px;
    }

    td {
    padding: 10px 15px;
    border: 1px solid #eee;
    font-size: 15px;
    }

    tr:nth-child(even) {
    background-color: #f7f7f7;
    }   

    tr:hover {
    background-color: #eef2f7;
    transition: background-color 0.2s ease-in-out;
    }
    </style>
    </head>
    """
else:
    style = """
    <head>
    <style>
    table {
    border-collapse: collapse;
    width: 100%;
    font-family: Arial, sans-serif;
    margin-top: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    border: 1px solid #ddd;
    }
    body {
     font-family: arial, sans-serif;
    }
    select, input {
     font-family: arial, sans-serif;
     font-size: 110%;
    }
    th {
    background-color: #f9fafb;
    color: #333;
    font-weight: 600;
    padding: 12px 15px;
    border: 1px solid #ddd;
    text-align: left;
    font-size: 16px;
    }

    td {
    padding: 10px 15px;
    border: 1px solid #eee;
    font-size: 15px;
    }   

    tr:nth-child(even) {
    background-color: #f7f7f7;
    }

    tr:hover {
    background-color: #eef2f7;
    transition: background-color 0.2s ease-in-out;
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
    <a href="about.html" class="nav-link">About</a>
  </p>
</div>
<hr>
"""

print("Content-type:text/html\n")
print(style)
print("<body>")
print('<h1 style="text-align: center;">mangohub</h1>')
print('<p style="text-align: center;">Find jobs for highschool teens</p>')
print(navigator)

if dbg:
    print("City Selected: " + str(citySelected) + "<br>")
    print("City: '" + city + "'<br>")
    for i in arguments.keys():
        print(i + " '" + arguments[i].value + "'<br>")

# Search bar and buttons
print('<div style="text-align: center; margin-top: 20px;">')
print('<label for="citySearch">Search City: </label>')
print('<input list="cities" id="citySearch" placeholder="Start typing..." />')
print('<button onclick="goToCity()">Go</button>')
print('<button onclick="useCurrentLocation()">Use Current Location</button>')
print('<datalist id="cities">')
for i in cityState:
    if dbg or "CA" in i[0]:
        print(f"<option value='{i[0]}'>")
print('</datalist>')
print('</div>')

# JavaScript for geolocation + search
print("""
<script>
function goToCity() {
    const city = document.getElementById("citySearch").value;
    const validCities = Array.from(document.querySelectorAll("#cities option")).map(opt => opt.value);
    const dbg = window.location.href.includes("dbg=1") ? "&dbg=1" : "";
    if (validCities.includes(city)) {
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
</script>
""")

# JOBS TABLE
if not jobs and not dbg:
    print("<p style='text-align: center; margin-top: 20px;'>Please select a city to view jobs.</p>")
if jobs or dbg:
    print("    <table>")
    print("      <tr>")  # <-- Fixed: closing angle bracket added
    for col in columns:
        if col not in exclude:
            print(f"        <th>{col.capitalize()}</th>")
    print("      </tr>")

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
    print("<font size=+1>Environment</font><br>")
    for param in os.environ.keys():
        print("<b>%20s</b>: %s<br>" % (param, os.environ[param]))
    print(lat, long, "<br>")
    print(select, "<br>")

print("</body>")


#!/usr/bin/env python3
import os.path
import sqlite3
import cgi
from common import *

arguments = cgi.FieldStorage()
citySelected = "cityState" in arguments
city = arguments["cityState"].value if citySelected else ""

#check if user is on a phone
phone = "Phone" in os.environ["HTTP_USER_AGENT"]

dbg_mode = "dbg" in arguments
dbg = True if dbg_mode and arguments["dbg"].value  == '1' else False

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
jobs.sort(key=lambda x : float(x[0]))

columns = ["distance", "company", "title", "id", "age", "pay", "address", "cityState", "latitude", "longitude", "url"]
exclude = ["id", "longitude", "latitude"]

conn.close()


# change the style if your on mobile view vs computer
if phone:
    style = """
    <head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    table {
     margin-top: 20px;
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    font-size: 140%;
    }

    body{
    font-family: arial, sans-serif;
    font-size: 200%;
    }

    select, input{
    font-family: arial, sans-serif;
    font-size: 110%;
    }

    td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 18px;
    }

    td:nth-child(2) {
    max-width: 300px;
    word-wrap: break-word;
    }

    tr:nth-child(even) {
    background-color: #dddddd;
    }
    button i {
    font-size: 20px;
    }
    button {
    background: none;
    border: none;
    cursor: pointer;
    }
    </style>
    </head>
    """
else:
     style = """
        <head>
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
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }

        td:nth-child(2) {
        max-width: 300px;
        word-wrap: break-word;
        }

        tr:nth-child(even) {
        background-color: #dddddd;
        }
        tr:hover {
        background-color: #eef2f7;
        transition: background-color 0.2s ease-in-out;
        }
        button i {
        font-size: 20px;
        }
        button {
        background: none;
        border: none;
        cursor: pointer;
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
print("Content-type:text/html")
print(style)
print("  <body>")
print('    <h1 style="text-align: center;">mangohub</h1>')
print('    <p style="text-align: center;">Find jobs for highschool teens</p>')
print(navigator)
if dbg:
    print("City Selected: " + str(citySelected) +  "</br>")
    print("City: '" + city + "'</br>")
    for i in arguments.keys():
        print(i + " '" +  arguments[i].value + "'</br>")


# Search bar with Enter key support
print('''
<div style="text-align: center; margin-top: 20px;">
  <label for="citySearch">Search City: </label>
  <input
    list="cities"
    id="citySearch"
    placeholder="Start typing..."
    onkeydown="handleKey(event)"
  />
  <button onclick="useCurrentLocation()" title="Use Current Location"><i class="fas fa-location-crosshairs"></i></button>
  <datalist id="cities">
''')

for i in cityState:
    if dbg or "CA" in i[0]:
        print(f"<option value='{i[0]}'>")
print('</datalist>')
print('</div>')

# JavaScript
print('''
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

function handleKey(event) {
  if (event.key === "Enter") {
    event.preventDefault();
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
                print(job[1] + ", " +  job[2] + "<br> ")
                print(job[6] + ", " + str(job[7]) + "<br>")
                print(job[0] + " mi, "  + job[4] + "yo, " + job[5]  +  " " + job[10])
                print("<td>")
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

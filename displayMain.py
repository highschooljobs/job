#!/usr/bin/env python3
import os.path
import sqlite3
import cgi
from common import *

arguments = cgi.FieldStorage()
citySelected = "cityState" in arguments
city = arguments["cityState"].value if citySelected else ""


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

if citySelected:
    cursor.execute('SELECT latitude, longitude FROM cityState WHERE cityState = "' + city + '"')
    latLong = cursor.fetchall()
    lat = float(latLong[0][0])
    long = float(latLong[0][1])
    minLong = long - 0.1
    maxLong = long + 0.1
    minLat = lat - 0.1
    maxLat = lat + 0.1

# Execute SELECT statement
inBox = '" OR (latitude > ' + str(minLat) + ' AND latitude < ' + str(maxLat) + ' AND longitude > ' + str(minLong) + ' AND longitude < '  + str(maxLong) +  '))' if citySelected else ""
addcity = ' AND (cityState = "' + city + inBox if citySelected else ""
select = 'SELECT company, title, id, age, pay, address, cityState, latitude, longitude, url FROM jobs WHERE age = 16' + addcity
cursor.execute(select)
jobsRaw = cursor.fetchall()

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

style = """
<head>
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

select{
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
</style>
</head>
"""


navigator = """
<hr>
<p>
<b>
<font color="gray">Home</font>
 | 
<a href="about.html">About</a>
</b>
</font>
</p>
<hr>
"""

print("Content-type:text/html")
print(style)
print("  <body>")
print("    <h1>JobNest</h1>")
print("    Find jobs for highschool teens")
print(navigator)
if dbg:
    print("City Selected: " + str(citySelected) +  "</br>")
    print("City: '" + city + "'</br>")
    for i in arguments.keys():
        print(i + " '" +  arguments[i].value + "'</br>")


# DROPDOWN MENU
print('City: ')
if dbg:
    print('<select onchange = "location = this.options[this.selectedIndex].value + \'&dbg=1\';">')
else:
    print('<select onchange = "location = this.options[this.selectedIndex].value;">')
print("<option value='http://52.53.194.209/?'>ALL</option>")
for i in cityState:
    if dbg or "CA" in i[0]:
        selectstr = " selected" if citySelected and i[0] == city else ""
        latlong = " None" if i[1] is None or i[2] is None else " " +  str(i[1]) + " " + str(i[2])
        geodata = latlong if dbg else ""
        print("<option value='http://52.53.194.209/?cityState=" + i[0]  + "'" + selectstr + ">" + i[0] + geodata  + "</option>")
print("</select>")


# PRINT TABLE
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
    print(lat, long, "<br>")
    print(select, "<br>")
    print(jobs)
print("  </body>")

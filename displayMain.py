#!/usr/bin/env python3
import os.path
import sqlite3
import cgi

arguments = cgi.FieldStorage()
citySelected = "cityState" in arguments
city = arguments["cityState"].value if citySelected else ""

jobpath = "/var/lib/db/jobs.db"

if not os.path.exists(jobpath):
    print("Error: jobs.db not found!")
    exit()

# Connect to the database
conn = sqlite3.connect(jobpath)
cursor = conn.cursor()

cursor.execute('SELECT cityState FROM cityState')
cityState = cursor.fetchall()
cityState.sort()

# Execute SELECT statement
addcity = ' AND cityState = "' + city + '"' if citySelected else ""
cursor.execute('SELECT company, title, id, age, pay, cityState, longitude, latitude, url FROM jobs WHERE age = 16' + addcity)
jobs = cursor.fetchall()


conn.close()

style = """
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
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
<font size="5">
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
print("    <h1>Jobs</h1>")
print(navigator)
print("City Selected: " + str(citySelected) +  "</br>")
print("City: '" + city + "'</br>")
for i in arguments.keys():
    print(i + " '" +  arguments[i].value + "'</br>")
print('<select onchange = "location = this.options[this.selectedIndex].value;">')
print("<option value='http://52.53.194.209'>ALL</option>")
for i in cityState:
    selectstr = " selected" if citySelected and i[0] == city else ""
    print("<option value='http://52.53.194.209/?cityState=" + i[0]  + "'" + selectstr + ">" + i[0] + "</option>")
print("</select>")
print("    <table>")
print("      <tr>")
print("        <th>Company</th>")
print("        <th>Title</th>")
print("        <th>Id</th>")
print("        <th>Age</th>")
print("        <th>Pay</th>")
print("        <th>cityState</th>")
print("        <th>Longitude</th>")
print("        <th>Latitude</th>")
print("        <th>url</th>")


print("      </tr>")

for i in jobs:
    print("      <tr>")
    for x in i:
        print("<td>" + x + "</td>")
    print("      </tr>")
print("    </table>")
print("Total jobs: ", len(jobs))
print("  </body>")

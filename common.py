from geopy.geocoders import GoogleV3
import geopy.distance
import sqlite3
from datetime import datetime
GM_API_KEY = 'AIzaSyBejZVTH21hRQdHODK8PkcQ6jng5SlWpxs'
geolocator = GoogleV3(api_key=GM_API_KEY)


dbpath = "/var/lib/db/jobs.db"
cityTable = "cityStates"
jobTable = "jobs"
def get_state_abbreviation(state_name):
    states = {
        "alabama": "AL",
        "alaska": "AK",
        "arizona": "AZ",
        "arkansas": "AR",
        "california": "CA",
        "colorado": "CO",
        "connecticut": "CT",
        "delaware": "DE",
        "district of columbia": "DC",
        "florida": "FL",
        "georgia": "GA",
        "hawaii": "HI",
        "idaho": "ID",
        "illinois": "IL",
        "indiana": "IN",
        "iowa": "IA",
        "kansas": "KS",
        "kentucky": "KY",
        "louisiana": "LA",
        "maine": "ME",
        "maryland": "MD",
        "massachusetts": "MA",
        "michigan": "MI",
        "minnesota": "MN",
        "mississippi": "MS",
        "missouri": "MO",
        "montana": "MT",
        "nebraska": "NE",
        "nevada": "NV",
        "new hampshire": "NH",
        "new jersey": "NJ",
        "new mexico": "NM",
        "new york": "NY",
        "north carolina": "NC",
        "north dakota": "ND",
        "ohio": "OH",
        "oklahoma": "OK",
        "oregon": "OR",
        "pennsylvania": "PA",
        "rhode island": "RI",
        "south carolina": "SC",
        "south dakota": "SD",
        "tennessee": "TN",
        "texas": "TX",
        "utah": "UT",
        "vermont": "VT",
        "virginia": "VA",
        "washington": "WA",
        "west virginia": "WV",
        "wisconsin": "WI",
        "wyoming": "WY"
    }
    
    cleaned_name = state_name.strip().lower()
    return states.get(cleaned_name, "Invalid state name")

def parseTerm(s, keyStart, keyEnd, lastIndex):
    pos = s.find(keyStart, lastIndex)
    start = pos + len(keyStart)
    end = s.find(keyEnd, start)

    term = s[start:end].strip()

    return term

def existsCityState(cityState, cursor):
    command1 = 'SELECT EXISTS(SELECT 1 FROM %s WHERE cityState=" %s ")' % (cityTable, cityState)
    cursor.execute(command1)
    result = cursor.fetchone()

    return result[0]

def existsId(jobId, cursor):
    command1 = 'SELECT EXISTS(SELECT 1 FROM jobs WHERE id="' + str(jobId) + '")'
    cursor.execute(command1)
    result = cursor.fetchone()

    return result[0]

def getLatLong(address):
    location = geolocator.geocode(address)
    if location is None:
        raise ValueError("Bad address")
    return (location.latitude, location.longitude)

def calcDistance(cityLat, cityLong, jobLat, jobLong):
    city = (cityLat, cityLong)
    job = (jobLat, jobLong)
    return (geopy.distance.geodesic(city, job).miles)

def updateSQL(dictionary, cursor, company):
    command = """
    INSERT INTO jobs (
        company, title, id, age, pay, address, cityState, longitude, latitude, url, postdate, lastverify, count
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    if "latitude" not in dictionary:
        address = dictionary.get('address')    
        cityState = dictionary.get("cityState")
        print(address)
        print(cityState)
        cursor.execute("SELECT latitude, longitude FROM jobs WHERE address = ? AND cityState = ?",(address, cityState))
        result = cursor.fetchone()
        if result:
            latitude, longitude = result
            print("saved a token")
        else:
            latitude, longitude = getLatLong(address + cityState)
            print("using a token")
    else:
        latitude = dictionary.get("latitude")
        longitude = dictionary.get("longitude")
    values = (
        company,
        dictionary.get("title"),
        dictionary.get("id"),
        dictionary.get("age"),
        dictionary.get("pay"),
        dictionary.get("address"),
        dictionary.get("cityState"),
        longitude,
        latitude,
        f'<a href="{dictionary["url"]}" target="_blank"> Apply</a>',
        dictionary.get("postdate"),
        datetime.today().strftime("%Y-%m-%d"),
        0
    )

    cursor.execute(command, values)

    cityState = dictionary.get("cityState")
    id = dictionary.get("id")
    print("Job ", id, " added", dictionary.get('url'))
    if isValidAge(dictionary.get('age')):
        if not existsCityState(cityState, cursor):
            if len(cityState) < 4:
                print("job " + str(id) + " skipped because has invalid cityState " + cityState)
                return
            try:
                citylat, citylong = getLatLong(cityState)
            except:
                return
            command1 = f"INSERT INTO {cityTable} (cityState, latitude, longitude) VALUES (?, ?, ?)"
            cursor.execute(command1, (cityState, citylat, citylong))
        else:
            command2 = f"""
            UPDATE {cityTable}
            SET job_count = job_count + 1
            WHERE cityState = ?
            """
            cursor.execute(command2, (cityState,))


def isValidAge(age):
    return age < 18 and age > 0


def openInitDb():
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    command1 = "CREATE TABLE IF NOT EXISTS %s (company TEXT, title TEXT, id TEXT, age TEXT, pay TEXT, address TEXT, cityState TEXT, longitude FLOAT, latitude FLOAT, url TEXT)" % (jobTable)
    cursor.execute(command1)

    command2 = "CREATE TABLE IF NOT EXISTS %s (cityState TEXT, latitude FLOAT, longitude FLOAT)" % (cityTable)
    cursor.execute(command2)
    return connection
def isTooSenior(title):
    seniors = ['Director', 'Manager', 'in Charge', 'Specialty', 'Meat']
    for i in seniors:
        if i in title:
            return True
    return False

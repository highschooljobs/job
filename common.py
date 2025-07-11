from geopy.geocoders import GoogleV3
import geopy.distance
GM_API_KEY = 'AIzaSyBejZVTH21hRQdHODK8PkcQ6jng5SlWpxs'
geolocator = GoogleV3(api_key=GM_API_KEY)



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
    command1 = 'SELECT EXISTS(SELECT 1 FROM cityState WHERE cityState="' + str(cityState) + '")'
    cursor.execute(command1)
    result = cursor.fetchone()

    return result[0]

def existsId(jobId, cursor):
    command1 = 'SELECT EXISTS(SELECT 1 FROM jobs WHERE id="' + str(jobId) + '")'
    cursor.execute(command1)
    result = cursor.fetchone()

    return result[0]

def getLatLong(address):
    print(address)
    location = geolocator.geocode(address)
    
    return (location.latitude, location.longitude)

def calcDistance(cityLat, cityLong, jobLat, jobLong):
    city = (cityLat, cityLong)
    job = (jobLat, jobLong)
    return (geopy.distance.geodesic(city, job).miles)

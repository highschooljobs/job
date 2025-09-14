#!/usr/bin/env python3
import sqlite3
import re
from datetime import datetime
from common import *

# Connect to source and destination databases
db = sqlite3.connect("/var/lib/db/jobs.db")

cursor = db.cursor()

cursor.execute("DROP TABLE cityStates")
# Create cityStates table before inserting
cursor.execute("""
CREATE TABLE cityStates (
    cityState TEXT,
    Latitude FLOAT,
    Longitude FLOAT,
    job_count INTEGER
)
""")

# fetch all unique cityState values
cursor.execute("SELECT DISTINCT cityState FROM jobs;")
rows = cursor.fetchall()

# store them in a list
city_states = [row[0] for row in rows]

for cityState in city_states:
    cityState = cityState.strip()
    try:
        latitude, longitude = getLatLong(cityState)
        cursor.execute(
            "INSERT INTO cityStates (cityState, latitude, longitude) VALUES (?, ?, ?)",
            (cityState, latitude, longitude)
        )
    except Exception as e:
        print(f"Skipping '{cityState}' due to error: {e}")

# Count jobs per cityState and update job_count
cursor.execute("SELECT cityState, COUNT(*) FROM jobs WHERE age < 18 AND age > 0 GROUP BY cityState")
counts = cursor.fetchall()

for citystate, count in counts:
    cursor.execute("UPDATE cityStates SET job_count = ? WHERE cityState = ?", (count, citystate))

# Finalize
db.commit()
db.close()

print("Data changed successfully.")

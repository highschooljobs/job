#!/usr/bin/env python3
import sqlite3
import requests
import html
import json
import time
from datetime import date, datetime
import sys
import signal
from common import *

#-------------------Functions-----------------------------

def deleteJob(cursor, job):
    cursor.execute(
        "UPDATE cityStates SET job_count = job_count - 1 WHERE cityState = ?",
        (job["cityState"],)
    )
    print(job["company"])
    print(job["title"])
    print(job["cityState"])
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job["id"],))
    print("-"*50)

def signal_handler(sig, frame):
    print(" exiting gracefully")
    conn.commit()
    conn.close()
    sys.exit(0)

#----------------------Variables-----------------------------

#list of albertsons companies
albertcompany = ['Albertsons', "Safeway", "Vons", "Andronico's", "Albertsons Companies", "Pavilions"]

# todays date
today = date.today().strftime("%Y-%m-%d")
rows_deleted = 0



# Connect to the database
conn = sqlite3.connect("/var/lib/db/jobs.db")
conn.row_factory = sqlite3.Row  # Enable named columns
cursor = conn.cursor()


#signal detector
signal.signal(signal.SIGINT, signal_handler)


# Get list of URLs older than 2 days
cursor.execute("SELECT * FROM jobs WHERE DATE(lastverify) < DATE('now', '-2 days');")
joblist = cursor.fetchall()

print("Running at: ", datetime.now())

# count jobs before
cursor.execute("SELECT count(1) FROM jobs;")
jobCount = cursor.fetchone()[0]
print("Jobs Before: ", jobCount)


print("Checking " + str(len(joblist)) + " jobs")

for job in joblist:
    if existsJob(job) == False:
        deleteJob(cursor, job)
        rows_deleted += 1
        continue
    cursor.execute("UPDATE jobs SET lastverify = ? WHERE id = ?", (today, job["id"]))

# Commit and close
conn.commit()
conn.close()

print("Rows deleted: ", rows_deleted)
print("Job cleanup complete.")

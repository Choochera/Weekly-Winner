import datetime
import requests
import csv

def weeklyOptions():
    updateCSV()
    results = []
    flag = False
    with open('weeklysmf.csv') as File:
        reader = csv.DictReader(File)
        for row in reader:
            if flag:
                results.append(row["List of Available Weekly Options"])
            if row['List of Available Weekly Options'] == "Available Weeklys - Equity":
                flag = True
    return results

def updateCSV():
    url = "https://www.cboe.com/available_weeklys/get_csv_download/"
    r = requests.get(url, allow_redirects = True)
    open("weeklysmf.csv", 'wb').write(r.content)

#Function that returns date of next Friday
def nextFriday():
    day = datetime.datetime.today()
    if day.strftime('%A') == "Friday":
        day = day + datetime.timedelta(days = 1)
    while day.weekday() != 4:
        day = day + datetime.timedelta(days = 1)
    return str(day).split(" ")[0]
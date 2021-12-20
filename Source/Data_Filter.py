import datetime
import requests
import csv

#Returns list of stocks offering weekly options reads them into results
def weeklyOptions():
    updateCSV()
    results = []
    flag = False
    with open('../Data/weeklysmf.csv') as File:
        reader = csv.DictReader(File)
        try:
            for row in reader:
                if flag:
                    results.append(row["List of Available Weekly Options"])
                if row['List of Available Weekly Options'] == "Available Weeklys - Equity":
                    flag = True
        except KeyError:
            print("Error retrieving weekly's data - weeklyOptions")
    return results

#Retrieves list of stocks offering weekly options 
def updateCSV():
    url = "https://www.cboe.com/available_weeklys/get_csv_download/"
    r = requests.get(url, allow_redirects = True)
    open("../Data/weeklysmf.csv", 'wb').write(r.content)

def updateHolidays():
    url = "https://www.cboe.com/us/equities/holidays/csv/"
    r = requests.get(url, allow_redirects = True)
    open("../Data/holidays.csv", 'wb').write(r.content)

#Function that returns date of next Friday
def nextFriday():
    updateHolidays()
    with open('../Data/holidays.csv') as File:
        holiday_dates = []
        reader = csv.DictReader(File)
        try:
            for row in reader:
                try:
                    holiday_dates.append(row[None][0])
                except:
                    pass
        except KeyError as err:
            print("Error retrieving holiday data")
    day = datetime.datetime.today()
    if day.strftime('%A') == "Friday":
        day = day + datetime.timedelta(days = 1)
    while day.weekday() != 4:
        day = day + datetime.timedelta(days = 1)
    if (str(day).split(" ")[0]) in holiday_dates:
        day = day - datetime.timedelta(days = 1)
    return str(day).split(" ")[0]

#Checks if idle an instance of idle is already running the background
def isIdleOpen():
    import subprocess
    subprocess = subprocess.Popen("wmic process get description, executablepath", shell = True, stdout = subprocess.PIPE)
    subprocess = subprocess.stdout.read()
    subprocess = subprocess.decode("utf-8")
    return "pythonw.exe" not in subprocess
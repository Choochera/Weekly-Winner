from os import close
import robin_stocks.robinhood as rh
import datetime
from calendar import monthrange

#Function that returns date of next Friday
def nextFriday():
    day = datetime.datetime.today().weekday()
    offset = day - 1
    if(day < 4):
        offset = 4 - day
    day = datetime.datetime.today()
    daysInTheMonth = monthrange(day.year, day.month)[1]
    whatDay = day.day
    whatMonth = day.month
    whatYear = day.year
    if whatDay + offset > daysInTheMonth:
        whatMonth += 1
        whatDay = monthrange(whatYear, whatMonth + 1)[1] - whatDay
        if whatMonth == 13:
            whatMonth = 1
            whatYear += 1
   
    day = ("%02d-%02d-%02d" % (whatYear, whatMonth, whatDay))
    return day

#Returns list of symbols that offer weekly options
def weeklyOptions(validateFlag):

    Friday = nextFriday()
    with open("Available_Weeklys.txt", 'r') as file:
        lines = file.read()
        lines = lines.split("\n")
        close

    symbols = []
    for pair in lines:
        symbol = pair.split("\t")[0]
        if validateFlag and not isinstance(rh.find_options_by_expiration(symbol, Friday, "put"), type(None)):
            symbols.append(symbol)
        if not validateFlag:
            symbols.append(symbol)
    return symbols
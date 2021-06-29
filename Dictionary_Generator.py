import robin_stocks.robinhood as rh
import os
import json
import threading
from Data_Filter import weeklyOptions, nextFriday
import time

#Dictionaries of options and their premiums key = stock ticker, value = name/tstrike/tmark
callDictionary = dict()
putDictionary = dict()

#Aqcuiring environmental variables stored in OS
robin_user = os.environ.get("robinhood_username")
robin_pass = os.environ.get("robinhood_password")

#Log in to Robinhood
rh.login(
    username = robin_user,           #Username
    password = robin_pass,           #Password
    expiresIn = 86400,               #Time until login expiration
    by_sms = True,                   #Text or Email message validation code   
)

#List of tickers with weekly options/date of next weekly options expiration/balance of portfolio
weeklyOptions = weeklyOptions(False)
Friday = nextFriday()
skipped_stocks = []

#returns closest strike price above the current price of a ticker
def closestCallStrike(ticker):
    try:
        minimum = 0
        currentPrice = rh.get_latest_price(ticker, None, True)[0]
        closestStrike = float(round(float(currentPrice), 0))
        for i in range(20):
            try:
                if float(closestStrike) >= float(currentPrice):
                    minimum = rh.find_options_by_expiration_and_strike(ticker, nextFriday(), closestStrike, "call", "strike_price")[0]
                    break
                else: closestStrike += 0.5
            except IndexError:
                closestStrike += 0.5
    except AttributeError:
        skipped_stocks.append(ticker)
    return minimum

#return closest strike price below the current price of a ticker
def closestPutStrike(ticker):
    try:
        maximum = 0
        currentPrice = rh.get_latest_price(ticker, None, True)[0]
        closestStrike = float(round(float(currentPrice), 0))
        for i in range(20):
            try:
                if float(closestStrike) <= float(currentPrice):
                    maximum = rh.find_options_by_expiration_and_strike(ticker, nextFriday(), closestStrike, "put", "strike_price")[0]
                    break
                else: closestStrike -= 0.5
            except IndexError:
                closestStrike -= 0.5
    except AttributeError:
        skipped_stocks.append(ticker)
    return maximum

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

progress = 0

#Return dictionary containing all strike prices for weekly option depending on type

#callStrikes = strikeDictionary("call")
#putStrikes = strikeDictionary("put")

#creates dictionary for either calls or puts with keyword as 'ticker name' and values: strike date, strike price and mark price then saves it as an importable file
def dictionaryGenerator(threadID, stockList, optionType):
    Friday = nextFriday()
    increment = int(len(weeklyOptions)/32)
    global progress
    lowerBound = (threadID-1)*increment
    upperBound = threadID*increment
    for stock in stockList[lowerBound:upperBound]:
        if optionType == "call": strikePrice = closestCallStrike(stock)
        if optionType == "put": strikePrice = closestPutStrike(stock)
        try:
            try:
                stockData = rh.get_option_market_data(stock, Friday, strikePrice, optionType)[0][0]
                if(optionType == "call"):
                    callDictionary[str(stock)] = "%s\t%s\t%s\t%s" % (
                        str(stock),
                        strikePrice, 
                        stockData['adjusted_mark_price'],
                        stockData['delta'])
                if(optionType == "put"):
                    putDictionary[str(stock)] = "%s\t%s\t%s\t%s" % (
                        str(stock),
                        strikePrice, 
                        stockData['adjusted_mark_price'],
                        stockData['delta'])
            except TypeError:
                skipped_stocks.append(str(stock))
        except IndexError:
            skipped_stocks.append(str(stock))
        progress += 1
        printProgressBar(progress, len(weeklyOptions), prefix = optionType + ' Dictionary Progress:', suffix = 'Complete (' + str(progress) + "/" + str(len(weeklyOptions)) + ')', length = 50)
        #print("\nGenerating %s Dictionary: %.2f%%" % (optionType, progress/5.16), end = "\r")

#Class outlining behavior of threads
class myThread (threading.Thread):
   def __init__(self, threadID, name, counter, option):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.option = option
   def run(self):
      dictionaryGenerator(self.threadID, weeklyOptions, self.option)

#Calls Threads to update dictionaries
def updateDictionary(option):
    global progress

    progress = 0
    i = 0
    threads = []

    for i in range(32):
        threads.append(myThread(i + 1, "thread_" + str(i + 1), i+1, option))
        threads[i].start()
    start = time.time()
    
    for t in threads:
        t.join()
    end = time.time()
    print("Unable to process symbols: " + str(skipped_stocks))
    print(str(option) + " Dictionary Generation Complete\nElapsed time: %2d minutes, %2d seconds\n" % ((end - start)/60, (end - start)%60))

    if option == "call":
        output = open("callDictionary.json", "w")
        json.dump(callDictionary, output)
        output.close()

    if option == "put":
        output = open("putDictionary.json", "w")
        json.dump(putDictionary, output)
        output.close()
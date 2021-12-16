import robin_stocks.robinhood as rh
import json
import threading
from Data_Filter import weeklyOptions, nextFriday
import time
import getpass
import os

print("Weekly Winner by Matthew Gabriel\nVersion 0.3.2")

try:
    rh.login(
        username = os.environ.get("robinhood_username"),           #Username
        password = os.environ.get("robinhood_password"),           #Password
        expiresIn = 86400,               #Time until login expiration
        store_session = True,             #Save login authorization
        mfa_code = True
    )
except:
    os.system("export robinhood_username = " + input("Insert Robinhood Username: ") )    
    os.system("export robinhood_password = " + getpass.getpass(prompt = 'Password: ')  )        

#List of tickers with weekly options/date of next weekly options expiration/balance of portfolio
weeklyOptions = weeklyOptions()
weeklyOptions_flags = dict()
Friday = nextFriday()
skipped_stocks = []
dictionary = dict()
MAX_NUM_THREADS = 16

#Returns closest strike price to current price (lesser than if puts, greater than if calls)
def closestStrike(ticker, date, optionType):
    try:
        result = []
        currentPrice = rh.get_latest_price(ticker, None, True)[0]
        closestStrike = float(round(float(currentPrice), 0))
        for i in range(20):
            if optionType == "put":
                try:
                    if float(closestStrike) <= float(currentPrice):
                        result.append(rh.find_options_by_expiration_and_strike(ticker, date, closestStrike, "put", "strike_price")[0])
                        if len(result) == 3: break
                    closestStrike -= 0.5
                except IndexError or TypeError:
                    closestStrike -= 0.5
            elif optionType == "call":
                try:
                    if float(closestStrike) >= float(currentPrice):
                        result.append(rh.find_options_by_expiration_and_strike(ticker, date, closestStrike, "call", "strike_price")[0])
                        if len(result) == 3: break
                    closestStrike += 0.5
                except IndexError or TypeError:
                    closestStrike += 0.5
    except AttributeError or TypeError:
        if not str(ticker) in skipped_stocks: skipped_stocks.append(ticker)
    return result

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

#creates dictionary for either calls or puts with keyword as 'ticker name' and values: strike date, strike price and mark price then saves it as an importable file
def dictionaryGenerator(stockList, optionType, date):
    global progress, dictionary, weeklyOptions_flags
    for stock in stockList:
        if not str(stock) in weeklyOptions_flags:
            weeklyOptions_flags[str(stock)] = True
            stockData = dict()
            try:
                try:
                    strikePrice = closestStrike(stock, date, optionType)
                    for i in range(len(strikePrice)):
                        stockData = rh.get_option_market_data(str(stock), str(date), strikePrice[i], optionType)[0][0]
                        if stockData['delta'] != None:
                            if not (str(stock) in dictionary): dictionary[str(stock)] = []
                            dictionary[str(stock)].append([
                                    str(stock),
                                    strikePrice[i],
                                    stockData['adjusted_mark_price'],
                                    stockData['delta'],
                                    stockData['implied_volatility']])
                except TypeError:
                    None
            except IndexError or AttributeError:
                if not str(stock) in skipped_stocks: skipped_stocks.append(str(stock))
            progress += 1
            printProgressBar(progress, len(weeklyOptions), prefix = optionType + ' Dictionary Progress:', suffix = 'Complete (' + str(progress) + "/" + str(len(weeklyOptions)) + ')', length = 50)

def dictionaryValidator(optionType, date):
    global weeklyOptions, dictionary, weeklyOptions_flags
    for stock in weeklyOptions:
        if not str(stock) in dictionary:
            if not str(stock) in weeklyOptions_flags:
                weeklyOptions_flags[str(stock)] = True
                try:
                    try:
                        strikePrice = closestStrike(stock, date, optionType)
                        for i in range(len(strikePrice)):
                            stockData = rh.get_option_market_data(str(stock), str(date), strikePrice[i], optionType)[0][0]
                            if stockData['delta'] != None:
                                if not (str(stock) in dictionary): dictionary[str(stock)] = []
                                dictionary[str(stock)].append([
                                        str(stock),
                                        strikePrice[i],
                                        stockData['adjusted_mark_price'],
                                        stockData['delta'],
                                        stockData['implied_volatility']])
                    except TypeError:
                        None
                except IndexError or AttributeError:
                    None

#Class outlining behavior of threads
class generatorThread (threading.Thread):
   def __init__(self, threadID, name, counter, option, date):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.option = option
      self.date = date
   def run(self):
        dictionaryGenerator(weeklyOptions, self.option, self.date)

class validatorThread (threading.Thread):
   def __init__(self, threadID, name, counter, option, date):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.option = option
      self.date = date
   def run(self):
        dictionaryValidator(self.option, self.date)

#Calls Threads to update dictionaries
def updateDictionary(option, date):
    global progress, dictionary, skipped_stocks, weeklyOptions_flags
    
    dictionary = dict()
    weeklyOptions_flags = dict()
    skipped_stocks = []
    progress = 0
    i = 0
    threads = []
    start = time.time()

    for i in range(MAX_NUM_THREADS):
        threads.append(generatorThread(i + 1, "thread_" + str(i + 1), i+1, option, date))
        threads[i].start()
    for t in threads:
        t.join()
    threads = []
    weeklyOptions_flags = dict()

    print("\nValidating data...")
    for i in range(MAX_NUM_THREADS):
        threads.append(validatorThread(i + 1, "thread_" + str(i + 1), i+1, option, date))
        threads[i].start()
    for t in threads:
        t.join()
    del(threads)

    end = time.time()
    if len(skipped_stocks) != 0: print("\nUnable to process symbols: " + str(skipped_stocks))
    print(str(option) + " Dictionary Generation Complete\nElapsed time: %2d minutes, %2d seconds\n" % ((end - start)/60, (end - start)%60))

    if option == "call":
        output = open("../Data/callDictionary.json", "w")
        json.dump(dictionary, output)
        output.close()
        
    if option == "put":
        output = open("../Data/putDictionary.json", "w")
        json.dump(dictionary, output)
        output.close()
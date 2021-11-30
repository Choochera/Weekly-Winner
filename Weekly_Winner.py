from Dictionary_Generator import updateDictionary, Friday
import json
import robin_stocks.robinhood as rh
import datetime
import os
import pandas as pd
import csv

balance = rh.profiles.load_portfolio_profile("equity")

def run(optionType, delta_threshold):
    #Load call dictionary
    def loadCallDictionary():
        try:
            dictionary = json.load( open( "callDictionary.json") )
            if len(dictionary) == 0: 
                print("Warning: call dictionary is empty")
        except FileNotFoundError:
            print("Requested file not found - generating requested call dictionary:")
            updateDictionary("call")
            loadCallDictionary()
        return dictionary

    #Load put dictionary
    def loadPutDictionary():
        try:
            dictionary = json.load( open( "putDictionary.json") )
            if len(dictionary) == 0: 
                print("Warning: put dictionary is empty")
        except FileNotFoundError:
            print("Requested file not found - generating requested put dictionary:")
            updateDictionary("put")
            loadPutDictionary()
        return dictionary

    #Call/Put dictionary data
    dictionary = dict()
    if optionType == 'call':
        dictionary = loadCallDictionary()
        fileName = 'call_sale_options.csv'
    if optionType == 'put':
        dictionary = loadPutDictionary()
        fileName = 'put_sale_options.csv'

    #Isolates options under delta threshold, calculates the maximum possible profit, and outputs data in a dictionary
    result = []
    keys = dictionary.keys()

    for stock in keys:
        for i in range(len(dictionary[stock])):
            data = dictionary[stock][i]
            if abs(float(data[3])) <= delta_threshold:
                amountOfContracts = int(float(balance)/(float(data[1])*100))
                potentialProfit = amountOfContracts*(float(data[2])*100)
                if potentialProfit > 0: result.append([data[0], data[1], data[2], data[3], data[4], amountOfContracts, potentialProfit])
    dictionary = result

    #Export profitable call options
    flag = False
    while not flag:
        if len(dictionary) > 0:
            table = pd.DataFrame(dictionary, columns = ['Symbol', 'Strike', 'Premium', 'Delta', 'IV', '# Contracts', 'Profit'])
            table.sort_values(by = ['Profit'], ascending=True, inplace=True)
            try:
                table.to_csv(fileName, index = False)
                flag = True
                pd.set_option('display.max_rows', None)
                print(table.to_string(index = False))
            except PermissionError:
                print("Cannot rewrite file - open in another window")
                input("Press Enter to continue")
        else:
            print("No " + optionType + " Options Available with current definitions\n")
    print()

print("""                                                        
                    ░██╗░░░░░░░██╗███████╗██╗░░░░░░█████╗░░█████╗░███╗░░░███╗███████╗
                    ░██║░░██╗░░██║██╔════╝██║░░░░░██╔══██╗██╔══██╗████╗░████║██╔════╝
                    ░╚██╗████╗██╔╝█████╗░░██║░░░░░██║░░╚═╝██║░░██║██╔████╔██║█████╗░░
                    ░░████╔═████║░██╔══╝░░██║░░░░░██║░░██╗██║░░██║██║╚██╔╝██║██╔══╝░░
                    ░░╚██╔╝░╚██╔╝░███████╗███████╗╚█████╔╝╚█████╔╝██║░╚═╝░██║███████╗
                    ░░░╚═╝░░░╚═╝░░╚══════╝╚══════╝░╚════╝░░╚════╝░╚═╝░░░░░╚═╝╚══════╝                               
                                              ████████████
                                              █─▄─▄─█─▄▄─█
                                              ███─███─██─█
                                              ▀▀▄▄▄▀▀▄▄▄▄▀\n""")

equityFlag = False
changeCallFlag = False
changePutFlag = False
inputText = ""
delta_threshold = 0.25
while inputText.lower() != "exit":
    print(""" 
          █████████████████████████████████████████████████████████████████████████████████████
          █▄─█▀▀▀█─▄█▄─▄▄─█▄─▄▄─█▄─█─▄█▄─▄███▄─█─▄███▄─█▀▀▀█─▄█▄─▄█▄─▀█▄─▄█▄─▀█▄─▄█▄─▄▄─█▄─▄▄▀█
          ██─█─█─█─███─▄█▀██─▄█▀██─▄▀███─██▀██▄─▄█████─█─█─█─███─███─█▄▀─███─█▄▀─███─▄█▀██─▄─▄█
          ▀▀▄▄▄▀▄▄▄▀▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▀▄▄▄▀▀▀▀▀▄▄▄▀▄▄▄▀▀▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▀▀▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀\n""")
    print(("Option Expiration: " + Friday).center(105))
    if not equityFlag:
        balance = rh.profiles.load_portfolio_profile("equity")
    print((("Equity Balance: $%.2f" % (float(balance)))).center(105))
    print((("Delta Threshold: %.2f" % (float(delta_threshold)))).center(105), end = "\n")
    inputText = input("""
    Type \"update call\" to update call dictionary
    Type \"update put\" to update put dictionary
    Type \"update all\" to update all dictionaries
    Type \"generate call\" to output possible call option sales with acceptable risk
    Type \"generate put\" to output possible put option sales with acceptable risk
    Type \"open call\" to open generated call options file
    Type \"open put\" to open generated put options file
    Type \"isolate [ticker]\" to isolate options of a specific stock symbol
    Type \"delta = 0.##\" to change delta threshold
    Type \"expiration = YYYY-MM-DD\" to change expiration of options (must update dictionaries after updating) 
    Type \"equity = ####\" to change equity to invest 
    Type \"Exit\" to exit the program
    (DEFAULT VALUES: delta = 0.25 - expiration date = next Friday - equity to invest = account balance)
    Press \"Enter\" to continue\n\n""")

    if inputText.lower() == "update call":
        updateDictionary("call", Friday)
        changeCallFlag = False
    elif inputText.lower() == "update put":
        updateDictionary("put", Friday)
        changePutFlag = False
    elif inputText.lower() == "update all":
        updateDictionary("call", Friday)
        updateDictionary("put", Friday)
        changeCallFlag = False
        changePutFlag = False
    elif inputText.lower() == "generate call":
        run("call", delta_threshold)
    elif inputText.lower() == "generate put":
        run("put", delta_threshold)
    elif inputText.lower() == "open call":
        os.system('call_sale_options.csv')
        print()
    elif inputText.lower() == "open put":
        os.system('put_sale_options.csv')
        print() 
    elif inputText.lower().strip().split(" ")[0] == "isolate":
        symbol = inputText.split(" ")[1].upper()
        try:
            with open("call_sale_options.csv") as calls:
                try:
                    with open("put_sale_options.csv") as puts:
                        calls_reader = csv.reader(calls)
                        puts_reader = csv.reader(puts)
                        print(str(symbol) + " Calls:")
                        flag = False
                        for row in calls_reader:
                            if row[0] == symbol:
                                flag = True
                                print("\t" + str(row))
                        if not flag: print("\tNone")
                        flag = False
                        print(str(symbol) + " Puts:")
                        for row in puts_reader:
                            if row[0] == symbol:
                                flag = True
                                print("\t" + str(row))
                        if not flag: print("\tNone")
                except FileNotFoundError:
                    updateDictionary('put', Friday)
        except FileNotFoundError:
            updateDictionary('call', Friday)
        print() 
    elif inputText.lower().strip().split(" ")[0] == "delta" or inputText.lower().strip().split("=")[0] == "delta":
        try:
            if float(inputText.lower().strip().split("=")[1]) <= 1:
                delta_threshold = float(inputText.lower().strip().split("=")[1])
                run("call", delta_threshold)
                print()
                run("put", delta_threshold)
                print("Delta Threshold updated to: " + str(delta_threshold) + "\n")
            else:
                print("Invalid delta")
        except IndexError or ValueError:
            None
    elif inputText.lower().strip().split(" ")[0] == "expiration" or inputText.lower().strip().split("=")[0] == "expiration":
        try:
            temp_Friday = inputText.lower().strip().split("=")[1]
            parts = temp_Friday.strip().split("-")
            if parts[0].isnumeric and len(parts[0]) == 4 and parts[1].isnumeric and len(parts[1]) == 2 and parts[2].isnumeric and len(parts[2]) == 2:
                if datetime.date(int(parts[0]),int(parts[1]), int(parts[2])).strftime('%A') == "Friday":
                    Friday = temp_Friday.strip()
                    print("Expiration updated to: " + str(Friday) + "\n")
                    changeCallFlag = True
                    changePutFlag = True
                else:
                    print("Expiration must be on a Friday")
            else:
                print("Invalid expiration date")
        except IndexError or ValueError:
            print("Invalid input")
    elif inputText.lower().strip().split(" ")[0] == "equity" or inputText.lower().strip().split("=")[0] == "equity":
        try:
            if float(inputText.lower().strip().split("=")[1]) > 0:
                balance = float(inputText.lower().strip().split("=")[1])
                print("Equity updated to: " + str(balance) + "\n")
                equityFlag = True
            else:
                print("Invalid equity balance")
        except ValueError or IndexError:
            print("Invalid input")
    elif inputText.lower() == "exit":
        rh.logout()
    else: print("Invalid input")
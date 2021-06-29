from Dictionary_Generator import updateDictionary, Friday
import json
import numpy as np
import sympy as sp
import robin_stocks.robinhood as rh

#Portfolio balance
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

    #Returns list of close expiration options with deltas below .35
    def highest_call_premium_under_delta(threshold):
        result = []
        for stock in callDictionary_keys:
            stock_info = callDictionary[stock].split("\t")
            if float(stock_info[3]) < threshold:
                result.append(callDictionary[stock])
        return result

    #Returns list of close expiration options with deltas below .35
    def highest_put_premium_under_delta(threshold):
        result = []
        for stock in putDictionary_keys:
            stock_info = putDictionary[stock].split("\t")
            if abs(float(stock_info[3])) < threshold:
                result.append(putDictionary[stock])
        return result

    #Returns highest profit option from list of acceptable deltas for calls
    def max_call_profit(call_stock_list):
        global balance
        profit_dictionary = dict()
        for stock in call_stock_list:
            stock = stock.split("\t")
            profit = 0
            counter = 0
            increment = float(stock[1])*100
            while increment <= float(balance):
                profit += float(stock[2])*100
                counter += 1
                increment += float(stock[1])*100
            profit_dictionary[profit] = "%s - Strike: %s Premium: %s delta: %s Number of Contracts: %s" % (stock[0], stock[1], stock[2], stock[3], counter)
        return profit_dictionary

    #Returns highest profit option from list of acceptable deltas for puts
    def max_put_profit(put_stock_list):
        profit_dictionary = dict()
        for stock in put_stock_list:
            stock = stock.split("\t")
            profit = 0
            counter = 0
            increment = float(stock[1])*100
            while increment <= float(balance):
                profit += float(stock[2])*100
                counter += 1
                increment += float(stock[1])*100
            profit_dictionary[profit] = "%s - Strike: %s Premium: %s delta: %s Number of Contracts: %s" % (stock[0], stock[1], stock[2], stock[3], counter)
        return profit_dictionary

    #Call/Put dictionary data
    callDictionary = loadCallDictionary()
    putDictionary = loadPutDictionary()

    #Call/Put dictionary keys
    callDictionary_keys = sorted(callDictionary)
    putDictionary_keys = sorted(putDictionary)

    #Lists of calls/puts under delta threshold
    callDictionary = highest_call_premium_under_delta(delta_threshold)
    putDictionary = highest_put_premium_under_delta(delta_threshold)

    #Call sales under delta threshold and sorted keys
    profitable_call_sales = max_call_profit(callDictionary)
    profitable_call_sales_keys = sorted(profitable_call_sales)

    if optionType == "call":
        i = 0
        print("\nSym.   Price Prem. Delta     #    Profit\n")
        callTable = np.zeros((len(profitable_call_sales), 6), type(str))
        #Export profitable call options
        with open('call_sale_options.txt', 'w') as f:
            for amount in profitable_call_sales_keys:
                f.write("%s Profit: $%.2f\n"  % (profitable_call_sales[amount], amount))
                info = profitable_call_sales[amount].split()
                callTable[i][0] = str(info[0])
                callTable[i][1] = info[3]
                callTable[i][2] = info[5]
                callTable[i][3] = info[7]
                callTable[i][4] = info[11]
                callTable[i][5] = amount
                i += 1
        sp.pprint(sp.Matrix(callTable), use_unicode = False)

    #Put sales under delta threshold and sorted keys
    profitable_put_sales = max_put_profit(putDictionary)
    profitable_put_sales_keys = sorted(profitable_put_sales)

    if optionType == "put":
        i = 0
        print("\nSym.   Price Prem. Delta      #   Profit\n")
        putTable = np.zeros((len(profitable_put_sales), 6), type(str))
        #Export profitable put options
        with open('put_sale_options.txt', 'w') as f:
            for amount in profitable_put_sales_keys:
                f.write("%s Profit: $%.2f\n"  % (profitable_put_sales[amount], amount))
                info = profitable_put_sales[amount].split()
                putTable[i][0] = str(info[0])
                putTable[i][1] = info[3]
                putTable[i][2] = info[5]
                putTable[i][3] = info[7]
                putTable[i][4] = info[11]
                putTable[i][5] = amount
                i += 1
        sp.pprint(sp.Matrix(putTable), use_unicode = False, wrap_line = False,)

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


inputText = ""
delta_threshold = 0.35
while inputText.lower() != "exit":
    print(""" 
          █████████████████████████████████████████████████████████████████████████████████████
          █▄─█▀▀▀█─▄█▄─▄▄─█▄─▄▄─█▄─█─▄█▄─▄███▄─█─▄███▄─█▀▀▀█─▄█▄─▄█▄─▀█▄─▄█▄─▀█▄─▄█▄─▄▄─█▄─▄▄▀█
          ██─█─█─█─███─▄█▀██─▄█▀██─▄▀███─██▀██▄─▄█████─█─█─█─███─███─█▄▀─███─█▄▀─███─▄█▀██─▄─▄█
          ▀▀▄▄▄▀▄▄▄▀▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▀▄▄▄▀▀▀▀▀▄▄▄▀▄▄▄▀▀▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▀▀▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀\n""")
    print(("Option Expiration: " + Friday).center(105))
    balance = rh.profiles.load_portfolio_profile("equity")
    print((("Account Balance: $%.2f" % (float(balance)))).center(105), end = "\n")
    inputText = input("""
    Type \"update call\" to update call dictionary
    Type \"update put\" to update put dictionary
    Type \"update all\" to update all dictionaries
    Type \"generate call\" to output possible call option sales with acceptable risk
    Type \"generate put\" to output possible put option sales with acceptable risk
    Type \"Exit\" to exit the program
    (To change delta threshold, type \"delta = 0.##\" - delta = 0.35 by default)\n
    Press \"Enter\" to continue\n\n""")

    if inputText.lower() == "update call":
        updateDictionary("call")
    if inputText.lower() == "update put":
        updateDictionary("put")
    if inputText.lower() == "update all":
        updateDictionary("call")
        updateDictionary("put")
    if inputText.lower() == "generate call":
        run("call", delta_threshold)
        print()
    if inputText.lower() == "generate put":
        run("put", delta_threshold)
        print()
    try:
        if float(inputText.lower().strip().split("=")[1]) <= 1:
            delta_threshold = float(inputText.lower().strip().split("=")[1])
            print("Delta Threshold changed to: " + str(delta_threshold) + "\n")
    except IndexError or ValueError:
        None
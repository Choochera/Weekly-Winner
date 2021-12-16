from Dictionary_Generator import updateDictionary
from Data_Filter import nextFriday, isIdleOpen
import json
import stat
import robin_stocks.robinhood as rh
import datetime
import time
import os
import pandas as pd

def run(optionType, delta_threshold, contract_threshold, balance, symbol = "None"):

    Friday = nextFriday()
    dictionary = dict()
    
    #Load call dictionary
    def loadCallDictionary():
        try:
            dictionary = json.load( open( "../Data/callDictionary.json") )
            if len(dictionary) == 0: 
                print("Warning: call dictionary is empty")
        except FileNotFoundError:
            print("Requested file not found - generating requested call dictionary:")
            updateDictionary("call", Friday)
            dictionary = json.load( open( "../Data/callDictionary.json" ) )
        return dictionary

    #Load put dictionary
    def loadPutDictionary():
        try:
            dictionary = json.load( open( "../Data/putDictionary.json") )
            if len(dictionary) == 0: 
                print("Warning: put dictionary is empty")
        except FileNotFoundError:
            print("Requested file not found - generating requested put dictionary:")
            updateDictionary("put", Friday)
            dictionary = json.load( open( "../Data/putDictionary.json" ) )
        return dictionary

    #Call/Put dictionary data
    fileName = '../Data/call_sale_options.csv'
    if optionType == 'call':
        dictionary = loadCallDictionary()
    elif optionType == 'put':
        fileName = '../Data/put_sale_options.csv'
        dictionary = loadPutDictionary()

    #Isolates options under delta threshold, calculates the maximum possible profit, and outputs data in a dictionary
    result = []
    keys = dictionary.keys()
    symbol_provided_flag = False
    if symbol != "None": symbol_provided_flag = True

    for stock in keys:
        for i in range(len(dictionary[stock])):
            data = dictionary[stock][i]
            if abs(float(data[3])) <= delta_threshold:
                amountOfContracts = int(float(balance)/(float(data[1])*100))
                if amountOfContracts <= contract_threshold:
                    potentialProfit = amountOfContracts*(float(data[2])*100)
                    if potentialProfit > 0: 
                        if not symbol_provided_flag:
                            result.append([data[0], data[1], data[2], data[3], data[4], amountOfContracts, potentialProfit])
                        elif data[0] == symbol:
                            result.append([data[0], data[1], data[2], data[3], data[4], amountOfContracts, potentialProfit])
                        else:
                            pass
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
            print("No " + optionType + " Options Available with current definitions\n equity = " + str(balance) + "\n Symbol = " + symbol + "\n delta < " + str(delta_threshold))
            flag = True
    print()

def main():
    balance = rh.profiles.load_portfolio_profile("equity")
    Friday = nextFriday()
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
    delta_threshold = 0.25
    contract_threshold = 10
    while inputText.lower() != "exit":
        print(""" 
            █████████████████████████████████████████████████████████████████████████████████████
            █▄─█▀▀▀█─▄█▄─▄▄─█▄─▄▄─█▄─█─▄█▄─▄███▄─█─▄███▄─█▀▀▀█─▄█▄─▄█▄─▀█▄─▄█▄─▀█▄─▄█▄─▄▄─█▄─▄▄▀█
            ██─█─█─█─███─▄█▀██─▄█▀██─▄▀███─██▀██▄─▄█████─█─█─█─███─███─█▄▀─███─█▄▀─███─▄█▀██─▄─▄█
            ▀▀▄▄▄▀▄▄▄▀▀▄▄▄▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀▄▄▄▄▄▀▀▄▄▄▀▀▀▀▀▄▄▄▀▄▄▄▀▀▄▄▄▀▄▄▄▀▀▄▄▀▄▄▄▀▀▄▄▀▄▄▄▄▄▀▄▄▀▄▄▀\n""")
        print(("Option Expiration: " + Friday).center(105))
        print((("Equity Balance: $%.2f" % (float(balance)))).center(105))
        print((("Delta Threshold: %.2f" % (float(delta_threshold)))).center(105), end = "\n")
        print((("Contract Threshold: %.2f" % (int(contract_threshold)))).center(105), end = "\n")

        modified_dates = []
        file_names = ['../Data/callDictionary.json', '../Data/putDictionary.json']
        for file in file_names:
            try:
                path_to_date = os.path.dirname(os.path.abspath(__file__))
                path_to_date = os.path.join(path_to_date, file)
                path_to_date = os.stat ( path_to_date )
                path_to_date = time.ctime ( path_to_date [ stat.ST_MTIME ] )
                modified_dates.append(path_to_date)
            except FileNotFoundError:
                modified_dates.append("%s has not been generated" % file)

        inputText = input("""
        Type \"update call\" to update call dictionary (Last Modified: %s)
        Type \"update put\" to update put dictionary (Last Modified: %s)
        Type \"update all\" to update all dictionaries
        Type \"generate call\" to output possible call option sales with acceptable risk
        Type \"generate put\" to output possible put option sales with acceptable risk
        Type \"open call\" to open generated call options file
        Type \"open put\" to open generated put options file
        Type \"isolate [ticker]\" to isolate options of a specific stock symbol
        Type \"delta = 0.##\" to change delta threshold
        Type \"max contracts = ##\" to change contract threshold
        Type \"expiration = YYYY-MM-DD\" to change expiration of options (must update dictionaries after updating) 
        Type \"equity = ####\" to change equity to invest 
        Type \"reset equity\" to set equity back to account balance
        Type \"Exit\" to exit the program
        (DEFAULT VALUES: delta = 0.25 - expiration date = next Friday - equity to invest = account balance)
        Press \"Enter\" to continue\n\n""" % (modified_dates[0], modified_dates[1]))
        
        if inputText.lower() == "update call":
            updateDictionary("call", Friday)
        elif inputText.lower() == "update put":
            updateDictionary("put", Friday)
        elif inputText.lower() == "update all":
            updateDictionary("call", Friday)
            updateDictionary("put", Friday)
        elif inputText.lower() == "generate call":
            run("call", delta_threshold, contract_threshold, balance)
        elif inputText.lower() == "generate put":
            run("put", delta_threshold, contract_threshold, balance)
        elif inputText.lower() == "open call":
            os.system('../Data/call_sale_options.csv')
            print()
        elif inputText.lower() == "open put":
            os.system('../Data/put_sale_options.csv')
            print() 
        elif inputText.lower().strip().split(" ")[0] == "isolate":
            symbol = inputText.split(" ")[1].upper()
            run("call", delta_threshold, contract_threshold, balance, symbol)
            run("put", delta_threshold, contract_threshold, balance, symbol)
            print() 
        elif inputText.lower().strip().split(" ")[0] == "delta" or inputText.lower().strip().split("=")[0] == "delta":
            try:
                if float(inputText.lower().strip().split("=")[1]) <= 1:
                    delta_threshold = float(inputText.lower().strip().split("=")[1])
                    print("Delta Threshold updated to: " + str(delta_threshold) + "\n")
                else:
                    print("Invalid delta")
            except IndexError or ValueError:
                None
        elif inputText.lower().strip().split(" ")[0] == "max" and  inputText.lower().strip().split(" ")[1] == "contracts":
            try:
                if float(inputText.lower().strip().split("=")[1]) >= 1:
                    contract_threshold = float(inputText.lower().strip().split("=")[1])
                    print("Contract Threshold updated to: " + str(contract_threshold) + "\n")
                else:
                    print("Invalid value")
            except IndexError or ValueError:
                None
        elif inputText.lower().strip().split(" ")[0] == "expiration" or inputText.lower().strip().split("=")[0] == "expiration":
            try:
                temp_Friday = inputText.lower().strip().split("=")[1]
                parts = temp_Friday.strip().split("-")
                if parts[0].isnumeric and len(parts[0]) == 4 and parts[1].isnumeric and len(parts[1]) == 2 and parts[2].isnumeric and len(parts[2]) == 2:
                    if datetime.date(int(parts[0]),int(parts[1]), int(parts[2])).strftime('%A') == "Friday":
                        Friday = temp_Friday.strip()
                        print("Expiration updated to: " + str(Friday) + "\nUpdating data...")
                        updateDictionary("call", Friday)
                        updateDictionary("put", Friday)
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
                else:
                    print("Invalid equity balance")
            except ValueError or IndexError:
                print("Invalid input")
        elif inputText.lower().strip() == "reset equity":
            balance = rh.profiles.load_portfolio_profile("equity")
        elif inputText.lower() == 'exit':
            #Check if auto-update is already running, if not then run.
            if isIdleOpen():
                os.system("start pythonw idle.pyw")
            print("Goodbye!")
        else: print("Invalid input")

if __name__ == "__main__":
    main()
![alt text](https://github.com/Choochera/WeeklyWinner/blob/main/Source/dashboard.png "Home Screen")

# Weekly Winner

Python CMD line program that utilizes one's Robinhood brokerage account and assists in employing the wheel investment strategy by parsing through stocks and their corresponding weekly options (limited to single calls/puts) for highest total profitability - taking into account the maximum number of contracts afforded by portfolio balance or a user defined amount of equity (maximum equity > strike*100), the premium credit awarded by the sale of said contract (# contracts * premium * 100) and a user-defined delta threshold to filter the contracts through for risk management. The result is a printed list of options in order of maximum profit that have strike prices closest to the current price of the underlying stock while maintaining a delta level below (by default) 0.25. This mitigates but of course does not eliminate risk - how much trust one puts in delta as a determinant of risk diminishment and where the user places the maximum delta is up to the user. The expiration date for the options is initially set to the next Friday from whatever day the program is used and a csv file is provided containing the large majority of stocks providing weekly options (source: https://www.cboe.com/available_weeklys/). NOTE: this list updates automatically.

IMPORTANT: The options information is not in real-time but rather is collected by dictionaries that can be updated whenever the user wishes. The average run time is +/- 2 minutes for updating either dictionary. For this reason, the program produces best results updating afterhours when options are not being traded to support educated actions for the follow trading day.

DISCLAIMER: I am not fit to provide financial advice and the usability and application of this program to ones stock market endeavors is entirely up to the discretion of the user. I am not responsible for any poor decisions/investments made by any user spurred by the use of this code.

## Example of updating call/put dictionary data

![alt text](https://github.com/Choochera/WeeklyWinner/blob/main/Source/update.PNG "Update Put")

## Example Output with delta < 0.25

![alt text](https://github.com/Choochera/WeeklyWinner/blob/main/Source/output.PNG "Output")

# How to run:

python Weekly_Winner.py

# Necessary installs

1. robin_stocks
  unofficial Robinhood API 
  instructions to install provided here: https://algotrading101.com/learn/robinhood-api-guide/
  documentation: https://github.com/jmfernandes/robin_stocks

2. pandas

# I want to thank the people over at the Robin Stocks github for making this possible - I'm new to financial programming and this has netted me more than a few dollars in use and priceless experience!
  https://github.com/jmfernandes/robin_stocks

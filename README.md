# WeeklyWinner

Python CMD line program that utilizes ones Robinhood brokerage account and assists in employing the wheel investment strategy by parsing through stocks and their corresponding weekly options (limited to single calls/puts) for highest total profitability - taking into account the maximum number of contracts afforded by portfolio balance or a user defined amount of equity (maximum equity > strike*100), the premium credit awarded by the sale of said contract (# contracts * premium * 100) and a user-defined delta threshold to filter the contracts through for risk management. The result is a printed list of options in order of maximum profit that have strike prices closest to the current price of the underlying stock while maintaining a delta level below (by default) 0.35. This mitigates but of course does not eliminate risk - how much trust one puts in delta as a determinant of risk diminishment and where the user places the maximum delta is up to the user. The expiration date for the options is automatically set to the next Friday from whatever day the program is used and a txt file is provided containing the large majority of stocks providing weekly options (source: https://www.cboe.com/available_weeklys/). NOTE: this list does not update automatically.

IMPORTANT: The options information is not in real-time but rather is collected by dictionaries that can be updated whenever the user wishes. The average run time is +/35 seconds for updating either dictionary. This program produces best results updating afterhours when options are not being traded to support educated actions for the follow trading day.

DISCLAIMER: I am not fit to provide financial advice and the usability and application of this program to ones stock market endeavors is entirely up to the discretion of the user. I am not responsible for any poor decisions/investments made by any user spurred by the use of this code.

# Necessary installs

1. robin_stocks
  unofficial Robinhood API 
  instructions to install provided here: https://algotrading101.com/learn/robinhood-api-guide/
  documentation: https://github.com/jmfernandes/robin_stocks
2. numpy
  https://numpy.org/install/
3. sympy
  https://pypi.org/project/sympy/

from Dictionary_Generator import updateDictionary
from Data_Filter import nextFriday
import time

Friday = nextFriday()
while True:
    try:
        if int(time.strftime("%H", time.localtime())) <= 16:
            updateDictionary("put", Friday)
            updateDictionary("call", Friday)
        time.sleep(1800)
    except:
        pass
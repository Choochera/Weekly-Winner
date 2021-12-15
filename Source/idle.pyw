from Dictionary_Generator import updateDictionary
from Data_Filter import nextFriday
import time

def main():
    Friday = nextFriday()
    while True:
        try:
            if int(time.strftime("%H", time.localtime())) <= 15:
                updateDictionary("put", Friday)
                updateDictionary("call", Friday)
            time.sleep(3600)
        except: 
            pass

if __name__ == "__main__":
    main()
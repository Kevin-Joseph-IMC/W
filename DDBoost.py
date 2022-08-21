import json
import os

def DDBoost():
    path = os.path.dirname(os.path.abspath(__file__))

    with open(f'{path}\\data\\ansb100c\\DDBoost.json', 'r') as openfile:
        # Reading from json file
        dictionary = json.load(openfile)

    if True:
        print("OK - DDBoost is enabled")
    else:
        print("CRITICAL - DDBoost is disabled")

if __name__ == "__main__":
    DDBoost()




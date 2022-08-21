import json
import requests
import argparse
import getpass
import datetime
import time
import os

# http_GET_requests >>> names_to_write
names_to_write = [
    ""
]

URL_to_req = [
    ""
]

for i in range(len(URL_to_req)):
    json_object = json.dumps(i, indent=4)
    path = os.path.dirname(os.path.abspath(__file__))
    with open(f"{path}\\data\\ansb100c\\{names_to_write[i]}","w") as outfile:
        outfile.write(json_object)








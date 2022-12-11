import sys
from os.path import exists, basename
from urllib.parse import urlparse
import getpass
import base64
import requests
import argparse
import operator, logging
import mysql.connector
import re, ast, keyword, urllib3
from textwrap import indent
from pip._internal.cli.cmdoptions import cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
"""
if args.verbose >=1 print()

"""

class RestClient:
    def __init__(self):
        self.session = requests.Session()

    def __call__(self, args):
        code = self.batchReturnCode(args)
        #print(code)
        return code

    def restConfig(self, args, filepath):
        restConfig_dict = {}

        if exists(filepath):
            with open(filepath) as f:

                line = f.readline().strip()

                restConfig_dict["header"] = ";".join(line.split(";"))
                for line in f:
                    rConfig = line.strip().split()
                    if not rConfig:
                        continue
                    if len(rConfig) == 3:
                        keys = rConfig[:2]
                    else:
                        keys = rConfig[:2] + rConfig[3:]
                    value = rConfig[2]
                    key_string = ";".join(keys)
                    restConfig_dict[key_string] = value
                    #v2
                return restConfig_dict
        else:
            #v1
            return 1
    def restURL(self, args):
        #v2
        url_regex = re.search(r"^https?://[^/]+/", args.url)
        #v2

        if url_regex:
            abs_url = args.url
            #v2
        else:
            x = re.search(r"^/", args.url)
            if not x:
                #v1
                return 1

            rel_url = args.url
            if not args.s:
                #v1
                return 1
            #v2
            url_regex = re.search(r"^https?://.+", args.s)
            #v2
            if not url_regex:
                #v1
                return 1
            abs_url = args.s + rel_url
            #v2
        return abs_url

    def authentication(selfself, args, abs_URL):
        if args.enc:
            username = input("Please enter username: ")
            password = getpass.getpass("Please enter password (Hidden Input): ")
            lcf = input("Please enter file path of your login-config file: ")

            password_encoded = base64.b64encode(f'{password}'.encode())
            with open(lcf, "a") as f:
                string = f"\n;u\n{username}\n{password_encoded}"
                f.write(string)
            return (username, password)

        if args.u:
            #v2
            try:
                user_acc = json.loads(args.u)
            except json.decoder.JSONDecodeError as e:
                #v1
                return 1
            #v2
            #v2
            if type(user_acc) == dict:
                #v2
                for k, v in user_acc.items():
                    key = k
                    value = v
                #v2
                return (key, value)
            else:
                #v2
                return 1

        elif args.lcf:
            file_exists = exists(args.lcf)
            if file_exists:
                with open(args.lcf) as f:
                    #v1
                    line = f.readline()
                    if line.strip() == ";ud":
                        db_keywords = ["DBDRIVER", "DBHOST=","DBNAME=","DBUSER=","DBPASS","DBTABLE=","COLUSER=","COLPASS="]
                        dbdriver, dbhost, dbname, dbuser, dbpass, dbtable, coluser, colpass ="","","","","","","",""
                        i = f.readline().strip()
                        while i:
                            if ";" == i[0]:
                                break
                            elif db_keywords[0] in i:
                                dbdriver = i[len(db_keywords[0]):]
                            elif db_keywords[1] in i:
                                dbhost = i[len(db_keywords[1]):]
                            elif db_keywords[2] in i:
                                dbname = i[len(db_keywords[2]):]
                            elif db_keywords[3] in i:
                                dbuser = i[len(db_keywords[3]):]
                            elif db_keywords[4] in i:
                                dbpass = i[len(db_keywords[4]):]
                                dbpass = base64.b64decode(dbpass)
                                dbpass = dbpass.decode()
                            elif db_keywords[5] in i:
                                dbtable = i[len(db_keywords[5]):]
                            elif db_keywords[6] in i:
                                coluser = i[len(db_keywords[6]):]
                            elif db_keywords[7] in i:
                                colpass = i[len(db_keywords[7]):]
                                colpass = base64.b64decode(colpass)
                            i = f.readline().strip()
                        #v2
                        if not (dbdriver and dbhost and dbname and dbuser and dbpass and dbtable and coluser and colpass):
                            #v1
                            return 1
                        try:
                            #v1
                            conn = mysql.connector.connect(
                                user = dbuser,
                                password = dbpass,
                                host = dbhost,
                                database = dbname
                            )
                        except mysql.connector.Error as e:
                            #v1
                            return 1
                        cur = conn.cursor()
                        cur.execute(f"SELECT * FROM {dbtable} WHERE user=''{coluser}")
                        #v1
                        authentication = cur.fetchone()
                        if not authentication:
                            #v1
                            return 1
                        #v2
                        return (authentication[2], authentication[3])
                    elif line.strip() == ";u":
                        username = f.readline().strip()
                        password_encoded = f.readline.strip()
                        password = base64.b64decode(password_encoded)
                        #v2
                        return (username, password)
                    else:
                        line = f.readline()
            else:
                # v1
                return 1
        else:
            #v1
            return 1


    def method(self, args, abs_URL, account, header, cert_verify):
        methods = {
            "GET":self.session.get,
            "POST":self.session.post,
            "DELETE":self.session.delete,
            "PUT":self.session.put
        }
        if header: header = ast.literal_eval(args.head)
        #v2
        if args.m not in methods:
            #v1
            return 1
        #v1
        try:
            if not account:
                if not args.body:
                    response = methods[args.m](abs_URL, header=header, verify= cert_verify)
                else:
                    body = ast.literal_eval(args.body)
                    response = methods[args.m](abs_URL, json=body, headers = header, verify= cert_verify)
            else:
                self.session.auth = (account[0], account[1])
                if not args.body:
                    response = methods[args.m](abs_URL, headers = header, verify= cert_verify)
                else:
                    body = ast.literal_eval(args.body)
                    response = methods[args.m](abs_URL, json=body, headers=header, verify=cert_verify)
        except Exception as e:
            logging.error(e)
            return 1
        #v1
        #printresposne
        logging.info("Status "+str(response.text))
        logging.info("URL "+response.url)
        if len(response.text) > 0:
            logging.info("Response text exists: True")
        else:
            logging.info("Response text exists: False")
        #v2
        return response

    def queryCode(self, args, response, restConfig_dict, abs_URL):
        if restConfig_dict:
            #v2
            #v2
            for k, v in restConfig_dict.items():
                keys = k.split(";")
                #v2
                if len(keys) == 2:
                    if keys[0] in abs_URL:
                        if keys[1] == str(response.status_code):
                            #v1
                            return 0
                elif len(keys) == 3:
                    if keys[0] in abs_URL:
                        if keys[1] == str(response.status_code):
                            #v2
                            x = re.search(keys[2],response.text)
                            #v2
                            if x:
                                #v1
                                return 0
            #v1
            return 2

        elif args.q:
            if str(response.status_code) == "200":
                if response.headers.get("content-type") != "application/json":
                    #v2
                    return 0
                else:
                    #v2
                    string = str(response.text)
                    string = string.encode("unicode_escape").decode()
                    #v2
                    x = re.findall(args.q, string)
                    if x:
                        #v2
                        #v2
                        return 0
                    else:
                        #v2
                        return 2
            else:
                res = response.json()
                res["status code"] = response.status_code
                logging.error(res)
                #v1
                return 2
        else:
            if str(response.status_code) == "200":
                #v2
                return 0
            else:
                res = response.json()
                res["status code"] = response.status_code
                logging.error(res)
                #v1
                return 2
    def batchReturnCode(self, args):
        abs_URL = self.restURL(args)
        if abs_URL == 1:
            return 1
        authentication = self.authentication(args, abs_URL)
        if authentication == 1:
            account = None
        else:
            account = authentication
        response = self.method(args, abs_URL, account, args.head, args.ignorecert)
        if response == 1:
            return 1
        if args.rcf:
            restConfig_dict = self.restConfig(args, args.rcf)
            if restConfig_dict == 1:
                return 1
        else:
            restConfig_dict = None
        code = self.queryCode(args, response, restConfig_dict, abs_URL)
        return code

def create_parser():
    pass

def create_logging():
    pass

if __name__ == "__main__":
    args = create_parser().parse_args()
    #v2
    #v1
    if args.log: create_logging()
    client = RestClient()
    exit_number = client(args)
    #v1
    if exit_number == 1:
        exit(1)
    elif exit_number == 2:
        exit(2)
    elif exit_number == 0:
        exit(0)





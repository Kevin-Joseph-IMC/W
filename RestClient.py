from cryptography.fernet import Fernet
from os.path import exists, basename
from urllib.parse import urlparse
#from requests_kerberos import HTTPKerberosAuth
import requests
import argparse
import operator
import logging
import mysql.connector
import re
import ast
import sys

session = requests.Session()

def r_RestConfigFile(r_filepath):

    restConfig_dict = {}

    # Check if given file exists
    if exists (r_filepath):
        with open(r_filepath) as f:

            # Read first line of file and remove the new line at the end
            line = f.readline().strip()

            #Put first line into a dict
            restConfig_dict["header"] = ";".join(line.split())

            for line in f:
                #split the line into single strings
                rConfig= line.strip().split()

                # If only white space exists
                if not rConfig:
                    continue

                #If line only has URL, httpreturn & BatchReturncode
                if len(rConfig) == 3:

                    #Read until httpreturn
                    keys = rConfig[:2]
                else:

                    #Query & QueryValue included
                    keys = rConfig[:2] + rConfig[3:]

                #BatchReturncode
                value = rConfig[2]

                # Place everything from line into the dict
                key_string = ";".join(keys)
                restConfig_dict[key_string] = value
            return restConfig_dict
    else:
        #raise FileNotFoundError("File path to 'Newton.config' does not exist.")
        return 1

def c_s_p_RestURL(args):
    # Used operators: -c, -s, -p

    url_regex = re.search(r"^https?://[^/]+/",args.c)

    #Check if it absolute or relative URL
    if url_regex:
        abs_url = args.c
        return abs_url
    else:
        # Assuming that it is the relative path
        rel_url = args.c

        # Check if the RestServer is correctly typed
        url_regex = re.search(r"^https?://.+", args.s)
        if not url_regex: return 1

        #Check if port number is included
        if args.p:
            abs_url = args.s + ":" + str(args.p) + rel_url
        else:
            abs_url = args.s + rel_url
        return abs_url



def u_ud_cf_Authentication(args):
    if args.ud:
        sql_string = args.ud
        db_string = re.findall(
            r"^\w+=\w+:\w+://(\w+)((:)(\d+))?/(\w+)\?user=(\w+)\&password=([-\w]+)\&restserver=([A-Za-z0-9:]+)",
            sql_string)
        if not db_string: return 1
        db = db_string[0][4]
        dbport = db_string[0][3]
        dbhost = db_string[0][0]
        dbuser = db_string[0][5]
        dbpass = db_string[0][6]
        dbrestserver = db_string[0][7]

        try:
            conn = mysql.connector.connect(
                user=dbuser,
                password=dbpass,
                host=dbhost,
                database=db
            )
        except mysql.connector.Error as e:
            return 1

        cur = conn.cursor()
        cur.execute(f"SELECT * FROM oenb_user WHERE restserver='{dbrestserver}'")
        authentication = cur.fetchone()
        if not authentication: return 1
        return (authentication[1], authentication[2])

    elif args.u:
        user_acc = ast.literal_eval(args.u)
        if ("user" in user_acc) and ("pass" in user_acc):
            return (user_acc["user"], user_acc["pass"])
        else:
            return 1

    elif args.cf:

        # Does file exist
        file_exists = exists(args.cf)
        if file_exists:
            with open(args.cf) as f:

                line = f.readline()
                while line:
                    if line.strip() == ";ud":
                        sql_string = f.readline().strip()
                        db_string = re.findall(r"^\w+=\w+:\w+://(\w+)((:)(\d+))?/(\w+)\?user=(\w+)\&password=([-\w]+)\&restserver=([A-Za-z0-9:]+)",sql_string)
                        if not db_string: return 1
                        db = db_string[0][4]
                        dbport = db_string[0][3]
                        dbhost = db_string[0][0]
                        dbuser = db_string[0][5]
                        dbpass = db_string[0][6]
                        dbrestserver = db_string[0][7]

                        try:
                            conn = mysql.connector.connect(
                                user = dbuser,
                                password = dbpass,
                                host = dbhost,
                                database = db
                            )
                        except mysql.connector.Error as e:
                            return 1

                        cur = conn.cursor()
                        cur.execute(f"SELECT * FROM oenb_user WHERE restserver='{dbrestserver}'")
                        authentication = cur.fetchone()
                        if not authentication: return 1
                        return (authentication[1], authentication[2])


                    elif line.strip() == ";u":
                        username = f.readline().strip()
                        password = f.readline().strip()
                        return (username, password)
                    else:
                        return 1
        else:
            return 1
    else:
        return 1


def m_Method(args, abs_URL, user_opt, pass_opt):

    methods = {
        "GET": session.get,
        "POST": session.post,
        "DELETE": session.delete,
        "PUT": session.put
    }

    #If REST method does not exist
    if args.m not in methods: return 1
    if not user_opt:
        if not args.b:
            response = methods[args.m](abs_URL)
        else:
            body = ast.literal_eval(args.b)
            response = methods[args.m](abs_URL, json=body)
    else:
        session.auth = (user_opt, pass_opt)
        if not args.b:
            response = methods[args.m](abs_URL)
        else:
            body = ast.literal_eval(args.b)
            response = methods[args.m](abs_URL, json=body)
    return response





def q_Code(args, response, restConfig_dict, abs_URL):
    ops = {
        "=": operator.eq,
        "<": operator.lt,
        ">": operator.gt,
        "<=": operator.le,
        ">=": operator.ge,
        "!=": operator.ne
    }


    def find_value(dict1, keys, value, ops_query):

        if "[]" in keys[0]:

            k = keys[0][:-2]

            for element in dict1[k]:

                if len(keys) > 1: keys.pop(0)

                return find_value(element, keys, value, ops_query)
        else:

            if (value.replace('.','',1).isdigit()):
                if ops_query(float(dict1[keys[0]]), float(value)):
                    return True
                else:
                    return None
            elif ops_query(str(dict1[keys[0]]).lower(),str(value).lower()):
                return True
            else:
                return None

    restConfig_list = [k.split(";") for k in restConfig_dict.keys() if ";" in k]
    for rest in restConfig_list:
        wildcard = re.search(r"[*]",rest[0])

        #rest[URL]
        if rest[0] in abs_URL:

            #rest[http]
            if str(response.status_code) == str(rest[1]):

                #Check if queue parameter is available
                if not args.q: return restConfig_dict[";".join(rest)]

                queryList = re.findall(r"""([\[\]/A-Za-z]+)([!<>][=]|[=<>!])(["A-Za-z0-9]+)""", args.q)

                if not queryList: return 1
                for q, o, v in queryList:

                    if rest[2] == q:

                        r_v = rest[3].replace('\"', '')
                        r_v = r_v.replace('\'', '')
                        r_v = re.findall(r"""([!<>][=]|[=<>!])(["A-Za-z0-9]+)""", r_v)
                        r_v = r_v[0][1]

                        v = v.replace('\"', '')
                        v = v.replace('\'', '')
                        if r_v == v:
                            keys = re.findall("\w+", q)
                            if find_value(response.json(), keys, v, ops[o]):
                                return restConfig_dict[";".join(rest)]

        elif wildcard:
            check = True
            s = [((m.start(0)), (m.end(0))) for m in re.finditer("[*]", rest[0])]
            for i in range(len(s) - 1):
                string = rest[0][s[i][1]:s[i + 1][0]]
                if string not in abs_URL:
                    check = False
                    break
            if not check: continue

            # rest[http]
            if str(response.status_code) == str(rest[1]):

                # Check if queue parameter is available
                if not args.q: return restConfig_dict[";".join(rest)]

                queryList = re.findall(r"""([\[\]/A-Za-z]+)([!<>][=]|[=<>!])(["A-Za-z0-9]+)""", args.q)
                if not queryList: return 1

                for q, o, v in queryList:
                    if rest[3] == q:
                        keys = re.findall("\w+", q)
                        if find_value(response.json(), keys, v, ops[o]):
                            return restConfig_dict[";".join(rest)]

    return 1


    #(rec) = If multiple same values exists in restConfig_dict, then do recursion
    #1) Check if [abs_URL in restConfig_dict[0]](rec)
    #2) Check if [response.status_code in restConfig_dict[1]]

    #3) Analyze args.q
    #4) Check if [re_query in restConfig_dict[3]](rec)
    #5) Check if [re_query_value in restConfig_dict[4]]

    #If found: 0, If not: 1

def batchReturnCode(args):

    # Required operators
    restConfig_dict = r_RestConfigFile(args.r)  # Converting the file into a dict
    if restConfig_dict == 1: return 1
    abs_URL = c_s_p_RestURL(args) # Constructing the absolute path
    if abs_URL == 1: return 1

    #Optional operators
    authentication = u_ud_cf_Authentication(args)
    if authentication == 1:
        username, password = None, None
    else:
        username, password = authentication[0], authentication[1]


    response = m_Method(args, abs_URL, username, password)
    if response == 1: return 1

    code = q_Code(args, response, restConfig_dict, abs_URL)
    return code

if __name__ == "__main__":

    parser  = argparse.ArgumentParser(description="Process all parameters and arguments")

    parser.add_argument('-r', required=True, help="RestConfigFile [Required] | e.g. 'OeNB_test\RestConfig.config'")
    parser.add_argument('-c', required=True, help="RestURL. [Required] e.g. 'http://anut240:6655/ae/api/v1/1/system/agents'")
    parser.add_argument('-s', help="RestServer [Optional] | e.g. http://anut240")
    parser.add_argument('-p', help="RestPort [Optional] | e.g. 6655")
    #sqlDriverConnect=jdbc:mariadb://anut240:6655/####?user=#####&password=####&restserver=gorest'
    parser.add_argument('-ud',help="UserDatabase string [Optional] | e.g. 'sqlDriverConnect=jdbc:postgresql://host:port/databaser?ssl-true&user-benutzer&password-meinpasswort'")
    parser.add_argument('-u', help="Username & Password [Optional] | e.g. '('user': 'RESTTEST/ITO', 'pass': 're$t0815')'")
    parser.add_argument('-cf', help="File path to Configfile.conf [Optional] | e.g. 'OeNB_test\Configfile.config'")
    parser.add_argument('-b', help= "Request Body in JSON [Optional]")
    parser.add_argument('-m', default="GET", help="Methods (GET, POST, DELETE). [Default: GET]")

    parser.add_argument('-q', help="first, Query, QueryList. [Default: first] [Optional] | e.g. data[]/name='Unix1'")

    parser.add_argument('-k', help="Kerberos connection. [Optional]")

    args = parser.parse_args()

    code = batchReturnCode(args)
    print(code)




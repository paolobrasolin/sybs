#!/usr/bin/env python3
# coding: utf-8

import os
import csv

import html
import requests
import json

from retrying import retry
import ssl


# the source CSV is UTF-8 w/BOM, so utf-8-sig is needed
# with open(file='talks_table.csv', mode='r', encoding='utf-8-sig') as csv_file:
    # talks = [{key: value for key, value in row.items()}
             # for row in csv.DictReader(csv_file)]

# ids = [int(talk["post_id"]) for talk in talks]


SESSION = requests.Session()
ADAPTER = requests.adapters.HTTPAdapter(max_retries=10)
SESSION.mount('https://', ADAPTER)

def fetch_page(page):
    url = "https://www.amruta.org/wp-json/wp/v2/posts/?per_page=100&page={0}".format(page)
    response = SESSION.get(url)
    return json.loads(response.text)


def is_ssl_error(exception):
    """Check whether an exception is an SSL error."""
    return (isinstance(exception, requests.exceptions.SSLError) or
            isinstance(exception, ssl.SSLError))

@retry(retry_on_exception=is_ssl_error,
       wait_exponential_multiplier=1000,
       wait_exponential_max=10000)
def safe_fetch_page(page):
    return fetch_page(page)




page = 1
digest = []
data_is_pouring = True
while data_is_pouring:
    new_data = safe_fetch_page(page)
    if len(new_data)>0:
        print("Digested {0} posts.".format(len(new_data)))
        digest.extend(new_data)
        page = page + 1
    else:
        print("Posts exhausted. Total: {0}".format(len(digest)))
        data_is_pouring = False

with open('amruta.json', 'w') as output_file:
    json.dump(digest, output_file)



# from argparse import ArgumentParser
# import logging
# import json
# import html
# import ssl
# from subprocess import Popen, PIPE
# from os import rename
# from time import sleep
# from retrying import retry
# from tqdm import tqdm
# import requests
#
# #=====================[ COMMANDLINE PARSING ]===================================
#
# PARSER = ArgumentParser(
    # description='Fetches Yahoo! group messages and archives them into an mbox file.')
#
# PARSER.add_argument(
    # 'group', type=str,
    # help='name of the Yahoo! group')
#
# PARSER.add_argument(
    # '--first', type=int, default=1,
    # help='index of first message to fetch (default 1)')
#
# PARSER.add_argument(
    # '--last', type=int, default=100,
    # help='index of last message to fetch (default: 100)')
#
# PARSER.add_argument(
    # '--sleep', type=int, default=0,
    # help='ms of sleep between requests (default: 0)')
#
# PARSER.add_argument(
    # '--log', type=str, default='WARNING',
    # choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    # help='sets the logging level (default: WARNING)')
#
# ARGS = PARSER.parse_args()
#
# #=====================[ LOGGING ]===============================================
#
# NUMERIC_LOG_LEVEL = getattr(logging, ARGS.log.upper(), None)
# if not isinstance(NUMERIC_LOG_LEVEL, int):
    # raise ValueError("Invalid log level: {0}".format(ARGS.log))
# logging.basicConfig(filename='.{0}.log'.format(ARGS.group), level=NUMERIC_LOG_LEVEL)
#
# #=====================[ FETCHING ]==============================================
#
# # Set up the connection.
#
# SESSION = requests.Session()
# ADAPTER = requests.adapters.HTTPAdapter(max_retries=10)
# SESSION.mount('https://', ADAPTER)
#
# # This is the basic fetching routine.
#
# def fetch_mail(group_name: str, message_id: int) -> str:
    # """Fetch a message from a group using Y! API."""
    # url = ("https://groups.yahoo.com/api/v1"
           # "/groups/{0}/messages/{1}/raw".format(group_name, message_id))
    # response = SESSION.get(url)
    # response.raise_for_status()
    # data = json.loads(response.text)
    # raw_email = data["ygData"]["rawEmail"]
    # # raw_email = raw_email.replace('=\r\n', '')
    # return html.unescape(raw_email)
#
# # I need to wrap the fetching routine to counter SSL errors by retrying.
# # My connection is kinda flakey.
#
# def is_ssl_error(exception):
    # """Check whether an exception is an SSL error."""
    # return (isinstance(exception, requests.exceptions.SSLError) or
            # isinstance(exception, ssl.SSLError))
#
# # CAVEAT: there is no max number of retries.
#
# @retry(retry_on_exception=is_ssl_error,
       # wait_exponential_multiplier=1000,
       # wait_exponential_max=10000)
# def safe_fetch_mail(group_name: str, message_id: int) -> str:
    # """Fetch a message from a group using Y! API. Retry on SSL errors."""
    # return fetch_mail(group_name, message_id)
#
# #=====================[ FORMATTING ]============================================
#
# def formail(raw: str) -> str:
    # """Pipe a string to formail and return the result."""
    # pipe = Popen(['formail'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    # return pipe.communicate(input=raw.encode())[0].decode()
#
# #=====================[ MAIN LOOP ]=============================================
#
# DIGEST = open(".{0}.mbox".format(ARGS.group), "w")
#
# LAST = 0
# """
# Keeps track of the last succesfully digested message.
# Used for graceful recovery in case of catastrophic failure.
# """
#
# try:
    # for msgid in tqdm(range(ARGS.first, ARGS.last+1)):
        # sleep(ARGS.sleep)
        # try:
            # rawMail = safe_fetch_mail(ARGS.group, msgid)
            # formattedMail = formail(rawMail)
            # DIGEST.write(formattedMail)
        # except requests.exceptions.HTTPError as exc:
            # code = exc.response.status_code
            # if code == 404:
                # # the message was probably deleted (spam?), just log a warning
                # logging.warning("HTTP error 404 when fetching message %s", msgid)
            # else:
                # logging.error("HTTP error %s when fetching message %s", code, msgid)
                # if code == 500:
                    # logging.error("Quota was probably exceeded (HTTP error 500)")
                # raise exc
        # else:
            # LAST = msgid
# except Exception as exc:
    # logging.exception(exc)
    # raise exc
# finally:
    # DIGEST.close()
    # rename(".{0}.mbox".format(ARGS.group),
           # "{0}_{1}-{2}.mbox".format(ARGS.group, ARGS.first, LAST))
    # rename(".{0}.log".format(ARGS.group),
           # "{0}_{1}-{2}.log".format(ARGS.group, ARGS.first, LAST))
#

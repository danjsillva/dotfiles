#!/usr/bin/env python3

import os
import pathlib
import subprocess
import time
import argparse
from apiclient import discovery, errors
from oauth2client import client, file
from httplib2 import ServerNotFoundError

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--prefix', default='\uf0e0')
parser.add_argument('-c', '--color', default='#e06c75')
parser.add_argument('-ns', '--nosound', action='store_true')
args = parser.parse_args()

DIR = os.path.dirname(os.path.realpath(__file__))
CREDENTIALS_PATH = os.path.join(DIR, 'credentials.json')

unread_prefix = args.prefix + ' '
error_prefix = ''
count_was = 0

def print_count(count, is_odd=False):
    tilde = '~' if is_odd else ''
    output = ''
    if count > 0:
        output = unread_prefix + tilde + str(count)
    else:
        output = ''
    print(output)

def update_count(count_was):
    gmail = discovery.build('gmail', 'v1', credentials=file.Storage(CREDENTIALS_PATH).get())
    labels = gmail.users().labels().get(userId='me', id='INBOX').execute()
    count = labels['messagesUnread']
    print_count(count)
    if count_was < count and count > 0:
        subprocess.run(['notify-send', 'New e-mail', 'You\'ve got new mail. Check it out.'])
    if not args.nosound and count_was < count and count > 0:
        subprocess.run(['canberra-gtk-play', '-i', 'message'])
    return count

print_count(0, True)

while True:
    try:
        if pathlib.Path(CREDENTIALS_PATH).is_file():
            count_was = update_count(count_was)
            time.sleep(10)
        else:
            print(error_prefix + 'credentials not found')
            time.sleep(2)
    except (errors.HttpError, ServerNotFoundError, OSError) as error:
        print_count(count_was, True)
        time.sleep(5)
    except client.AccessTokenRefreshError:
        print(error_prefix + 'revoked/expired credentials')
        time.sleep(5)

#!/usr/bin/env python

import urllib
import requests
from dbdriver import select

def send(dest, message):
    user = select('users', {'name': dest})[0]

    token = user['telegrambot_token']
    chatid = user['telegrambot_chatid']

    url = 'https://api.telegram.org/bot'+token+'/sendMessage?chat_id='+str(chatid)+'&text='+urllib.quote(message)
    result = requests.get(url)

    return result.status_code


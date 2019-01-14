#!/usr/bin/python

import urllib
import requests
from dbdriver import Database

class Telegram:

    def __init__(self):
        self.database = Database()

    def new(self, dest, message):
        db = self.database

        user = db.select('users', {'name': dest})
        token = user['telegrambot_token']
        chatid = user['telegrambot_chatid']

        url = 'https://api.telegram.org/bot'+token+'/sendMessage?chat_id='+chatid+'&text='+urllib.quote(message)
        result = requests.get(url)

        return result.status_code

#!/usr/bin/python

import ovh
from dbdriver import Database

class Sms:

    def __init__(self):
        self.database = Database()
        self.client = ovh.Client()

    def new(self, dest, message):
        db = self.database

        user = db.select('users', {'name': dest})
        phone = user['phone']
        account = user['sms_account']

        result = self.client.post('/sms/'+account+'/jobs',
            message=message,
            receivers=[phone],
            senderForResponse=True
        )

        return result


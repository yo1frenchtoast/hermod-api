#!/usr/bin/python

import ovh
from dbdriver import select

client = ovh.Client()

def send(dest, message):
    user = select('users', {'name': dest})[0]

    phone = user['phone']
    account = user['sms_account']

    result = client.post('/sms/'+account+'/jobs',
        message=message,
        receivers=[phone],
        senderForResponse=True
    )

    return result


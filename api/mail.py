#!/usr/bin/python

import smtplib
import configparser
from dbdriver import select

config = configparser.ConfigParser()
config.read('config.ini')
config = config['SMTP']

server = smtplib.SMTP(config['server'], int(config['port']))
server.ehlo()

if config['use_tls'] == 'yes':
    server.starttls()
server.login(config['user'], config['password'])

def send(dest, message):
    user = select('users', {'name': dest})[0]

    email = user['email']

    message = "Subject : {}\n\n".format(message)

    result = server.sendmail(config['user'], email, message)
    server.close()

    return result


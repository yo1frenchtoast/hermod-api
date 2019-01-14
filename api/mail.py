#!/usr/bin/python

import smtplib
import configparser
from dbdriver import Database

config = configparser.ConfigParser()
config.read('config.ini')

class Mail:

    def __init__(self):
        self.database = Database()

        server = smtplib.SMTP(config['SMTP']['server'], int(config['SMTP']['port']))
        server.ehlo()
        if config['SMTP']['use_tls'] == 'yes':
            server.starttls()
        server.login(config['SMTP']['user'], config['SMTP']['password'])
        self.mailserver = server

    def new(self, dest, message):
        db = self.database

        user = db.select('users', {'name': dest})
        mail = user['email']

        message = "Subject : {}\n\n".format(message)

        result = self.mailserver.sendmail(config['SMTP']['user'], mail, message)
        self.mailserver.close()

        return result

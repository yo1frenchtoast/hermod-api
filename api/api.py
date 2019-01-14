#!/usr/bin/python

import json
import datetime
import configparser
from flask import Flask, json
from flask_restful import Api, Resource, reqparse, inputs

from dbdriver import Database
from sms import Sms
from mail import Mail
from telegram import Telegram
from templates import Netwatch, Update


config = configparser.ConfigParser()
config.read('config.ini')

class RESTDB(Resource):

    def __init__(self):
        self.database = Database()
        self.endpoints = {'host': 'hosts', 'router': 'routers', 'user': 'users'}

    def get(self, name):
        db = self.database

        result = ''
        if name in self.endpoints:
            result = db.dump(self.endpoints[name])
            if result is None:
                return "Table {} not found".format(name), 404
        else:
            if hasattr(self, 'table'):
                result = db.select(self.table, {'name': name})
                if result is None:
                    return "Entity '{}' not found in table '{}'".format(name, self.table), 404
            else:
                return "Table not defined", 404

        return result, 200

    def post(self, name):
        db = self.database

        if not hasattr(self, 'table'):
            return "Table not defined", 404

        if db.select(self.table, {'name': name}) is not None:
            return "Entity '{}' already exists in table '{}'".format(name, self.table), 400

        parser = reqparse.RequestParser()
        for key in self.definition:
            parser.add_argument(key)
        args = parser.parse_args()

        data = {}
        for key in args.keys():
            data[key] = args[key]
        data['name'] = name

        result = db.insert(self.table, data)

        if result is None:
            return "Error on insert : {}".format(result), 400
        else:
            db.commit()
            result = db.select(self.table, {'name': name})
            db.close()
            return result, 201

    def put(self, name):
        db = self.database

        if not hasattr(self, 'table'):
            return "Table not defined", 404

        parser = reqparse.RequestParser()
        for key in self.definition:
            parser.add_argument(key)
        args = parser.parse_args()

        data = {}
        for key in self.definition:
            if args[key]:
                data[key] = args[key]

        result = db.update(self.table, data, {'name': name})

        if 'name' in data:
            name = data['name']

        if result is None:
            return "Error on update : {}".format(result), 400
        else:
            db.commit()
            result = db.select(self.table, {'name': name})
            db.close()
            return result, 201

    def delete(self, name):
        db = self.database

        if not hasattr(self, 'table'):
            return "Table not defined", 404

        result = db.delete(self.table, {'name': name})
        if result is None:
            return "Error on delete : {}".format(result), 400
        else:
            db.commit()
            db.close()
            return "Entity '{}' is deleted from table '{}'".format(name, self.table), 200

class Host(RESTDB):

    def __init__(self):
        self.table = 'hosts'
        self.definition = ['name', 'address', 'status', 'last_down', 'last_up', 'duration', 'witness']
        super(Host, self).__init__()

    def put(self, name):
        db = Database()

        parser = reqparse.RequestParser()
        for key in self.definition:
            parser.add_argument(key)
        parser.add_argument('email', type=inputs.boolean, default=False)
        parser.add_argument('sms', type=inputs.boolean, default=False)
        parser.add_argument('telegram', type=inputs.boolean, default=False)
        parser.add_argument('user')
        args = parser.parse_args()

        data = {}
        for key in self.definition:
            if args[key]:
                data[key] = args[key]

        host = db.select(self.table, {'name': name})

        r = ''
        if host is None:
            data['name'] = name
            if args['status'] == 'down':
                data['last_up'] = data['last_down']
            elif args['status'] == 'up':
                data['last_down'] = data['last_up']
            r = db.insert(self.table, data)
        else:
            r = db.update(self.table, data, {'name': name})

        if r is None:
            return "Error on insert/update : {}".format(r), 400
        db.commit()

        host = db.select(self.table, {'name': name})
        witness = host['witness']
        address = host['address']
        status = args['status']
        since = ''
        previous = ''

        if status == 'down':
            since = datetime.datetime.strptime(data['last_down'], '%b/%d/%Y %H:%M:%S')
            previous = datetime.datetime.strptime(host['last_up'], '%b/%d/%Y %H:%M:%S')
        elif status == 'up':
            since = datetime.datetime.strptime(data['last_up'], '%b/%d/%Y %H:%M:%S')
            previous = datetime.datetime.strptime(host['last_down'], '%b/%d/%Y %H:%M:%S')

        duration = str(since - previous)
        since = datetime.datetime.strftime(since, '%Y-%m-%d %H:%M:%S')
        message = "{} #{} host {} ({}) since {} (duration = {})".format(witness, status.upper(), address, name, since, duration)

        result = {}
        if args['email'] is True:
            mail = Mail()
            result['email'] = mail.new(args['user'], message)

        if args['sms'] is True:
            sms = Sms()
            result['sms'] = sms.new(args['user'], message)

        if args['telegram'] is True:
            telegram = Telegram()
            result['telegram'] = telegram.new(args['user'], message)

        db.update('hosts', {'duration': duration}, {'name': name})
        db.commit()

        result['host'] = db.select(self.table, {'name': name})
        db.close()

        return result, 201

class Router(RESTDB):

    def __init__(self):
        self.table = 'routers'
        self.definition = ['name', 'loopback', 'uptime', 'architecture', 'version', 'last_seen']
        super(Router, self).__init__()

class User(RESTDB):

    def __init__(self):
        self.table = 'users'
        self.definition = ['name', 'email', 'phone', 'sms_account', 'telegrambot_token', 'telegrambot_chatid']
        super(User, self).__init__()

class HostTemplate(Resource):

    def __init__(self):
        self.template = Netwatch()

    def post(self, address):
        template = self.template

        parser = reqparse.RequestParser()
        parser.add_argument('email')
        parser.add_argument('sms')
        parser.add_argument('telegram')
        parser.add_argument('user')
        args = parser.parse_args()

        email = True if args['email'] else False
        sms = True if args['sms'] else False
        telegram = True if args['telegram'] else False
        user = args['user']

        if (email or sms or telegram) and user is None:
            return "Notifications is set, user must be specified", 400

        host = address
        server = "{}://{}:{}".format(config['API']['protocol'], config['API']['url'], config['API']['port'])
        notifications = "email={}&sms={}&telegram={}".format(email, sms, telegram)

        result = {}
        for status in ['down', 'up']:
            result[status] = template.generate(host, status , server, notifications, user)

        return result, 200

if __name__ == "__main__":
    app = Flask(__name__)

    api = Api(app)
    api.add_resource(RESTDB, '/<string:name>')
    api.add_resource(Host, '/host/<string:name>')
    api.add_resource(HostTemplate, '/host/template/<string:address>')
    api.add_resource(Router, '/router/<string:name>')
    api.add_resource(User, '/user/<string:name>')

    app.run(host=config['API']['host'], port=config['API']['port'], debug=True)

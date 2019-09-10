#!/usr/bin/env python

import json
import datetime
import configparser
from rq import Queue
from redis import Redis
from flask import Flask, json
from flask_restful import Api, Resource, reqparse, inputs

import sms
import mail
import telegram
import dbdriver as db
from templates import Netwatch, Update

config = configparser.ConfigParser()
config.read('config.ini')

q = Queue(connection=Redis(config['REDIS']['host'], config['REDIS']['port']))

class RESTDB(Resource):

    def __init__(self):
        self.endpoints = {'host': 'hosts', 'router': 'routers', 'user': 'users'}

    def get(self, name):
        result = ''
        if name in self.endpoints:
            job = q.enqueue(db.dump, args=(self.endpoints[name],))
            while job.result is None:
                pass
            result, error = job.result

            if result is None:
                return "Error on dump : {}".format(error), 500

        else:
            if hasattr(self, 'table'):
                job = q.enqueue(db.select, args=(self.table, {'name': name},))
                while job.result is None:
                    pass
                result, error = job.result

                if result is None:
                    return "Entity '{}' not found in table '{}' : {}".format(name, self.table, error), 404

            else:
                return "Table not defined".format(name), 404

        return result, 200

    def post(self, name):
        if not hasattr(self, 'table'):
            return "Table not defined", 404

        job = q.enqueue(db.select, args=(self.table, {'name': name},))
        while job.result is None:
            pass
        result, error = job.result

        if result is not None:
            if error is not None:
                return "Error on select : {}".format(error), 500

            return "Entity '{}' already exists in table '{}'".format(name, self.table), 400

        parser = reqparse.RequestParser()
        for key in self.definition:
            parser.add_argument(key)
        args = parser.parse_args()

        data = {}
        for key in args.keys():
            data[key] = args[key]
        data['name'] = name

        job = q.enqueue(db.insert, args=(self.table, data),)
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            return "Error on insert : {}".format(error), 400

        else:
            job = q.enqueue(db.select, args=(self.table, {'name': name},))
            while job.result is None:
                pass
            result, error = job.result

            return result, 201

    def put(self, name):
        if not hasattr(self, 'table'):
            return "Table not defined", 404

        job = q.enqueue(db.select, args=(self.table, {'name': name},))
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            if error is not None:
                return "Error on select : {}".format(error), 500

            return "Entity '{}' does not exist in table '{}'".format(name, self.table), 400

        parser = reqparse.RequestParser()
        for key in self.definition:
            parser.add_argument(key)
        args = parser.parse_args()

        data = {}
        for key in self.definition:
            if args[key]:
                data[key] = args[key]

        job = q.enqueue(db.update, args=(self.table, {'name': name}, data,))
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            return "Error on update : {}".format(error), 400

        else:
            if 'name' in data:
                name = data['name']

            job = q.enqueue(db.select, args=(self.table, {'name': name},))
            while job.result is None:
                pass
            result, error = job.result

            return result, 201

    def delete(self, name):
        if not hasattr(self, 'table'):
            return "Table not defined", 404

        job = q.enqueue(db.select, args=(self.table, {'name': name},))
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            if error is not None:
                return "Error on select : {}".format(error), 500

            return "Entity '{}' does not exist in table '{}'".format(name, self.table), 400

        job = q.enqueue(db.delete, args=(self.table, {'name': name},))
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            return "Error on delete : {}".format(error), 500
        else:
            return "Entity '{}' has been deleted from table '{}'".format(name, self.table), 200

class Host(RESTDB):

    def __init__(self):
        self.table = 'hosts'
        self.definition = ['name', 'address', 'mac', 'status', 'last_down', 'last_up', 'duration', 'witness']
        super(Host, self).__init__()

    def put(self, name):
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

        job = q.enqueue(db.select, args=(self.table, {'name': name},))
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            if error is not None:
                return "Error on select : {}".format(error), 400

            data['name'] = name
            if args['status'] == 'down':
                data['last_up'] = data['last_down']
            elif args['status'] == 'up':
                data['last_down'] = data['last_up']

            job = q.enqueue(db.insert, args=(self.table, data,))
            while job.result is None:
                pass
            result, error = job.result

            if result is None:
                return "Error on insert : ".format(error), 500

        else:
            job = q.enqueue(db.update, args=(self.table, {'name': name}, data,))
            while job.result is None:
                pass
            result, error = job.result

            if result is None:
                return "Error on update : {}".format(error), 500

        job = q.enqueue(db.select, args=(self.table, {'name': name},))
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            if error is not None:
                return "Error on select : {}".format(error), 500

            return "Entity '{}' does not exist in table '{}'".format(name, self.table), 400

        host = result

        witness = host['witness']
        address = host['address']
        status = args['status']
        since = ''
        previous = ''

        if status == 'down':
            since = datetime.datetime.strptime(data['last_down'], '%b/%d/%Y %H:%M:%S')
            if host['last_up'] is None:
                previons = since
            else:
                previous = datetime.datetime.strptime(host['last_up'], '%b/%d/%Y %H:%M:%S')
        elif status == 'up':
            since = datetime.datetime.strptime(data['last_up'], '%b/%d/%Y %H:%M:%S')
            if host['last_down'] is None:
                previous = since
            else:
                previous = datetime.datetime.strptime(host['last_down'], '%b/%d/%Y %H:%M:%S')

        duration = str(since - previous)
        else:
            since = datetime.datetime.strftime(since, '%Y-%m-%d %H:%M:%S')
        message = "{} #{} host {} ({}) since {} (duration = {})".format(witness, status.upper(), address, name, since, duration)

        result = {}
        if args['email'] is True:
            job = q.enqueue(mail.send, args=(args['user'], message,))
            while job.result is None:
                pass
            result['email'] = job.result

        if args['sms'] is True:
            job = q.enqueue(sms.send, args=(args['user'], message,))
            while job.result is None:
                pass
            result['sms'] = job.result

        if args['telegram'] is True:
            job = q.enqueue(telegram.send, args=(args['user'], message,))
            while job.result is None:
                pass
            result['telegram'] = job.result

        job = q.enqueue(db.update, args=('hosts', {'name': name}, {'duration': duration},))
        while job.result is None:
            pass
        result, error = job.result

        if result is None:
            return "Error on update : {}".format(error), 500

        job = q.enqueue(db.select, args=(self.table, {'name': name},))
        while job.result is None:
            pass
        result, error = job.result

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

    def get(self, address):
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
        notifications = {'email': email, 'sms': sms, 'telegram': telegram}

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


#!/usr/bin/python

import json
import sqlite3

class Database:

    def __init__(self):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        try:
            self.connection = sqlite3.connect('data.db')
        except Error as e:
            print(e)

        self.connection.row_factory = dict_factory
        self.conn_cursor = self.connection.cursor()

    def dump(self, table):
        cursor = self.conn_cursor

        query = "SELECT * FROM {}".format(table)

        cursor.execute(query)
        result = cursor.fetchall()

        return result

    def select(self, table, element):
        cursor = self.conn_cursor

        column = element.keys()[0]
        value = element.values()[0]

        query = "SELECT * FROM {} WHERE {}='{}'".format(table, column, value)

        cursor.execute(query)
        result = cursor.fetchone()

        return result

    def insert(self, table, data):
        cursor = self.conn_cursor

        columns = ', '.join(data.keys())
        placeholders = ':'+', :'.join(data.keys())

        query = "INSERT INTO {}({}) VALUES ({})".format(table, columns, placeholders)

        result = cursor.execute(query, data)

        return result

    def delete(self, table, element):
        cursor = self.conn_cursor

        column = element.keys()[0]
        value = element.values()[0]

        query = "DELETE FROM {} WHERE {}='{}'".format(table, column, value)

        result = cursor.execute(query)

        return result

    def update(self, table, data, element):
        cursor = self.conn_cursor

        placeholders = ''
        for key in data.keys():
            placeholders += key+'=:'+key+', '
        placeholders = placeholders[:-2]
        column = element.keys()[0]
        value = element.values()[0]

        query = "UPDATE {} SET {} WHERE {}='{}'".format(table, placeholders, column, value)

        result = cursor.execute(query, data)

        return result

    def commit(self):
        result = ''

        result = self.connection.commit()

        return result

    def close(self):
        self.connection.close()


import json
import config
import mysql.connector

config = config.get('db')

def dump(table):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM {}".format(table)

    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result, None
    except mysql.connector.Error as e:
        print (e)
        return None, e.msg
    finally:
        cursor.close()
        connection.close()

def select(table, element):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    column = list(element.keys())[0]
    value = list(element.values())[0]

    query = "SELECT * FROM {} WHERE {}='{}'".format(table, column, value)

    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result, None
    except mysql.connector.Error as e:
        print (e)
        return None, e.msg
    finally:
        cursor.close()
        connection.close()

def insert(table, data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    columns = ', '.join(data.keys())
    placeholders = ', '.join(["%s"]*len(data))

    query = "INSERT INTO {}({}) VALUES ({})".format(table, columns, placeholders)

    try:
        cursor.execute(query, data.values())
        connection.commit()
        return "Data inserted successfully", None
    except mysql.connector.Error as e:
        print (e)
        return None, e.msg
    finally:
        cursor.close()
        connection.close()

def delete(table, element):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    column = list(element.keys())[0]
    value = list(element.values())[0]

    query = "DELETE FROM {} WHERE {}='{}'".format(table, column, value)

    try:
        cursor.execute(query)
        connection.commit()
        return "Data deleted successfully", None
    except mysql.connector.Error as e:
        print (e)
        return None, e.msg

    finally:
        cursor.close()
        connection.close()

def update(table, element, data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    placeholders = ''
    for key in data.keys():
        placeholders += "{}=\"{}\", ".format(key, data[key])
    placeholders = placeholders[:-2]
    column = list(element.keys())[0]
    value = list(element.values())[0]

    query = "UPDATE {} SET {} WHERE {}='{}'".format(table, placeholders, column, value)

    try:
        cursor.execute(query)
        connection.commit()
        return "Data updated successfully", None
    except mysql.connector.Error as e:
        print (e)
        return None, e.msg
    finally:
        cursor.close()
        connection.close()

'''subscribe to mqtt broker and store msgs in sqlite'''

import datetime
import json
import sqlite3
import time

import paho.mqtt.client as mqtt


CFG = {}
CFG['host'] = 'localhost'
CFG['port'] = 1883
CFG['db_name'] = 'climatelivingroom.db'
CFG['topic'] = 'climate/livingroom'


def store_data(db_name, device_timestamp, humidity, temperature):
    '''log device timestamp, humidity, temperature to db'''

    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS SensorValues(
                      ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                      entered DATETIME DEFAULT CURRENT_TIMESTAMP,
                      device DATETIME,
                      humidity REAL,
                      temperature REAL)''')
    db.commit()

    db.execute('INSERT INTO SensorValues(device, humidity, temperature) VALUES(?,?,?)',
                (device_timestamp, humidity, temperature))
    db.commit()
    db.close()


def on_connect(client, userdate, flags, rc):
    client.subscribe(CFG['topic'])


def on_message(client, userdata, message):
    msg = json.loads((message.payload).decode('utf-8'))

    ts = datetime.datetime.strptime(msg['tsp'], '%Y%m%d%H%M%S')
    temperature = msg['tmp']
    humidity = msg['hmd']

    store_data(CFG['db_name'], ts, humidity, temperature)


def mqtt_sub(host, port):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(host, port)
    client.loop_forever()


if __name__ == '__main__':
    mqtt_sub(CFG['host'], CFG['port'])

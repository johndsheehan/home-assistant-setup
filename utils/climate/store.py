'''subscribe to mqtt broker and store msgs in sqlite'''

import datetime
import json
import sqlite3
import sys
import time

import paho.mqtt.client as mqtt


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


def on_connect(client, userdata, flags, rc):
    '''subscribe to topic given by userdata dictionary'''

    client.subscribe(userdata['topic'])


def on_message(client, userdata, message):
    '''parse msg and store in db'''
    msg = json.loads((message.payload).decode('utf-8'))

    ts = datetime.datetime.strptime(msg['tsp'], '%Y%m%d%H%M%S')
    temperature = msg['tmp']
    humidity = msg['hmd']

    store_data(userdata['db_name'], ts, humidity, temperature)


def mqtt_sub(cfg):
    '''create mqtt connection'''
    client = mqtt.Client(userdata=cfg)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(cfg['host'], cfg['port'])
    client.loop_forever()


def main(config_file):
    try:
        with open(config_file) as cfile:
            cfg = json.load(cfile)

        mqtt_sub(cfg)
    except IOError:
        print('failed to open: {}'.format(config_file))
    except ValueError:
        print('failed to parse: {}'.format(config_file))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('usage: python {} <config.json>'.format(sys.argv[0]))

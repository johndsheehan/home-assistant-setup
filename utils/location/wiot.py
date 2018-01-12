'''relay data from Watson IoT to local broker'''

import json
import logging
import sqlite3
import sys
import ibmiotf.application

import paho.mqtt.client as mqtt


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] -> %(message)s')


def store_data(msg):
    try:
        payload = json.loads(msg.payload)

        longitude = payload['lon']
        latitude = payload['lat']
        altitude = payload['alt']
        accuracy = payload['acc']

        db = sqlite3.connect('location.db')
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS Locations(
                          ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                          entered DATETIME DEFAULT CURRENT_TIMESTAMP,
                          longitude REAL,
                          latitude REAL,
                          accuracy REAL,
                          altitude REAL)''')
        db.commit()

        db.execute('INSERT INTO Locations(longitude, latitude, accuracy, altitude) VALUES(?, ?, ?, ?)', (longitude, latitude, accuracy, altitude))
        db.commit()
        db.close()
    except:
        return False

    return True


def wiot_cb(msg):

    try:
        store_data(msg)
        client_local.publish('owntracks/user/dev', msg.payload)
    except:
        print('watson iot callback failed')


def main(config_file):

    with open(config_file) as f:
        cfg = json.load(f)

    cfg_local = cfg['local']
    cfg_wiot = cfg['wiot']

    client_local = mqtt.Client()
    client_local.connect(cfg_local['host'], cfg_local['port'], 60)

    client_wiot = ibmiotf.application.Client(cfg_wiot)
    client_wiot.connect()

    client_wiot.deviceEventCallback = wiot_cb
    client_wiot.subscribeToDeviceEvents(event=cfg_wiot['event'])

    client_local.loop_forever()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('usage: {} <config_file>'.format(sys.argv[0]))

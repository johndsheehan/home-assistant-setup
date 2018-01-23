'''relay data from Watson IoT to local broker'''

import json
import logging
import sqlite3
import os
import ssl
import sys

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


def on_connect(client, userdata, flags, rc):

    topic = 'iot-2/type/+/id/+/evt/location/fmt/+'
    client.subscribe(topic)


def on_message(client, userdata, msg):

    try:
        print(msg.payload)
        store_data(msg)
        userdata['local'].publish('owntracks/user/dev', msg.payload)
    except:
        print('relay callback failed')


def on_subscribe(client, userdata, mid, qos):

    print('subscribed')


def connect_local(config, userdata=None):

    client = mqtt.Client('location.local', userdata=userdata, clean_session=False)
    client.connect(config['host'], config['port'], 60)

    return client


def connect_relay(config, userdata):

    orgid = config['auth-key'].split('-')[1]

    client_id = 'a' + ':' + orgid + ':' + config['id']
    client = mqtt.Client(client_id, userdata=userdata, clean_session=False)

    username = config['auth-key']
    password = config['auth-token']
    client.username_pw_set(username, password)

    ca_file = "./messaging.pem"
    client.tls_set(ca_certs=ca_file, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

    address = orgid + '.messaging.internetofthings.ibmcloud.com' 

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe

    client.connect(address, 8883)
    client.loop_start()

    return client


def main(config_file):

    with open(config_file) as f:
        cfg = json.load(f)

    cfg_local = cfg['local']
    cfg_relay = cfg['relay']

    client_local = connect_local(cfg_local)

    userdata = {"local": client_local, "relay": cfg_relay}
    client_relay = connect_relay(cfg_relay, userdata=userdata)

    client_local.loop_forever()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('usage: {} <config_file>'.format(sys.argv[0]))

import dht
import machine
import time

from umqtt.robust import MQTTClient


def sub_cb(topic, msg):
    print(msg)


def mqtt_msg(config):
    host = config['host']
    port = config['port']
    mqtt_id = config['mqtt_id']
    topic = config['topic']
    delay = config['delay']

    client = MQTTClient(mqtt_id, host, port=port)
    client.connect()

    d = dht.DHT22(machine.Pin(4))
    try:
        '''required or a timeout error occurs !?'''
        d.measure()
    except:
        print('d.measure() failed')

    while True:
        try:
            d.measure()
            t = time.localtime()

            timestamp = '{}{:02d}{:02d}{:02d}{:02d}{:02d}'.format(t[0], t[1], t[2], t[3], t[4], t[5])
            temperature = d.temperature()
            humidity = d.humidity()

            m = '{{"tsp":"{}", "tmp":{:02.2f}, "hmd":{:02.2f}}}'.format(timestamp, temperature, humidity)

            client.publish(topic=topic, msg=m)
        except:
            print('d.measure() failed')

        time.sleep(delay)


if __name__ == '__main__':
    try:
        with open('./esp8266.cfg') as f:
            import ujson
            cfg = ujson.loads(f.read())
    
        mqtt_msg(cfg['mqtt'])
    except:
        print('failed to start mqtt msg')

import dht
import machine
import time

from umqtt.robust import MQTTClient


def sub_cb(topic, msg):
    print(msg)


def mqtt_msg(topic, delay):
    client = MQTTClient('esp8266', 'flatpi.lan', port=1883)
    client.connect()
 
    d = dht.DHT22(machine.Pin(4))
    try:
        '''required or a timeout error occurs !?'''
        d.measure()
    except:
        pass

    while True:
        d.measure()
        t = time.localtime()

        timestamp = '{}{:02d}{:02d}{:02d}{:02d}{:02d}'.format(t[0], t[1], t[2], t[3], t[4], t[5])
        temperature = d.temperature()
        humidity = d.humidity()

        m = '{{"tsp":"{}", "tmp":{:02.2f}, "hmd":{:02.2f}}}'.format(timestamp, temperature, humidity)

        client.publish(topic=topic, msg=m)
        time.sleep(delay)


if __name__ == '__main__':
    try:
        with open('./esp8266.cfg') as f:
            import ujson
            cfg = ujson.loads(f.read())
    
        mqtt_msg(cfg["topic"], cfg["delay"])
    except:
        print('failed to start mqtt msg')

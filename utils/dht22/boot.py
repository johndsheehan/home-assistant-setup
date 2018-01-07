# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import gc
import webrepl
webrepl.start()
gc.collect()

import time


def connect_ap(essid, psk):
    '''connect to wireless access point'''
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)

        sta_if.connect(essid, psk)

        count = 0
        while not sta_if.isconnected() and count < 5:
            count = count + 1
            time.sleep(count)

        if sta_if.isconnected():
            print('network config:', sta_if.ifconfig())
            # disconnect the access point
            ap_if = network.WLAN(network.AP_IF)
            ap_if.active(False)

            try:
                # set time from ntp
                time.sleep(5)
                from ntptime import settime
                settime()
            except:
                print('failed to set time')
        else:
            print('failed to connect')
            sta_if.active(False)


try:
    with open('./esp8266.cfg') as f:
        import ujson
        cfg = ujson.loads(f.read())
    
    connect_ap(cfg["essid"], cfg["psk"])
except:
    print('unable to parse config/connect to ap')

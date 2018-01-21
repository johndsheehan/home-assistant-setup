#!/bin/bash

if [ -z $1 ] ; then
    echo "usage: ./update.sh <config file>"
    exit 1
fi

set -x

ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put $1 esp8266.cfg

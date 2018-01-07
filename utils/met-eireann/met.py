'''connect to met eireann and fetch current radar image'''
import datetime
import logging
import os
import sys

import cv2
import imageio
import requests

import numpy as np

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)


def fetch(timestamp):
    '''fetch met eireann radar image'''
    LOGGER.debug('fetch timestamp %s', timestamp)

    url = 'https://www.met.ie/weathermaps/radar2/WEB_radar5_' + timestamp + '.png'
    resp = requests.get(url)
    if resp.status_code != requests.codes.ok:
        LOGGER.error('request failed: %s', resp.status_code)
        return None

    return resp.content


def files_fetch(dirname, ending='_met_eireann.png'):
    '''fetch filenames from directory which contain ending'''
    LOGGER.debug('files fetch in %s %s', dirname, ending)

    files_all = os.listdir(dirname)

    files = [os.path.abspath(f) for f in files_all if f.endswith(ending)]

    files.sort()

    return files


def files_remove(files):
    '''delete list of files'''
    for fle in files:
        os.remove(fle)


def gif_write(name, files):
    '''write gif to file'''
    LOGGER.debug('gif write %s %s', name, files)

    with imageio.get_writer(name, mode='I', duration=0.5, loop=1) as writer:
        for fle in files[:-1]:
            image = imageio.imread(fle)
            writer.append_data(image)

        image = imageio.imread(files[-1])
        writer.append_data(image)
        writer.append_data(image)
        writer.append_data(image)
        writer.append_data(image)


def img_write(img, filename):
    '''write image to file'''
    LOGGER.debug('img write %s', filename)

    with open(filename, 'wb') as ifile:
        ifile.write(img)


def img_text_add(img_buf, lines, xpos=10, ypos=30):
    '''add lines of text to image'''
    tmp = np.fromstring(img_buf, dtype='uint8')
    img = cv2.imdecode(tmp, cv2.IMREAD_UNCHANGED)

    font = cv2.FONT_HERSHEY_COMPLEX
    for i, line in enumerate(lines, 1):
        cv2.putText(img, line, (xpos, ypos * i), font, 0.75, (255, 255, 255), 2)

    _, buf = cv2.imencode('.png', img)

    return bytearray(buf)


def round15(value):
    '''return nearest multiple of 15 less than value'''
    LOGGER.debug('round15 %d', value)

    return value // 15 * 15


def timestrings():
    '''return required timestamp strings'''
    ts_now = datetime.datetime.now()
    minute = round15(ts_now.minute)
    ts_str = ts_now.strftime('%Y%m%d%H') + '{:02d}'.format(minute)

    date_str = ts_now.strftime('%Y-%m-%d')
    time_str = ts_now.strftime('%H:') + '{:02d}'.format(minute)

    return (ts_str, date_str, time_str)


def main():
    '''entry point'''
    timestamp, date_str, time_str = timestrings()

    LOGGER.debug('%s %s %s', timestamp, date_str, time_str)
    img = fetch(timestamp)
    if img is None:
        sys.exit(1)

    img = img_text_add(img, [date_str, time_str])

    dir_name = os.path.abspath('.')
    filename = dir_name + '/' + timestamp + '_met_eireann.png'
    img_write(img, filename)

    files = files_fetch(dir_name, '_met_eireann.png')
    gif_write(dir_name + '/' + 'radar.gif', files[-10:])

    count = len(files) - 10
    if count > 0:
        files_remove(files[:count])


if __name__ == '__main__':
    main()

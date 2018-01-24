'''query a sqlite db, and serve a generated plot'''

import os
import sqlite3

from datetime import datetime
from dateutil.relativedelta import relativedelta

import plotly.offline as offline
import plotly.graph_objs as gob

from flask import Flask, jsonify, render_template

APP = Flask(__name__)


DB = {'bedroom': './climatebedroom.db',
      'livingroom': './climatelivingroom.db'}


RANGES = {'last-hour': relativedelta(hours=1),
          'last-3hours': relativedelta(hours=3),
          'last-6hours': relativedelta(hours=6),
          'last-12hours': relativedelta(hours=12),
          'last-day': relativedelta(days=1),
          'last-3days': relativedelta(days=3),
          'last-week': relativedelta(weeks=1),
          'last-2weeks': relativedelta(weeks=1),
          'last-month': relativedelta(months=1),
          'last-2months': relativedelta(months=2),
          'last-3months': relativedelta(months=3)}

RANGE_DEFAULT = 'last-3months'


@APP.route("/")
def index():
    '''return chart with default range'''

    data = fetch()
    plot_gen(data)

    return render_template("climate.html")


@APP.route('/data/<room>/<data_range>')
def data_json(room, data_range):
    '''return values in json for given room & range'''

    db = DB.get(room, './climatelivingroom.db')
    return jsonify(fetch(db, data_range, -1))


@APP.route('/chart/<room>/<data_range>')
def chart(room, data_range):
    '''return chart for given room & range, default range otherwise'''

    db = DB.get(room, './climatelivingroom.db')

    data = fetch(db, data_range)
    plot_gen(data)

    return render_template("climate.html")


def fetch(db_name, data_range=RANGE_DEFAULT, maximum=288):
    '''return data for given range, default otherwise, up to maximum rows'''

    if data_range not in RANGES:
        data_range = RANGE_DEFAULT

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    stmt = query_stmt(data_range)
    cur.execute(stmt)

    rows = cur.fetchall()

    lst = []
    for row in rows:
        tsp, hum, tmp = row
        lst.append({'timestamp':tsp, 'humidity':hum, 'temperature':tmp})

    if maximum < 0:
        '''return all values'''
        return lst

    length = len(lst)
    if length > maximum:
        '''if number of rows found is large, filter'''
        step = (length // maximum) + 1
        lst = lst[::-step]
        lst.reverse()

    return lst


def query_stmt(data_range):
    '''generate an sqlite query'''
    delta_time = RANGES[data_range]

    start = (datetime.now() - delta_time).strftime('%Y-%m-%d %H:%M:%S')
    finish = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    select = 'select entered, humidity, temperature from SensorValues where '
    stmt = select + "entered between '{start}' and '{finish}'".format(start=start, finish=finish)

    return stmt


def plot_gen(data):
    '''use plotly to generate a html page (png not possible offline)'''

    timestamps = [d['timestamp'] for d in data]
    temperatures = [d['temperature'] for d in data]
    humidities = [d['humidity'] for d in data]

    trace1 = gob.Scatter(x=timestamps,
                         y=temperatures,
                         mode='lines',
                         name='temperature',
                         line=dict(color=('rgb(255, 0, 0)'), shape='spline'))

    trace2 = gob.Scatter(x=timestamps,
                         y=humidities,
                         mode='lines',
                         name='humidity',
                         line=dict(color=('rgb(0, 255, 0)'), shape='spline'),
                         yaxis='y2')

    data = [trace1, trace2]

    yaxis_temperature = dict(title='temperature',
                             side='right',
                             titlefont=dict(color='rgb(255, 0, 0)'),
                             tickfont=dict(color='rgb(255, 0, 0)')
                            )

    yaxis_humidity = dict(title='humidity',
                          side='left',
                          titlefont=dict(color='rgb(0, 255, 0)'),
                          tickfont=dict(color='rgb(0, 255, 0)'),
                          overlaying='y'
                         )

    layout = gob.Layout(title='Climate',
                        yaxis=yaxis_temperature,
                        yaxis2=yaxis_humidity
                       )

    fig = dict(data=data, layout=layout)
    offline.plot(fig, filename='./templates/climate.html', auto_open=False)


if __name__ == '__main__':
    if not os.path.exists('./templates'):
        '''directory to store generated plots'''
        os.makedirs('./templates')

    APP.run(host='0.0.0.0', port=5001)

from flask import Flask, send_file

APP = Flask(__name__)

@APP.route('/radar')
def radar():
    return send_file('./radar.gif', mimetype='image/gif')


if __name__ == '__main__':
    APP.run(host='127.0.0.1', port=5050, debug=False)

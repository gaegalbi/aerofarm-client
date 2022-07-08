import datetime
import random
import time
import socket
import getmac
from flask import Flask, request, jsonify, make_response
import requests
from apscheduler.schedulers.background import BackgroundScheduler

with open('ip.txt', 'r') as file:
    ip = file.read()

spring_server = 'http://' + ip + ':8080'
uuid = 'bcec74a4-ea3f-4b78-a6ed-40f789643036'

app = Flask(__name__)


def send_ip_mac():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    s.close()

    data = {
        "uuid": uuid,
        "ipAddress": ip_address,
        "macAddress": getmac.get_mac_address()
    }

    headers = {'Content-Type': 'application/json; charset=utf-8'}
    requests.post(spring_server + '/test', json=data, headers=headers)


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=send_ip_mac, trigger="interval", day=1, next_run_time=datetime.datetime.now())
# scheduler.start()


@app.route('/')
def hello_world():  # put application's code here
    response = requests.get(spring_server + '/test')

    row = response.json()

    return make_response(jsonify(row), 200)


@app.route('/test', methods=['POST'])
def test():
    print(request.is_json)
    params = request.get_json()
    print(params)

    return make_response('', 200)


@app.route('/test2', methods=['POST'])
def test2():
    time.sleep(random.uniform(1, 3))

    uuid = request.form['uuid']
    print(uuid)

    data = {
        'online': bool(random.getrandbits(1)),
        'temperature': random.randint(20, 40),
        'humidity': random.randint(0, 100),
        'brightness': random.randint(0, 100),
        'fertilizer': random.randint(0, 1000)
    }

    return make_response(jsonify(data), 200)


if __name__ == '__main__':
    app.run()

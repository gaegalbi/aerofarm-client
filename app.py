import datetime
import random
import socket
import getmac
from flask import Flask, request, jsonify, make_response
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import serial

with open('ip.txt', 'r') as file:
    ip = file.read()

spring_server = 'http://' + ip + ':8080'
print(spring_server)
uuid = 'bcec74a4-ea3f-4b78-a6ed-40f789643036'
arduino = serial.Serial('/dev/cu.usbmodem101', 9600)

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
    requests.post(spring_server + '/api/devices/update', json=data, headers=headers)


scheduler = BackgroundScheduler()
scheduler.add_job(func=send_ip_mac, trigger="interval", days=1, next_run_time=datetime.datetime.now())
scheduler.start()


@app.route('/')
def hello_world():  # put application's code here
    response = requests.get(spring_server + '/test')

    row = response.json()

    return make_response(jsonify(row), 200)


@app.route('/test', methods=['POST'])
def test():

    params = request.get_json()
    print(params)

    if params['ledOn']:
        arduino.write(b"led_on")
    else:
        arduino.write(b"led_off")

    return make_response('', 200)


@app.route('/test2', methods=['POST'])
def test2():
    reqeust_uuid = request.form['uuid']
    print(reqeust_uuid)

    data = {
        'online': bool(random.getrandbits(1)),
        'temperature': random.randint(20, 40),
        'humidity': random.randint(0, 100),
        'brightness': random.randint(0, 100),
        'fertilizer': random.randint(0, 1000)
    }

    return make_response(jsonify(data), 200)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5111
    )

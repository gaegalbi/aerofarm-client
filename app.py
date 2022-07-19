import datetime
import random
import socket
import getmac
from flask import Flask, request, jsonify, make_response
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import serial
import json

with open('ip.txt', 'r') as file:
    ip = file.read()

spring_server = 'http://' + ip + ':8080'
print(spring_server)
# uuid = '2add5557-d6e2-4fb8-94eb-da182db84036'  # AWS MARIA
uuid = 'bcec74a4-ea3f-4b78-a6ed-40f789643036'  # LOCAL TEST

try:
    arduino = serial.Serial('/dev/ttyACM0', 9600)
except serial.SerialException:
    arduino = serial.Serial('/dev/ttyACM1', 9600)

app = Flask(__name__)


def send_ip_mac():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]  # 공유기로 연결됬다면 공인 아이피 주소의 입력이 필요함
    # ip_address = requests.get("https://api.ipify.org").text # 외부 아이피 주소 가져오기
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


@app.route('/device-setting', methods=['POST'])
def device_setting():
    params = request.get_json()
    print(params)

    if params['ledOn']:
        arduino.write(b"led_on")
    else:
        arduino.write(b"led_off")

    return make_response('', 200)


@app.route('/device-info', methods=['POST'])
def device_info():
    reqeust_uuid = request.form['uuid']
    print(reqeust_uuid)

    arduino.write(b"read_value")
    res = arduino.readline()
    json_data = json.loads(res)

    data = {
        'online': bool(random.getrandbits(1)),
        'temperature': random.randint(20, 40),
        'humidity': random.randint(0, 100),
        'brightness': random.randint(0, 100),
        'fertilizer': random.randint(0, 1000)
    }

    return make_response(jsonify(json_data), 200)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5111
    )

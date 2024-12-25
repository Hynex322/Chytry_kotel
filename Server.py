from flask import Flask, render_template, url_for
import multiprocessing
#from Temperature import TemperatureSensor

app = Flask('Kotel server')

sensor = None
tmp_history = []

@app.route("/")
def index():
    global history
    return render_template('main.html', temp=sensor.get_temperature(), len=len(tmp_history[:]), history=tmp_history[:])

@app.route("/temp")
def temp():
    return str(sensor.get_temperature())
    
    
@app.route("/reboot")
def reboot_server():
    import os
    os.system('reboot')
    
@app.route("/shutdown")
def shutdown_server():
    import os
    os.system('shutdown now')

def run(tmp_sensor, ip, history):
    global sensor, tmp_history
    tmp_history = history
    sensor = tmp_sensor

    app.run(host='0.0.0.0', port=80, debug=False)

def run_async(sensor, ip, history):
    p = multiprocessing.Process(target=run, args=(sensor, ip, history, ))
    p.start()


def remote_worker(sensor, url, key):
    import requests, time
    delay = 1

    while True:
        try:
            requests.post(url, auth=('rpi-controll', key), data={'temp': sensor.get_temperature()})
        except:
            print("[REMOTE WORKER]: Data upload failed!")
        time.sleep(delay)

def run_remote(sensor, url, key):
    p = multiprocessing.Process(target=remote_worker, args=(sensor, url, key,))
    p.start()

from flask import Flask, redirect, render_template, url_for
import multiprocessing
import os
#from Temperature import TemperatureSensor

app = Flask('Kotel server')

sensor = None
tmp_history = []
max_Temp = None

@app.route("/")
def index():
    global history, max_Temp
    return render_template('main.html', temp=sensor.get_temperature(), len=len(tmp_history[:]), history=tmp_history[:], maxTemp=max_Temp[0])

@app.route("/temp")
def temp():
    return str(sensor.get_temperature())

@app.route("/maxTemp")   
def maxTemp():
    global max_Temp
    return str(max_Temp[0])
    
@app.route("/reboot")
def reboot_server():
    os.system(' (sleep 1 && reboot) &) ')
    return redirect("/")

@app.route("/update")
def update():
    os.system('git pull &')
    return redirect("/")
    
@app.route("/shutdown")
def shutdown_server():
    os.system('(sleep 1 && shutdown now &)')
    return redirect("/")

def run(tmp_sensor, ip, history, maxTemp):
    global sensor, tmp_history, max_Temp
    tmp_history = history
    sensor = tmp_sensor
    max_Temp = maxTemp

    app.run(host='0.0.0.0', port=80, debug=False)

def run_async(sensor, ip, history, maxTemp):
    p = multiprocessing.Process(target=run, args=(sensor, ip, history, maxTemp ))
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

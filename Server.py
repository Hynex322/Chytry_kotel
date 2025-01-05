from flask import Flask, redirect, render_template, url_for
import multiprocessing
import os
#from Temperature import TemperatureSensor

app = Flask('Kotel server')

sensor = None
tmp_history = []
server_maxTemp = 0

@app.route("/")
def index():
    global history, max_Temp
    return render_template('main.html', temp=sensor.get_temperature(), len=len(tmp_history[:]), history=tmp_history[:], maxTemp=server_maxTemp)


@app.route("/temp")
def temp():
    return str(sensor.get_temperature())

@app.route("/maxTemp")   
def maxTemp():
    global server_maxTemp
    with open("server.txt", 'a') as filelog:
        if server_maxTemp < sensor.get_temperature():
            text="max teplota:", str(server_maxTemp)," nahrazena: ", str(sensor.get_temperature())
            filelog.write(text)
            server_maxTemp=sensor.get_temperature()
    text="max teplota je: ", str(server_maxTemp)
    filelog.write(text)
    return str(server_maxTemp)
    
@app.route("/reboot")
def reboot_server():
    os.system(' (sleep 1 && reboot) & ')
    return redirect("/")

@app.route("/update")
def update():
    os.system('sudo git pull &')
    return redirect("/")
    
@app.route("/shutdown")
def shutdown_server():
    os.system('(sleep 1 && shutdown now &)')
    return redirect("/")

def run(tmp_sensor, ip, history):
    global sensor, tmp_history
    tmp_history = history
    sensor = tmp_sensor
    
    app.run(host='0.0.0.0', port=80, debug=False)

def run_async(sensor, ip, history):
    p = multiprocessing.Process(target=run, args=(sensor, ip, history))
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

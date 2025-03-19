from flask import Flask, redirect, render_template, url_for
import multiprocessing
import os
import subprocess
#from Temperature import TemperatureSensor

app = Flask('Kotel server')

sensor = None
server_history = None  # Sdílená historie
server_maxTemp = None
server_averageTemp = None

@app.route("/")
def index():
    global server_history, server_maxTemp, server_averageTemp
    return render_template(
        'main.html', 
        temp=sensor.get_temperature(), 
        len=len(server_history), 
        history=list(server_history),  # Převod sdíleného seznamu na běžný seznam
        server_maxTemp=server_maxTemp.value,
        server_averageTemp= server_averageTemp.value) # Čtení sdílené proměnné


@app.route("/temp")
def temp():
    return str(sensor.get_temperature())

@app.route("/maxTemp")   
def maxTemp():
    return str(server_maxTemp.value)

@app.route("/avgTemp")   
def maxTemp():
    return str(server_averageTemp.value)
    
@app.route("/reboot")
def reboot_server():
    os.system(' (sleep 1 && reboot) & ')
    return render_template('reboot.html')

@app.route("/update")
def update():
    VystupUpdate = subprocess.check_output("sudo git pull", shell=True, text=True)
    return render_template('update.html', output=VystupUpdate)
    #return f"{VystupUpdate}</pre><br><br><a href='/'>Zpět</a> <a href='/reboot'>Reboot</a>"
    
@app.route("/shutdown")
def shutdown_server():
    os.system('(sleep 1 && shutdown now &)')
    
    return redirect("/")

def run(tmp_sensor, ip, history, max_temp, averageTemp):
    global sensor, server_history, server_maxTemp, server_averageTemp
    sensor = tmp_sensor
    server_history = history
    server_maxTemp = max_temp  # Sdílená proměnná
    server_averageTemp = averageTemp

    app.run(host='0.0.0.0', port=80, debug=False)

def run_async(sensor, ip, history, max_temp, averageTemp):
    p = multiprocessing.Process(target=run, args=(sensor, ip, history, max_temp, averageTemp))
    p.start()
    return p

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
    return p
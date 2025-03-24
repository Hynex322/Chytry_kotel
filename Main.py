from pickle import FALSE
import time
import schedule, sched
from Temperature import TemperatureSensor
from Relay import Relay
import os
from LedBar import LedBar
from Button import Button
import Server
from Pin import Pin
from multiprocessing import Array,Manager

import threading

# gpio w1 init
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-term')

# config
check_delay = 30  # delay between temp checks
siren_btn_shutoff = 600  # shutoff time after btn press
temp_bounds = [20, 120]  # bounds for LEDs
temp_warn = 85  # limit temp for warning
TEMP_SOS_WARN = 80 # limit temp for SOS warning
SOS_OMEZENI_SPUSTENI = 300 # omezeni kolikrat za minutu se SOS spusti ve vterinach
press_for_turnoff = 50  # times btn is pressed to turnoff
lowBound  = 40
FALLaLARM = 2
HISTORYlEN = 10
PERIODhISTORY = 120 # ve vterinach, vzdalenost zaznamu 
TEPLOTA_ROZTOPENO = 50 #°C #Hranice od kdy se aktivuje automatickemu vypnuti
LIMIT_VYPNUTI = 30     #°C #Hranice automatickeho vypnuti
SPODNI_ALARM_LIMIT= 40 #°C #Spodni hranice od kdy prestane hlasit FALLaLARM

main_tmp_sensor = '28-00000a10a10f'

# gpio bcm config
siren_pin = 22
bar_pins = [12, 5, 6, 13, 19]
yellowLed_pin = 16

# server config
ip = '192.168.43.102'

# remote config
remote_url = 'http://kotel.esy.es/upload'
remote_key = 'secret_key'


# secondary init
tmp_sensor = TemperatureSensor(main_tmp_sensor, "Hlavní čidlo teploty")
sirena = Pin(siren_pin) #siren_relay = Relay(siren_pin)
yellowLed = Pin(yellowLed_pin)
siren_ontime = 0
bar = LedBar(bar_pins, temp_bounds)
siren_stop_btn = Button(17, 27)
history_60 = []  #list pro vypocet prumeru za 60 minut
# Vytvoříme Manager pro sdílenou paměť
manager = Manager()
maxTemp = manager.Value('d', 0)  # 'd' znamená double (desetinné číslo)
averageTemp = manager.Value('d', 0)
history = manager.list()
sos_omezeni_counter=False
# turn off the relay
Pin(26).low()

# functions definition
def Start_alarm():
    global siren_ontime
    if time.time() >= siren_ontime:
        sirena.high() #siren_relay.on()
        print("ALARM")
    else:
        sirena.low() #siren_relay.off()

def Stop_alarm():
    sirena.low() #siren_relay.off()
    
def ShutDown():
    print("[log]", "Shutting down")
    bar.snake(1, 3)
    os.system('shutdown now')
    
def Reboot():
    print("[log]", "Rebooting")
    bar.snake(.3, 5)
    os.system('reboot')

def Decline_alert():
    sirena.high() #siren_relay.on()
    time.sleep(0.3)
    sirena.low() #siren_relay.off()

def alert_long():
    sirena.high() #siren_relay.on()
    time.sleep(0.5)
    sirena.low() #siren_relay.off()

def alert_short():
    sirena.high() #siren_relay.on()
    time.sleep(0.2)
    sirena.low() #siren_relay.off()

def Sos():
    if Sos_omezeni():
        alert_short()
        time.sleep(0.1)
        alert_short()
        time.sleep(0.1)
        alert_short()
        time.sleep(0.1)
        alert_long()
        time.sleep(0.1)
        alert_long()
        time.sleep(0.1)
        alert_long()
        time.sleep(0.1)
        alert_short()
        time.sleep(0.1)
        alert_short()
        time.sleep(0.1)
        alert_short()

# Vytvoření plánovače
scheduler = sched.scheduler(time.time, time.sleep)

def Sos_zruseni_omezeni():
    global sos_omezeni_counter
    sos_omezeni_counter=False

def Sos_omezeni():
    global sos_omezeni_counter
    if sos_omezeni_counter:
        return False
    else:
        sos_omezeni_counter = True
        scheduler.enter(SOS_OMEZENI_SPUSTENI, 1, Sos_zruseni_omezeni)
        return True
    
def run_scheduler():
    while True:
        scheduler.run(blocking=True)
        time.sleep(1)  # Krátká pauza pro uvolnění CPU

def PrumerTeploty():
    global averageTemp, history_60

    temperature=tmp_sensor.get_temperature()
    history_60.append(round(temperature , 1))  # Přidáme novou hodnotu

    if len(history_60) > 60:
        history_60.pop(0)  # Omezíme délku na 60 prvků

    if len(history_60) > 0:
        averageTemp.value = round(sum(history_60) / len(history_60), 1)
    print("hodnota averageTemp: ", averageTemp )

def KontrolaVypnuti(history, pocet_kontrolovanych, roztopen_kotel):
    # Pokud je seznam kratší než požadovaný počet kontrolovaných prvků, vrátíme False
    if (len(history) < pocet_kontrolovanych) or (not roztopen_kotel):
        #print("Seznam je příliš krátký! Požadováno:", pocet_kontrolovanych, "Dostupné:", len(history))
        return False

    # Procházíme prvky od konce seznamu směrem k začátku
    for ii in range(len(history) - 1, len(history) - 1 - pocet_kontrolovanych, -1):
    	if history[ii] > LIMIT_VYPNUTI:
            print("Teplota je moc vysoká:", history[ii], "Kontrola pole:", ii)
            return False  # Okamžité ukončení při vysoké teplotě
    return True

#definice jak casto se spusti ulozeni prumerne teploty
schedule.every().minute.do(PrumerTeploty)

# program loop
def main():
    global siren_ontime, maxTemp, history
    posledni_maxTemp=0
    pressed_for = 0
    blik_i = 0
    odpocet = 0
    roztopen_kotel = False
   
    while True:
        temperature = tmp_sensor.get_temperature()
        #print("[teplota]", temperature)
        schedule.run_pending()  # Zkontroluje, zda je čas na spuštění úlohy

        if temperature >= temp_warn:
            Start_alarm()
        else:
            Stop_alarm()
        if temperature >= TEMP_SOS_WARN:
            Sos()              
        if temperature < lowBound:
            yellowLed.high()
        else:
            yellowLed.low()

        bar.display(temperature)

        if maxTemp.value < temperature:
            maxTemp.value = round(temperature, 1)
            #print("Nová maximální hodnota: ", maxTemp.value)

        if posledni_maxTemp < temperature:
            posledni_maxTemp = temperature
            #print("Nová posledni maximální hodnota: ", posledni_maxTemp)
        elif ((temperature < (posledni_maxTemp - FALLaLARM)) and (temperature > SPODNI_ALARM_LIMIT)):
            Decline_alert()
            posledni_maxTemp = temperature
            #print("Maximální teplota byla snížena na: ", posledni_maxTemp)
         
        for _ in range(int(check_delay / .1)):
            if siren_stop_btn.get():
                if siren_ontime < time.time():
                    print("[log]", "Alarm was paused")
                    siren_ontime = time.time() + siren_btn_shutoff
                    Stop_alarm()
                pressed_for += 1
                if pressed_for >= press_for_turnoff:
                    ShutDown()
            else:
                pressed_for = 0
            if temperature < temp_bounds[0]:
                if blik_i > 60:
                    blik_i = 0
                    bar.light(0)
                    time.sleep(0.5)
                    bar.off()
                else:
                    blik_i += 1
                    
            time.sleep(.1)

        odpocet += check_delay

        if odpocet >= PERIODhISTORY:
            history.append(round(temperature, 1))  # Přidáme novou hodnotu
            if len(history) > 10:
                history.pop(0)  # Omezíme délku na 10 prvků
            odpocet = 0

        print("History:", list(history))  # Výpis historie

        if (not roztopen_kotel) and (temperature > TEPLOTA_ROZTOPENO):
            roztopen_kotel = True
    
        if KontrolaVypnuti(history, 6, roztopen_kotel):
            print("vypinam kotel")
            time.sleep(220.0) #zpozdeni kdyby se nekde stala chyba
            ShutDown()
         

# program start
if __name__ == '__main__':
    bar.snake(0.5, 5)  # start!
    print("Test sirény")
    sirena.high() #siren_relay.on()
    time.sleep(0.25)
    sirena.low() #siren_relay.off()
    time.sleep(0.5)
    sirena.high() #siren_relay.on()
    time.sleep(0.25)
    sirena.low() #siren_relay.off()
    print("Konec testu sirény")
    Server.run_async(tmp_sensor, ip, history, maxTemp, averageTemp)
    # Server.run_remote(tmp_sensor, url=remote_url, key=remote_key)
    # Spustíme plánovač v samostatném vlákně
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    main()


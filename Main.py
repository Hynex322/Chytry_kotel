from pickle import FALSE
import time
from Temperature import TemperatureSensor
from Relay import Relay
import os
from LedBar import LedBar
from Button import Button
import Server
from Pin import Pin
from multiprocessing import Array

# gpio w1 init
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-term')

# config
check_delay = 30  # delay between temp checks
siren_btn_shutoff = 600  # shutoff time after btn press
temp_bounds = [20, 120]  # bounds for LEDs
temp_warn = 85  # limit temp for warning
press_for_turnoff = 50  # times btn is pressed to turnoff
lowBound  = 40
FALLaLARM = 2
HISTORYlEN = 10
PERIODhISTORY = 60 # ve vterinach, vzdalenost zaznamu 
TEPLOTA_ROZTOPENO = 50 #°C #Hranice od kdy se aktivuje automatickemu vypnuti
LIMIT_VYPNUTI = 30     #°C #Hranice automatickeho vypnuti

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
history = Array('d', HISTORYlEN)
maxTemp = 0

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

# program loop
def main():
    
    global siren_ontime, maxTemp
    pressed_for = 0
    blik_i = 0
    odpocet = 0
    roztopen_kotel = 0
    while True:
        temperature = tmp_sensor.get_temperature()
        print("[teplota]", temperature)

        if temperature >= temp_warn:
            Start_alarm()
        else:
            Stop_alarm()

        if temperature < lowBound:
            yellowLed.high()
        else:
            yellowLed.low()

        bar.display(temperature)

        if maxTemp < temperature:
            maxTemp = temperature
            print("Nová maximální hodnota: ", maxTemp)
        elif temperature < (maxTemp - FALLaLARM):
            Decline_alert()
            maxTemp = temperature
            print("Maximální teplota byla snížena na: ", maxTemp)
         
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
            for i in range(HISTORYlEN-1):
                history[i] = history[i+1]
            history[HISTORYlEN-1] = round(temperature, 1)
            odpocet = 0

        print("History: ", history[:])

        if (not roztopen_kotel) and (temperature > TEPLOTA_ROZTOPENO):
            roztopen_kotel = 1
        if (roztopen_kotel and (len(history) > 5) and (temperature < LIMIT_VYPNUTI)):
            for ii in range(6):
                if history[ii] > LIMIT_VYPNUTI:
                    print("teplota je moc vysoka ", history[ii])
                    break
                else:
                    print("kotel se vypne ",ii)
            if ii == 5:
                sirena.high()
                time.sleep(2.0)
                sirena.low()
                print("vypinam kotel")
                time.sleep(120.0) #zpozdeni kdyby se nekde stala chyba
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
    Server.run_async(tmp_sensor, ip, history, maxTemp)
    # Server.run_remote(tmp_sensor, url=remote_url, key=remote_key)
    main()




class TemperatureSensor:

    def __init__(self, serial, note="Temperature sensor"):
        self.serial = serial
        self.note = note

    def get_temperature(self):
        with open('/sys/bus/w1/devices/' + self.serial + '/w1_slave') as log:
            lines = log.readlines()
            for line in lines:
                if line.find('t=') != -1:
                    return int(line[line.find('t=')+2:]) / 1000
                    #return t + (abs(22-t)*10)
        return "Fail"

    def is_working(self):
        with open('/sys/bus/w1/devices/' + self.serial + '/w1_slave') as log:
            lines = log.readlines()
            for line in lines:
                if line.find(' : crc=') != -1:
                    return line[line.find(' : crc=')+10:-1]
        return "NO"


    def status(self):
        print('Type:', '1-wire sensor')
        print('Serial:', self.serial)
        print('Note:', self.note)
        print('Working:', self.is_working())
        print('Temp:', self.get_temperature(), '°C')


# 28-00000a10a10f
#
# sensor = TemperatureSensor("28-00000a10a10f", "Virtual sensor")
# print(sensor.get_temperature(), "°C")
# sensor.status()

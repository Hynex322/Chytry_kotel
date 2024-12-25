import time
import Pin

pins_id = [12, 5, 6, 13, 19]
pins = []
for pin in pins_id:
	pins.append(Pin.Pin(pin))

while True:
	for pin in pins:
		pin.high()
	time.sleep(0.5)
	for pin in pins:
		pin.low()
	time.sleep(0.5)



import RPi.GPIO as io
io.setmode(io.BCM)

class Pin:
	def __init__(self, pin):
		self.pin = pin
		io.setup(pin, io.OUT)

	def high(self):
		io.output(self.pin, io.HIGH)

	def low(self):
		io.output(self.pin, io.LOW)


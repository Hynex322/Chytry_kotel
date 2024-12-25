import RPi.GPIO as IO
IO.setmode(IO.BCM)


class Relay:

    def __init__(self, main_pin):
        self.pin = main_pin
        self.state = False
        IO.setup(main_pin, IO.OUT)

    def on(self):
        self.state = True
        IO.output(self.pin, True)

    def off(self):
        self.state = False
        IO.output(self.pin, False)

    def toggle(self):
        self.state = not self.state
        IO.output(self.pin, self.state)
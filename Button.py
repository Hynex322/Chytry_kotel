import RPi.GPIO as IO
IO.setmode(IO.BCM)


class Button:

    def __init__(self, pin_in, pin_out):
        self.pin_in = pin_in
        self.pin_out = pin_out

        self.setup()

    def setup(self):
        IO.setup(self.pin_in, IO.IN, pull_up_down=IO.PUD_DOWN)
        IO.setup(self.pin_out, IO.OUT)
        IO.output(self.pin_out, True)

    def get(self):
        return IO.input(self.pin_in)

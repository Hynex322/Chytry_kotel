import RPi.GPIO as IO
IO.setmode(IO.BCM)


class LedBar:

    def __init__(self, pins, bounds):
        self.step = (bounds[1] - bounds[0]) / len(pins)
        self.start = bounds[0]
        self.pins = pins
        self.setmodes()

    def setmodes(self):
        for pin in self.pins:
            IO.setup(pin, IO.OUT)

    def display(self, number):
        n = int((number - self.start) // self.step)
        self.light_to(n)
        
    def light(self, i):
        IO.output(self.pins[i], True)

    def light_to(self, n):
        self.off()
        for i in range(min(n, len(self.pins))):
            IO.output(self.pins[i], True)

    def off(self):
        for pin in self.pins:
            IO.output(pin, False)
            
    def snake(self, length=1, iterations=1):
        import time
        delay = length / len(self.pins) / 2
        for _ in range(iterations):
            for plus in [0, 1 + len(self.pins)*-1]:
                for i in range(len(self.pins)):
                    self.off()
                    self.light(abs(i + plus))
                    time.sleep(delay)



BCM = "bcm"
OUT = "out"
IN = "in"
HIGH = "high"
LOW = "low"
PUD_UP = "pull up"
PUD_DOWN = "pull down"


mode = None


def setmode(mode):
    mode = mode

def setup(pin, how, pull_up_down=None):
    print("Pin", pin, "setup as", how)
    if pull_up_down:
        print("Pin", pin, "is", pull_up_down)

def output(pin, what):
    print("Pin", pin, "is", what)

def input(pin):
    return False
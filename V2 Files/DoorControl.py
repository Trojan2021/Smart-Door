import Jetson.GPIO as GPIO



class Door:
    # For doorstate, True means that the door is closed and False means that it is open
    def __init__(self, doorName):
        self.name = doorName
        self.doorState = True
        self.face = False
        self.deadState = False
        self.faceState = False
        self.handState = False

    # Door Controls
    def doorToggle(self):
        self.doorState = not self.state

    def open(self):
        if self.doorState:
            self.doorState = False
            # Put servo control here

    def close(self):
        if not self.doorState:
            self.doorState = True

    # Facial Recognition Control
    def toggleface(self):
        self.face = not self.face

    # Deadbolt Control
    def deadOpen(self):
        self.deadState = False

    def deadClose(self):
        self.deadState = True

    # Handle Control
    def handOpen(self):
        self.handState = True

    def handClose(self):
        self.handState = False

    # Control the LEDs
    def lockedLED(self):
        GPIO.output(RED, False)
        GPIO.output(GREEN, True)

    def unlockedLED(self):
        GPIO.output(RED, True)
        GPIO.output(GREEN, False)

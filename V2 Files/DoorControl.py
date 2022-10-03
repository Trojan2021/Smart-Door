class Door:
    # For doorstate, True means that the door is closed and False means that it is open
    def __init__(self, doorName):
        self.name = doorName
        self.state = True

    def toggle(self):
        self.state = not self.state

    def open(self):
        self.state = False

    def close(self):
        self.state = True

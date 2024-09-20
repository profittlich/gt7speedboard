


class Component:
    def __init__(self, cfg, data):
        self.cfg = cfg
        self.data = data

    def getWidget(self):
        return None

    def addPoint(self, curPoint, curLap):
        pass

    def initRace(self):
        pass

    def newLap(self, curPoint):
        pass

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class MapCE(sb.component.Component):
    def __init__(self, cfg, data):
        super().__init__(cfg, data)
        self.mapViewCE = MapView()

    def getWidget(self):
        return self.mapViewCE

    def speedDiffQColor(self, d):
        col = QColor()
        hue = self.cfg.speedDiffCenterHue - d/(self.cfg.speedDiffSpread/self.cfg.speedDiffCenterHue) 
        if hue < self.cfg.speedDiffMinHue:
            hue = self.cfg.speedDiffMinHue
        if hue > self.cfg.speedDiffMaxHue:
            hue = self.cfg.speedDiffMaxHue
        col.setHsvF (hue, self.cfg.speedDiffColorSaturation, self.cfg.speedDiffColorValue)

        return col


    def updateMapCE(self, curPoint):
        if self.cfg.circuitExperience and not self.data.previousPoint is None:
            color = self.cfg.mapCurrentColor
            if len(self.data.previousLaps) > 0:
                speedDiff = self.data.previousLaps[self.data.bestLap].points[self.data.closestIBest].car_speed - curPoint.car_speed
                if speedDiff == 0:
                    color = self.cfg.mapStandingColor
                else:
                    color = self.speedDiffQColor(speedDiff)
            self.mapViewCE.setPoints(self.data.previousPoint, curPoint, color)
            self.mapViewCE.update()

        if curPoint.throttle == 0 and curPoint.brake == 0:
            self.data.noThrottleCount+=1
        elif self.data.noThrottleCount > 0:
            self.data.noThrottleCount=0

    def addPoint(self, curPoint, curLap):
        self.updateMapCE(curPoint)

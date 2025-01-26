from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

# TODO rename file
class Map(sb.component.Component):
    def description():
        return "Map of previous racing lines"
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)
        self.widget = QWidget()
        layout = QHBoxLayout()
        self.widget.setLayout(layout) 

        self.mapView = MapView()
        layout.addWidget(self.mapView)

    def getWidget(self):
        return self.widget

    def speedDiffQColor(self, d):
        col = QColor()
        hue = self.cfg.speedDiffCenterHue - d/(self.cfg.speedDiffSpread/self.cfg.speedDiffCenterHue) 
        if hue < self.cfg.speedDiffMinHue:
            hue = self.cfg.speedDiffMinHue
        if hue > self.cfg.speedDiffMaxHue:
            hue = self.cfg.speedDiffMaxHue
        col.setHsvF (hue, self.cfg.speedDiffColorSaturation, self.cfg.speedDiffColorValue)

        return col


    def updateMap(self, curPoint):
        if not self.data.previousPoint is None:
            color = self.cfg.mapCurrentColor
            if len(self.data.previousLaps) > 0:
                speedDiff = self.data.previousLaps[self.data.bestLap].points[self.data.closestIBest].car_speed - curPoint.car_speed
                color = self.speedDiffQColor(speedDiff)
            self.mapView.setPoints(self.data.previousPoint, curPoint, color)
            self.mapView.update()

        if curPoint.throttle == 0 and curPoint.brake == 0:
            self.data.noThrottleCount+=1
        elif self.data.noThrottleCount > 0:
            self.data.noThrottleCount=0
        self.mapView.update()

    def addPoint(self, curPoint, curLap):
        self.updateMap(curPoint)

    def title(self):
        return "Map"

    def newTrack(self, curPoint, track):
        self.newSession()

    def newSession(self):
        self.mapView.clear()
        for p in range(1,len(self.data.curLap.points)):
            self.mapView.setPoints(self.data.curLap.points[p-1], self.data.curLap.points[p])
        self.mapView.update()

    def completedLap(self, curPoint, lastLap, isFullLap):
        if not self.cfg.circuitExperience or curPoint.current_lap != 0:
            self.mapView.endLap()
        self.mapView.update()

sb.component.componentLibrary['Map'] = Map

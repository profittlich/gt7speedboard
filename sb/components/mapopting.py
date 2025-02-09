from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import threading

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

# TODO rename file
class OptimizingMap(sb.component.Component):
    def description():
        return "Map of previous racing lines"
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)
        self.colormap = [ 
             QColor ("#f00"),
             QColor ("#0f0"),
             QColor ("#00f"),
             QColor ("#ff0"),
             QColor ("#f0f"),
             QColor ("#0ff"),
             QColor ("#fff"),
             QColor ("#f77"),
             QColor ("#7f7"),
             QColor ("#77f"),
             QColor ("#ff7"),
             QColor ("#f7f"),
             QColor ("#7ff")]
        self.widget = QWidget()
        layout = QHBoxLayout()
        self.widget.setLayout(layout) 

        self.mapView = MapView()
        layout.addWidget(self.mapView)
        self.lastSize = 0

        self.thread = None
        self.bulkRendering = False
        self.requestUpdate = False

    def getWidget(self):
        return self.widget

    def updateMap(self, curPoint):
        if not self.previousPoint is None:
            color = self.colormap[curPoint.current_lap % len(self.colormap)]
            self.mapView.setPoints(self.previousPoint, curPoint, color)

    def defaultTitle(self):
        return "O-ing Map"

    def handleAllPoints(self):
        for p in self.data.curOptimizingLap.points:
            self.updateMap(p)
            self.previousPoint = p
        self.requestUpdate = True
        self.bulkRendering = False

    def addPoint(self, ignore, ignore2):
        if self.requestUpdate:
            logPrint("Display map segment")
            self.mapView.update()
            self.requestUpdate = False
        if len(self.data.optimizedLap.points) == 0:
            return
        if len(self.data.curOptimizingLap.points) != self.lastSize:
            if not self.bulkRendering:
                logPrint("Render map segment")
                self.lastSize = len(self.data.curOptimizingLap.points)
                self.mapView.clear()
                self.previousPoint = None
                self.bulkRendering = True
                self.thread = threading.Thread(target=self.handleAllPoints)
                self.thread.start()

sb.component.componentLibrary['OptimizingMap'] = OptimizingMap

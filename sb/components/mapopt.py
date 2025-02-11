from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

# TODO rename file
class OptimalMap(sb.component.Component):
    def description():
        return "Map of previous racing lines"
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)
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

    def getWidget(self):
        return self.widget

    def updateMap(self, curPoint):
        if not self.previousPoint is None:
            color = self.colormap[curPoint.current_lap % len(self.colormap)]
            self.mapView.setPoints(self.previousPoint, curPoint, color)

    def defaultTitle(self):
        return "OMap"

    def completedLap(self, curPoint, lastLap, isFullLap):
        if not self.cfg.circuitExperience or curPoint.current_lap != 0:
            self.mapView.endLap()
        self.mapView.clear()
        self.previousPoint = None
        for p in self.data.optimizedLap.points:
            self.updateMap(p)
            self.previousPoint = p
        self.mapView.update()

sb.component.componentLibrary['OptimalMap'] = OptimalMap

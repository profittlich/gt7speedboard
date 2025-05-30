from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import sb.component
from sb.gt7telepoint import Point
from sb.helpers import logPrint
from sb.gt7widgets import PedalWidget

class Pedals(sb.component.Component):
    def description():
        return "Brake and throttle pedal display"
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)

    def getWidget(self):
        self.widget = QWidget()
        layout = QHBoxLayout()
        self.widget.setLayout(layout) 

        self.pedalWidget = PedalWidget()
        layout.addWidget(self.pedalWidget)

        return self.widget

    def addPoint(self, curPoint, curLap):
        self.pedalWidget.setDistance(curPoint.brake, curPoint.throttle)
        self.widget.update()

    def defaultTitle(self):
        return "Pedals"

sb.component.componentLibrary['Pedals'] = Pedals

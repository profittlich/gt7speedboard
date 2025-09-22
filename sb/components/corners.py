from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class Corners(sb.component.Component):
    def description():
        return "Corner/straight indicator"
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)
        self.prevAV = 0
        self.txt = "STRAIGHT"

    def getWidget(self):
        self.widget = QLabel("")
        self.widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.widget.font()
        font.setPointSize(self.fontSizeLarge())
        font.setBold(True)
        self.widget.setFont(font)

        return self.widget

    def addPoint(self, curPoint, curLap):
        av = math.sqrt(curPoint.angular_velocity_x**2 + curPoint.angular_velocity_y**2 + curPoint.angular_velocity_z**2)
        if av > 0.35:
            self.txt = "CORNER"
        elif self.prevAV < 0.2:
            self.txt = "STRAIGHT"
        self.widget.setText(self.txt + "\n" + str(round(av,1)))
        self.prevAV = av

sb.component.componentLibrary['Corners'] = Corners

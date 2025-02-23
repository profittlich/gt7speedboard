from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class Gear(sb.component.Component):
    def description():
        return "Current car speed"
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)

    def getWidget(self):
        self.widget = QLabel("")
        self.widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.widget.font()
        font.setPointSize(self.fontSizeLarge())
        font.setBold(True)
        self.widget.setFont(font)

        return self.widget

    def addPoint(self, curPoint, curLap):
        self.widget.setText(str(curPoint.current_gear))

sb.component.componentLibrary['Gear'] = Gear

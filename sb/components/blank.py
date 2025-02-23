from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class Blank(sb.component.Component):
    def description():
        return "Blank space"
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)

    def getWidget(self):
        self.widget = QLabel("")

        return self.widget

sb.component.componentLibrary['Blank'] = Blank

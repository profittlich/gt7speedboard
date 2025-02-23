from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import sb.component
from sb.gt7telepoint import Point
from sb.gt7widgets import ColorLabel
from sb.helpers import logPrint

class TyreTemps(sb.component.Component):
    def description():
        return "Tyre temperature display"
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)

    def getWidget(self):
        self.tyreFR = ColorLabel("?°C")
        self.tyreFR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFR.setAutoFillBackground(True)
        font = self.tyreFR.font()
        font.setPointSize(self.fontSizeLarge())
        font.setBold(True)
        self.tyreFR.setFont(font)
        self.tyreFR.setColor(self.cfg.backgroundColor)

        self.tyreFL = ColorLabel("?°C")
        self.tyreFL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFL.setAutoFillBackground(True)
        font = self.tyreFL.font()
        font.setPointSize(self.fontSizeLarge())
        font.setBold(True)
        self.tyreFL.setFont(font)
        self.tyreFL.setColor(self.cfg.backgroundColor)
        
        self.tyreRR = ColorLabel("?°C")
        self.tyreRR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRR.setAutoFillBackground(True)
        font = self.tyreRR.font()
        font.setPointSize(self.fontSizeLarge())
        font.setBold(True)
        self.tyreRR.setFont(font)
        self.tyreRR.setColor(self.cfg.backgroundColor)

        self.tyreRL = ColorLabel("?°C")
        self.tyreRL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRL.setAutoFillBackground(True)
        font = self.tyreRL.font()
        font.setPointSize(self.fontSizeLarge())
        font.setBold(True)
        self.tyreRL.setFont(font)
        self.tyreRL.setColor(self.cfg.backgroundColor)

        self.tyreWidget = QWidget()
        tyreLayout = QGridLayout()
        self.tyreWidget.setLayout(tyreLayout)
        tyreLayout.addWidget(self.tyreFL, 0, 0)
        tyreLayout.addWidget(self.tyreFR, 0, 1)
        tyreLayout.addWidget(self.tyreRL, 1, 0)
        tyreLayout.addWidget(self.tyreRR, 1, 1)
    
        return self.tyreWidget

    def tyreTempQColor(self, temp):
        col = QColor()
        hue = self.cfg.tyreTempCenterHue - (temp - self.cfg.tyreTempCenter)/(self.cfg.tyreTempSpread/self.cfg.tyreTempCenterHue)
        if hue < self.cfg.tyreTempMinHue:
            hue = self.cfg.tyreTempMinHue
        if hue > self.cfg.tyreTempMaxHue:
            hue = self.cfg.tyreTempMaxHue
        col.setHsvF (hue, self.cfg.tyreTempSaturation, self.cfg.tyreTempValue)

        return col

    def updateTyreTemps(self, curPoint):
        self.tyreFL.setText (str(round(curPoint.tyre_temp_FL)) + "°C")
        self.tyreFL.setColor(QColor(self.tyreTempQColor(curPoint.tyre_temp_FL)))

        self.tyreFR.setText (str(round(curPoint.tyre_temp_FR)) + "°C")
        self.tyreFR.setColor(QColor(self.tyreTempQColor(curPoint.tyre_temp_FR)))

        self.tyreRR.setText (str(round(curPoint.tyre_temp_RR)) + "°C")
        self.tyreRR.setColor(QColor(self.tyreTempQColor(curPoint.tyre_temp_RR)))

        self.tyreRL.setText (str(round(curPoint.tyre_temp_RL)) + "°C")
        self.tyreRL.setColor(QColor(self.tyreTempQColor(curPoint.tyre_temp_RL)))

    def addPoint(self, curPoint, curLap):
        self.updateTyreTemps(curPoint)

    def defaultTitle(self):
        return "Tyres"

sb.component.componentLibrary['TyreTemps'] = TyreTemps

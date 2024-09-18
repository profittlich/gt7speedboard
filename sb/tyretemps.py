from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import sb.component
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class TyreTemps(sb.component.Component):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.tyreFR = QLabel("?°C")
        self.tyreFR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFR.setAutoFillBackground(True)
        font = self.tyreFR.font()
        font.setPointSize(self.cfg.fontSizeLarge)
        font.setBold(True)
        self.tyreFR.setFont(font)
        pal = self.tyreFR.palette()
        pal.setColor(self.tyreFR.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.tyreFR.foregroundRole(), self.cfg.foregroundColor)
        self.tyreFR.setPalette(pal)

        self.tyreFL = QLabel("?°C")
        self.tyreFL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFL.setAutoFillBackground(True)
        font = self.tyreFL.font()
        font.setPointSize(self.cfg.fontSizeLarge)
        font.setBold(True)
        self.tyreFL.setFont(font)
        pal = self.tyreFL.palette()
        pal.setColor(self.tyreFL.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.tyreFL.foregroundRole(), self.cfg.foregroundColor)
        self.tyreFL.setPalette(pal)
        
        self.tyreRR = QLabel("?°C")
        self.tyreRR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRR.setAutoFillBackground(True)
        font = self.tyreRR.font()
        font.setPointSize(self.cfg.fontSizeLarge)
        font.setBold(True)
        self.tyreRR.setFont(font)
        pal = self.tyreRR.palette()
        pal.setColor(self.tyreRR.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.tyreRR.foregroundRole(), self.cfg.foregroundColor)
        self.tyreRR.setPalette(pal)

        self.tyreRL = QLabel("?°C")
        self.tyreRL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRL.setAutoFillBackground(True)
        font = self.tyreRL.font()
        font.setPointSize(self.cfg.fontSizeLarge)
        font.setBold(True)
        self.tyreRL.setFont(font)
        pal = self.tyreRL.palette()
        pal.setColor(self.tyreRL.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.tyreRL.foregroundRole(), self.cfg.foregroundColor)
        self.tyreRL.setPalette(pal)

        self.tyreWidget = QWidget()
        tyreLayout = QGridLayout()
        self.tyreWidget.setLayout(tyreLayout)
        tyreLayout.addWidget(self.tyreFL, 0, 0)
        tyreLayout.addWidget(self.tyreFR, 0, 1)
        tyreLayout.addWidget(self.tyreRL, 1, 0)
        tyreLayout.addWidget(self.tyreRR, 1, 1)
    
    def getWidget(self):
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
        pal = self.tyreFL.palette()
        pal.setColor(self.tyreFL.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_FL)))
        self.tyreFL.setPalette(pal)

        self.tyreFR.setText (str(round(curPoint.tyre_temp_FR)) + "°C")
        pal = self.tyreFR.palette()
        pal.setColor(self.tyreFR.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_FR)))
        self.tyreFR.setPalette(pal)

        self.tyreRR.setText (str(round(curPoint.tyre_temp_RR)) + "°C")
        pal = self.tyreRR.palette()
        pal.setColor(self.tyreRR.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_RR)))
        self.tyreRR.setPalette(pal)

        self.tyreRL.setText (str(round(curPoint.tyre_temp_RL)) + "°C")
        pal = self.tyreRL.palette()
        pal.setColor(self.tyreRL.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_RL)))
        self.tyreRL.setPalette(pal)

    def addPoint(self, curPoint, curLap):
        self.updateTyreTemps(curPoint)

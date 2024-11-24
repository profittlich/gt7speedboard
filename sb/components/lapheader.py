from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class LapHeader(sb.component.Component):
    def description():
        return "Remaining or driven laps display"
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

        self.header = QLabel("? LAPS LEFT")
        font = self.header.font()
        font.setPointSize(cfg.fontSizeNormal)
        font.setBold(True)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pal = self.header.palette()
        pal.setColor(self.header.backgroundRole(), cfg.backgroundColor)
        pal.setColor(self.header.foregroundRole(), cfg.foregroundColor)
        self.header.setPalette(pal)
        self.inPit = False


    def getWidget(self):
        return self.header

    def updateLaps(self, curPoint):
        lapSuffix = ""
        if self.data.lapOffset > 0:
            lapSuffix += " [+" + str(self.data.lapOffset) + "]"
        elif self.data.lapOffset < 0:
            lapSuffix += " [" + str(self.data.lapOffset) + "]"
        #if self.inPit:
            #lapSuffix += " PIT STOP"
        if self.data.isRecording:
            lapSuffix += " [RECORDING]"
        if self.cfg.developmentMode:
            lapSuffix += " [DEV]"
        if self.cfg.circuitExperience:
            self.header.setText("CIRCUIT EXPERIENCE" + lapSuffix)
        elif curPoint.total_laps > 0:
            lapValue = curPoint.total_laps + self.data.lapOffset - curPoint.current_lap + 1
            if self.cfg.lapDecimals:
                lapValue -= self.data.lapProgress
                lapValue = round(lapValue, 2)
            self.header.setText(str(lapValue) + " LAPS LEFT" + lapSuffix)
        else:
            lapValue = curPoint.current_lap
            if self.cfg.lapDecimals:
                lapValue = str(lapValue) + " (" + str(round(self.data.lapProgress * 100)) + "%)"
            self.header.setText("LAP " + str(lapValue) + lapSuffix)

    def pitStop(self):
        self.inPit = True

    def completedLap(self, curPoint, lastLap, isFullLap):
        self.inPit = False

    def addPoint(self, curPoint, curLap):
        if curPoint.car_speed > 110:
            self.inPit = False

        self.updateLaps(curPoint)

sb.component.componentLibrary['LapHeader'] = LapHeader

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

componentLibrary = {}

class Component:
    def __init__(self, cfg, data):
        self.cfg = cfg
        self.data = data

    def title(self):
        return None

    @staticmethod
    def description():
        return ""

    def getWidget(self):
        return None

    def makeHeaderWidget(self, title):
        headerWidget = QLabel(title.upper())
        font = headerWidget.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        headerWidget.setFont(font)
        headerWidget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pal = headerWidget.palette()
        pal.setColor(headerWidget.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(headerWidget.foregroundRole(), self.cfg.foregroundColor)
        headerWidget.setPalette(pal)
        return headerWidget

    def getTitledWidget(self, title):
        result = QWidget()
        masterLayout = QGridLayout()
        masterLayout.setRowStretch(0, 1)
        masterLayout.setRowStretch(1, 1000)
        masterLayout.setContentsMargins(0,0,0,0)
        result.setLayout(masterLayout)
        self.header = self.makeHeaderWidget(title)
        masterLayout.addWidget(self.header, 0, 0, 1, 1)
        widget = self.getWidget()
        if not widget is None:
            masterLayout.addWidget(widget, 1, 0, 1, 1)
        return result


    def addPoint(self, curPoint, curLap):
        pass

    def newSession(self):
        pass

    def completedLap(self, curPoint, lastLap, isFullLap):
        pass

    def newTrack(self, curPoint, track):
        pass

    def maybeNewTrack(self, curPoint, track):
        pass

    def pitStop(self):
        pass

    def leftCircuit(self):
        pass

    def keyPressEvent(self, e):
        pass

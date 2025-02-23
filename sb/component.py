from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from sb.helpers import *

componentLibrary = {}

class Component:
    def __init__(self, cfg, data, callbacks):
        self.cfg = cfg
        self.data = data
        self.callbacks = callbacks
        self.overrideTitle = None
        self.fontScale = 1

    def defaultTitle(self):
        return None

    def title(self):
        if self.overrideTitle is None:
            return self.defaultTitle()
        else:
            return self.overrideTitle

    def setFontScale(self, s):
        self.fontScale = s

    def fontSizeLarge(self):
        logPrint(self.fontScale)
        return round(self.cfg.fontSizeLarge * self.fontScale)

    def fontSizeNormal(self):
        return round(self.cfg.fontSizeNormal * self.fontScale)

    def fontSizeSmall(self):
        return round(self.cfg.fontSizeSmall * self.fontScale)

    def fontSizeVerySmall(self):
        return round(self.cfg.fontSizeVerySmall * self.fontScale)

    def setTitle(self, t):
        self.overrideTitle = t

    @staticmethod
    def description():
        return ""

    @staticmethod
    def actions():
        return {}

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
        else:
            return None


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

    def callAction(self, a):
        pass

    def stop(self):
        pass

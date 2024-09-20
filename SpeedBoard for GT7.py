#import cProfile
import sys
import copy
import os
import threading
import traceback
import json
from wakepy import keep
import math
import queue
import datetime
import time
from pathlib import Path
import platform

from cProfile import Profile
from pstats import SortKey, Stats

from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from sb.gt7telepoint import Point
from sb.helpers import logPrint
from sb.laps import loadLap
from sb.laps import Lap
from sb.laps import PositionPoint
from sb.helpers import loadCarIds, idToCar
from sb.helpers import indexToTime, msToTime
from sb.trackdetector import TrackDetector

import sb.gt7telemetryreceiver as tele
from sb.gt7widgets import *

import sb.components.tyretemps
import sb.components.fuelandmessages
import sb.components.lapheader
import sb.components.mapce

class WorkerSignals(QObject):
    finished = pyqtSignal(str, float)

class Worker(QRunnable, QObject):
    def __init__(self, func, msg, t, args=()):
        super(Worker, self).__init__()
        self.func = func
        self.msg = msg
        self.t = t
        self.args = args
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        altMsg = self.func(*self.args)
        if altMsg is None:
            self.signals.finished.emit(self.msg, self.t)
        else:
            self.signals.finished.emit(altMsg, self.t)

class Run:
    def __init__(self, sessionStart):
        self.carId = None
        self.topSpeed = 0
        self.lapTimes = []
        self.sessionStart = sessionStart
        self.description = ""
    
    def addLapTime(self, t, l):
        self.lapTimes.append((t, l))

    def lastLap(self):
        return self.sessionStart + len(self.lapTimes)

    def startLap(self):
        return self.sessionStart

    def bestLap(self):
        fastest = (1000000000000, 0)
        for t in self.lapTimes:
            if t[0] < fastest[0]:
                fastest = t

        return fastest

    def medianLap(self):
        sorter = []
        for e in self.lapTimes:
            sorter.append(e[0])

        if len(sorter) > 0:
            sorter = sorted(sorter)
            target = sorter[len(sorter)//2]
            for e in self.lapTimes:
                if e[0] == target:
                    return e
        return (0,0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.defaultPalette = self.palette()

        loadCarIds()

        self.trackDetector = None
        self.goFullscreen = True

        logPrint("Clear sessions")
        self.sessionStats = []

        self.masterWidget = None
        self.masterWidgetIndex = 0
        self.loadConstants()
        self.threadpool = QThreadPool()

        self.startWindow = StartWindow()
        self.startWindow.starter.clicked.connect(self.startDash)
        self.startWindow.ip.returnPressed.connect(self.startDash)

        self.setWindowTitle("SpeedBoard for GT7 (v5)")
        self.queue = queue.Queue()
        self.receiver = None
        self.isRecording = False

        self.circuitExperience = True
        self.lapDecimals = False
        self.recordingEnabled = False
        self.messagesEnabled = False
        self.linecomp = False
        self.timecomp = False
        self.brakepoints = False
        self.throttlepoints = False
        self.countdownBrakepoint = False
        self.bigCountdownBrakepoint = 0
        self.switchToBestLap = True

        self.showBestLap = True
        self.showLastLap = True
        self.showMedianLap = True
        self.showRefALap = False
        self.showRefBLap = False
        self.showRefCLap = False
        self.showOptimalLap = False # TODO implement

        self.newMessage = None
        self.messages = []

        self.setCentralWidget(self.startWindow)

    def loadConstants(self):
        self.foregroundColor = QColor("#FFF")
        self.backgroundColor = QColor("#222")
        self.brightBackgroundColor = QColor("#333")

        self.warningColor1 = QColor("#f00")
        self.warningColor2 = QColor("#ff0")
        self.advanceWarningColor = QColor("#f80")

        self.countdownColor3 = QColor("#22F")
        self.countdownColor2 = QColor("#2FF")
        self.countdownColor1 = QColor("#FFF")

        self.tyreTempMinHue = 0
        self.tyreTempMaxHue = 0.667
        self.tyreTempCenterHue = 0.5 * (self.tyreTempMaxHue + self.tyreTempMinHue)
        self.tyreTempCenter = 70
        self.tyreTempSpread = 16.6667
        self.tyreTempSaturation = 1
        self.tyreTempValue = 1

        self.brakeColorHue = 0
        self.brakeColorSaturation = 1
        self.brakeColorMinValue = 0x22/0xff

        self.brakeMinimumLevel = 0.1

        self.circuitExperienceEndPointPurgeDistance = 15
        self.circuitExperienceShortLapSecondsThreshold = 10
        self.circuitExperienceNoThrottleTimeout = 10
        self.circuitExperienceJumpDistance = 10

        self.validLapEndpointDistance = 20

        self.fuelStatisticsLaps = 5
        self.fuelLastLapFactor = 0.667

        self.messageDisplayDistance = 100
        self.messageAdvanceTime = 5
        self.messageBlinkingPhase = 100000

        self.mapCurrentColor = QColor("#F00")
        self.mapStandingColor = QColor("#000")

        self.speedDiffMinHue = 0
        self.speedDiffMaxHue = 120/360
        self.speedDiffCenterHue = 0.5 * (self.speedDiffMaxHue + self.speedDiffMinHue)
        self.speedDiffColorSaturation = 1
        self.speedDiffColorValue = 1
        self.speedDiffSpread = 10

        self.closestPointValidDistance = 15
        self.closestPointGetAwayDistance = 20
        self.closestPointCancelSearchDistance = 500

        self.pollInterval = 20

        self.fontScale = 1

        self.fontSizeSmallPreset = 48
        self.fontSizeNormalPreset = 64
        self.fontSizeLargePreset = 72

        self.psFPS = 59.94

        if os.path.exists("gt7speedboardinternals.json"):
            with open("gt7speedboardinternals.json", "r") as f:
                j = f.read()
            d = json.loads(j)

            if "foregroundColor" in d: self.foregroundColor = QColor(d["foregroundColor"])
            if "backgroundColor" in d: self.backgroundColor = QColor(d["backgroundColor"])
            if "brightBackgroundColor" in d: self.brightBackgroundColor = QColor(d["brightBackgroundColor"])

            if "warningColor1" in d: self.warningColor1 = QColor(d["warningColor1"])
            if "warningColor2" in d: self.warningColor2 = QColor(d["warningColor2"])
            if "advanceWarningColor" in d: self.advanceWarningColor = QColor(d["advanceWarningColor"])

            if "countdownColor3" in d: self.countdownColor3 = QColor(d["countdownColor3"])
            if "countdownColor2" in d: self.countdownColor2 = QColor(d["countdownColor2"])
            if "countdownColor1" in d: self.countdownColor1 = QColor(d["countdownColor1"])

            if "tyreTempMinHue" in d: self.tyreTempMinHue = d["tyreTempMinHue"]
            if "tyreTempMaxHue" in d: self.tyreTempMaxHue = d["tyreTempMaxHue"]
            if "tyreTempCenterHue" in d: self.tyreTempCenterHue = d["tyreTempCenterHue"]
            if "tyreTempCenter" in d: self.tyreTempCenter = d["tyreTempCenter"]
            if "tyreTempSpread" in d: self.tyreTempSpread = d["tyreTempSpread"]
            if "tyreTempSaturation" in d: self.tyreTempSaturation = d["tyreTempSaturation"]
            if "tyreTempValue" in d: self.tyreTempValue = d["tyreTempValue"]

            if "brakeColorHue" in d: self.brakeColorHue = d["brakeColorHue"]
            if "brakeColorSaturation" in d: self.brakeColorSaturation = d["brakeColorSaturation"]
            if "brakeColorMinValue" in d: self.brakeColorMinValue = d["brakeColorMinValue"]

            if "brakeMinimumLevel" in d: self.brakeMinimumLevel = d["brakeMinimumLevel"]

            if "circuitExperienceEndPointPurgeDistance" in d: self.circuitExperienceEndPointPurgeDistance = d["circuitExperienceEndPointPurgeDistance"]
            if "circuitExperienceShortLapSecondsThreshold" in d: self.circuitExperienceShortLapSecondsThreshold = d["circuitExperienceShortLapSecondsThreshold"]
            if "circuitExperienceNoThrottleTimeout" in d: self.circuitExperienceNoThrottleTimeout = d["circuitExperienceNoThrottleTimeout"]
            if "circuitExperienceJumpDistance" in d: self.circuitExperienceJumpDistance = d["circuitExperienceJumpDistance"]

            if "validLapEndpointDistance" in d: self.validLapEndpointDistance = d["validLapEndpointDistance"]

            if "fuelStatisticsLaps" in d: self.fuelStatisticsLaps = d["fuelStatisticsLaps"]
            if "fuelLastLapFactor" in d: self.fuelLastLapFactor = d["fuelLastLapFactor"]

            if "messageDisplayDistance" in d: self.messageDisplayDistance = d["messageDisplayDistance"]
            if "messageAdvanceTime" in d: self.messageAdvanceTime = d["messageAdvanceTime"]
            if "messageBlinkingPhase" in d: self.messageBlinkingPhase = d["messageBlinkingPhase"]

            if "mapCurrentColor" in d: self.mapCurrentColor = QColor(d["mapCurrentColor"])
            if "mapStandingColor" in d: self.mapStandingColor = QColor(d["mapStandingColor"])

            if "speedDiffMinHue" in d: self.speedDiffMinHue = d["speedDiffMinHue"]
            if "speedDiffMaxHue" in d: self.speedDiffMaxHue = d["speedDiffMaxHue"]
            if "speedDiffCenterHue" in d: self.speedDiffCenterHue = d["speedDiffCenterHue"]
            if "speedDiffColorSaturation" in d: self.speedDiffColorSaturation = d["speedDiffColorSaturation"]
            if "speedDiffColorValue" in d: self.speedDiffColorValue = d["speedDiffColorValue"]
            if "speedDiffSpread" in d: self.speedDiffSpread = d["speedDiffSpread"]

            if "closestPointValidDistance" in d: self.closestPointValidDistance = d["closestPointValidDistance"]
            if "closestPointGetAwayDistance" in d: self.closestPointGetAwayDistance = d["closestPointGetAwayDistance"]
            if "closestPointCancelSearchDistance" in d: self.closestPointCancelSearchDistance = d["closestPointCancelSearchDistance"]

            if "pollInterval" in d: self.pollInterval = d["pollInterval"]

            #if "fontScale" in d: self.fontScale = d["fontScale"]
            if "fontSizeSmall" in d: self.fontSizeSmallPreset = d["fontSizeSmall"]
            if "fontSizeNormal" in d: self.fontSizeNormalPreset = d["fontSizeNormal"]
            if "fontSizeLarge" in d: self.fontSizeLargePreset = d["fontSizeLarge"]

            if "playStationFPS" in d: self.psFPS = d["playStationFPS"]

        if False: # write default file, only activate on demand
            d = {}
            d["foregroundColor"] = self.foregroundColor.name()
            d["backgroundColor"] = self.backgroundColor.name()
            d["brightBackgroundColor"] = self.brightBackgroundColor.name()

            d["warningColor1"] = self.warningColor1.name()
            d["warningColor2"] = self.warningColor2.name()
            d["advanceWarningColor"] = self.advanceWarningColor.name()

            d["countdownColor3"] = self.countdownColor3.name()
            d["countdownColor2"] = self.countdownColor2.name()
            d["countdownColor1"] = self.countdownColor1.name()

            d["tyreTempMinHue"] = self.tyreTempMinHue
            d["tyreTempMaxHue"] = self.tyreTempMaxHue
            d["tyreTempCenterHue"] = self.tyreTempCenterHue
            d["tyreTempCenter"] = self.tyreTempCenter
            d["tyreTempSpread"] = self.tyreTempSpread
            d["tyreTempSaturation"] = self.tyreTempSaturation
            d["tyreTempValue"] = self.tyreTempValue

            d["brakeColorHue"] = self.brakeColorHue
            d["brakeColorSaturation"] = self.brakeColorSaturation
            d["brakeColorMinValue"] = self.brakeColorMinValue

            d["brakeMinimumLevel"] = self.brakeMinimumLevel

            d["circuitExperienceEndPointPurgeDistance"] = self.circuitExperienceEndPointPurgeDistance
            d["circuitExperienceShortLapSecondsThreshold"] = self.circuitExperienceShortLapSecondsThreshold
            d["circuitExperienceNoThrottleTimeout"] = self.circuitExperienceNoThrottleTimeout
            d["circuitExperienceJumpDistance"] = self.circuitExperienceJumpDistance

            d["validLapEndpointDistance"] = self.validLapEndpointDistance

            d["fuelStatisticsLaps"] = self.fuelStatisticsLaps
            d["fuelLastLapFactor"] = self.fuelLastLapFactor

            d["messageDisplayDistance"] = self.messageDisplayDistance
            d["messageAdvanceTime"] = self.messageAdvanceTime
            d["messageBlinkingPhase"] = self.messageBlinkingPhase

            d["mapCurrentColor"] = self.mapCurrentColor.name()
            d["mapStandingColor"] = self.mapStandingColor.name()

            d["speedDiffMinHue"] = self.speedDiffMinHue
            d["speedDiffMaxHue"] = self.speedDiffMaxHue
            d["speedDiffCenterHue"] = self.speedDiffCenterHue
            d["speedDiffColorSaturation"] = self.speedDiffColorSaturation
            d["speedDiffColorValue"] = self.speedDiffColorValue
            d["speedDiffSpread"] = self.speedDiffSpread

            d["closestPointValidDistance"] = self.closestPointValidDistance
            d["closestPointGetAwayDistance"] = self.closestPointGetAwayDistance
            d["closestPointCancelSearchDistance"] = self.closestPointCancelSearchDistance

            d["pollInterval"] = self.pollInterval

            #d["fontScale"] = self.fontScale
            d["fontSizeSmall"] = self.fontSizeSmallPreset
            d["fontSizeNormal"] = self.fontSizeNormalPreset
            d["fontSizeLarge"] = self.fontSizeLargePreset

            d["playStationFPS"] = self.psFPS
            
            j = json.dumps(d, indent=4)
            with open("gt7speedboardinternals.json", "w") as f:
                f.write(j)


    def makeDashWidget(self):
        self.components = []

        # Lvl 4
        self.pedalBest = QLabel("")
        self.pedalBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalBest.setAutoFillBackground(True)
        font = self.pedalBest.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.pedalBest.setFont(font)
        pal = self.pedalBest.palette()
        pal.setColor(self.pedalBest.backgroundRole(), self.backgroundColor)
        pal.setColor(self.pedalBest.foregroundRole(), self.foregroundColor)
        self.pedalBest.setPalette(pal)

        self.speedBest = QLabel("BEST")
        self.speedBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedBest.setAutoFillBackground(True)
        font = self.speedBest.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.speedBest.setFont(font)
        pal = self.speedBest.palette()
        pal.setColor(self.speedBest.backgroundRole(), self.backgroundColor)
        pal.setColor(self.speedBest.foregroundRole(), self.foregroundColor)
        self.speedBest.setPalette(pal)

        self.lineBest = LineDeviation()
        self.timeDiffBest = TimeDeviation()

        self.pedalLast = QLabel("")
        self.pedalLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalLast.setAutoFillBackground(True)
        font = self.pedalLast.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.pedalLast.setFont(font)
        pal = self.pedalLast.palette()
        pal.setColor(self.pedalLast.backgroundRole(), self.backgroundColor)
        pal.setColor(self.pedalLast.foregroundRole(), self.foregroundColor)
        self.pedalLast.setPalette(pal)

        self.speedLast = QLabel("LAST")
        self.speedLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLast.setAutoFillBackground(True)
        font = self.speedLast.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.speedLast.setFont(font)
        pal = self.speedLast.palette()
        pal.setColor(self.speedLast.backgroundRole(), self.backgroundColor)
        pal.setColor(self.speedLast.foregroundRole(), self.foregroundColor)
        self.speedLast.setPalette(pal)

        self.lineLast = LineDeviation()
        self.timeDiffLast = TimeDeviation()

        self.pedalRefA = QLabel("")
        self.pedalRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefA.setAutoFillBackground(True)
        font = self.pedalRefA.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.pedalRefA.setFont(font)
        pal = self.pedalRefA.palette()
        pal.setColor(self.pedalRefA.backgroundRole(), self.backgroundColor)
        pal.setColor(self.pedalRefA.foregroundRole(), self.foregroundColor)
        self.pedalRefA.setPalette(pal)

        self.speedRefA = QLabel("REF A")
        self.speedRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefA.setAutoFillBackground(True)
        font = self.speedRefA.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.speedRefA.setFont(font)
        pal = self.speedRefA.palette()
        pal.setColor(self.speedRefA.backgroundRole(), self.backgroundColor)
        pal.setColor(self.speedRefA.foregroundRole(), self.foregroundColor)
        self.speedRefA.setPalette(pal)

        self.lineRefA = LineDeviation()
        self.timeDiffRefA = TimeDeviation()

        self.pedalRefB = QLabel("")
        self.pedalRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefB.setAutoFillBackground(True)
        font = self.pedalRefB.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.pedalRefB.setFont(font)
        pal = self.pedalRefB.palette()
        pal.setColor(self.pedalRefB.backgroundRole(), self.backgroundColor)
        pal.setColor(self.pedalRefB.foregroundRole(), self.foregroundColor)
        self.pedalRefB.setPalette(pal)

        self.speedRefB = QLabel("REF B")
        self.speedRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefB.setAutoFillBackground(True)
        font = self.speedRefB.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.speedRefB.setFont(font)
        pal = self.speedRefB.palette()
        pal.setColor(self.speedRefB.backgroundRole(), self.backgroundColor)
        pal.setColor(self.speedRefB.foregroundRole(), self.foregroundColor)
        self.speedRefB.setPalette(pal)

        self.lineRefB = LineDeviation()
        self.timeDiffRefB = TimeDeviation()

        self.pedalRefC = QLabel("")
        self.pedalRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefC.setAutoFillBackground(True)
        font = self.pedalRefC.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.pedalRefC.setFont(font)
        pal = self.pedalRefC.palette()
        pal.setColor(self.pedalRefC.backgroundRole(), self.backgroundColor)
        pal.setColor(self.pedalRefC.foregroundRole(), self.foregroundColor)
        self.pedalRefC.setPalette(pal)

        self.speedRefC = QLabel("REF C")
        self.speedRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefC.setAutoFillBackground(True)
        font = self.speedRefC.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.speedRefC.setFont(font)
        pal = self.speedRefC.palette()
        pal.setColor(self.speedRefC.backgroundRole(), self.backgroundColor)
        pal.setColor(self.speedRefC.foregroundRole(), self.foregroundColor)
        self.speedRefC.setPalette(pal)

        self.lineRefC = LineDeviation()
        self.timeDiffRefC = TimeDeviation()

        self.pedalMedian = QLabel("")
        self.pedalMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalMedian.setAutoFillBackground(True)
        font = self.pedalMedian.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.pedalMedian.setFont(font)
        pal = self.pedalMedian.palette()
        pal.setColor(self.pedalMedian.backgroundRole(), self.backgroundColor)
        pal.setColor(self.pedalMedian.foregroundRole(), self.foregroundColor)
        self.pedalMedian.setPalette(pal)

        self.speedMedian = QLabel("MEDIAN")
        self.speedMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedMedian.setAutoFillBackground(True)
        font = self.speedMedian.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.speedMedian.setFont(font)
        pal = self.speedMedian.palette()
        pal.setColor(self.speedMedian.backgroundRole(), self.backgroundColor)
        pal.setColor(self.speedMedian.foregroundRole(), self.foregroundColor)
        self.speedMedian.setPalette(pal)

        self.lineMedian = LineDeviation()
        self.timeDiffMedian = TimeDeviation()

        self.pedalOptimized = QLabel("")
        self.pedalOptimized.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalOptimized.setAutoFillBackground(True)
        font = self.pedalOptimized.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.pedalOptimized.setFont(font)
        pal = self.pedalOptimized.palette()
        pal.setColor(self.pedalOptimized.backgroundRole(), self.backgroundColor)
        pal.setColor(self.pedalOptimized.foregroundRole(), self.foregroundColor)
        self.pedalOptimized.setPalette(pal)

        self.speedOptimized = QLabel("OPT")
        self.speedOptimized.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedOptimized.setAutoFillBackground(True)
        font = self.speedOptimized.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.speedOptimized.setFont(font)
        pal = self.speedOptimized.palette()
        pal.setColor(self.speedOptimized.backgroundRole(), self.backgroundColor)
        pal.setColor(self.speedOptimized.foregroundRole(), self.foregroundColor)
        self.speedOptimized.setPalette(pal)

        self.lineOptimized = LineDeviation()
        self.timeDiffOptimized = TimeDeviation()

        # Lvl 3
        if self.circuitExperience:
            mapCEComponent = sb.components.mapce.MapCE(self, self)
            self.components.append(mapCEComponent)
            self.mapViewCE = mapCEComponent.getWidget()
        else:
            fuelComponent = sb.components.fuelandmessages.FuelAndMessages(self, self)
            self.components.append(fuelComponent)
            fuelWidget = fuelComponent.getWidget()

        tyreComponent = sb.components.tyretemps.TyreTemps(self, self)
        self.components.append(tyreComponent)
        tyreWidget = tyreComponent.getWidget()

        speedWidget = QWidget()
        speedLayout = QGridLayout()
        speedWidget.setLayout(speedLayout)
        if self.showBestLap:
            speedLayout.addWidget(self.speedBest, 2, 0)
        if self.showMedianLap:
            speedLayout.addWidget(self.speedMedian, 2, 1)
        if self.showRefALap:
            speedLayout.addWidget(self.speedRefA, 2, 2)
        if self.showRefBLap:
            speedLayout.addWidget(self.speedRefB, 2, 3)
        if self.showRefCLap:
            speedLayout.addWidget(self.speedRefC , 2, 4)
        if self.showLastLap:
            speedLayout.addWidget(self.speedLast, 2, 5)
        if self.showOptimalLap:
            speedLayout.addWidget(self.speedOptimized, 2, 6)

        if self.linecomp:
            if self.showBestLap:
                speedLayout.addWidget(self.lineBest, 1, 0)
            if self.showMedianLap:
                speedLayout.addWidget(self.lineMedian, 1, 1)
            if self.showRefALap:
                speedLayout.addWidget(self.lineRefA, 1, 2)
            if self.showRefBLap:
                speedLayout.addWidget(self.lineRefB, 1, 3)
            if self.showRefCLap:
                speedLayout.addWidget(self.lineRefC, 1, 4)
            if self.showLastLap:
                speedLayout.addWidget(self.lineLast, 1, 5)
            if self.showOptimalLap:
                speedLayout.addWidget(self.lineOptimized, 1, 6)
            speedLayout.setRowStretch(1, 1)
        if self.timecomp:
            speedLayout.setRowStretch(3, 6)
            if self.showBestLap:
                speedLayout.addWidget(self.timeDiffBest, 3, 0)
            if self.showMedianLap:
                speedLayout.addWidget(self.timeDiffMedian, 3, 1)
            if self.showRefALap:
                speedLayout.addWidget(self.timeDiffRefA, 3, 2)
            if self.showRefBLap:
                speedLayout.addWidget(self.timeDiffRefB, 3, 3)
            if self.showRefCLap:
                speedLayout.addWidget(self.timeDiffRefC, 3, 4)
            if self.showLastLap:
                speedLayout.addWidget(self.timeDiffLast, 3, 5)
            if self.showOptimalLap:
                speedLayout.addWidget(self.timeDiffOptimized, 3, 6)

        if self.brakepoints or self.throttlepoints:
            if self.showBestLap:
                speedLayout.addWidget(self.pedalBest, 0, 0)
            if self.showMedianLap:
                speedLayout.addWidget(self.pedalMedian, 0, 1)
            if self.showRefALap:
                speedLayout.addWidget(self.pedalRefA, 0, 2)
            if self.showRefBLap:
                speedLayout.addWidget(self.pedalRefB, 0, 3)
            if self.showRefCLap:
                speedLayout.addWidget(self.pedalRefC, 0, 4)
            if self.showLastLap:
                speedLayout.addWidget(self.pedalLast, 0, 5)
            if self.showOptimalLap:
                speedLayout.addWidget(self.pedalOptimized, 0, 6)
            speedLayout.setRowStretch(0, 1)
        speedLayout.setRowStretch(2, 4)

        # Lvl 2
        headerComponent = sb.components.lapheader.LapHeader(self, self)
        self.components.append(headerComponent)
        self.header = headerComponent.getWidget()

        if not self.circuitExperience:
            headerFuel = QLabel("FUEL")
        else:
            headerFuel = QLabel("MAP")
        font = headerFuel.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        headerFuel.setFont(font)
        headerFuel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pal = headerFuel.palette()
        pal.setColor(headerFuel.backgroundRole(), self.backgroundColor)
        pal.setColor(headerFuel.foregroundRole(), self.foregroundColor)
        headerFuel.setPalette(pal)

        headerTyres = QLabel("TYRES")
        font = headerTyres.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        headerTyres.setFont(font)
        headerTyres.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pal = headerTyres.palette()
        pal.setColor(headerTyres.backgroundRole(), self.backgroundColor)
        pal.setColor(headerTyres.foregroundRole(), self.foregroundColor)
        headerTyres.setPalette(pal)

        self.headerSpeed = QLabel("SPEED")
        font = self.headerSpeed.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.headerSpeed.setFont(font)
        self.headerSpeed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.headerSpeed.setAutoFillBackground(True)
        pal = self.headerSpeed.palette()
        pal.setColor(self.headerSpeed.foregroundRole(), self.foregroundColor)
        self.headerSpeed.setPalette(pal)

        # Lvl 1
        masterLayout = QGridLayout()
        self.masterWidget = QStackedWidget()
        self.dashWidget = QWidget()
        self.masterWidget.addWidget(self.dashWidget)

        self.uiMsgPageScroller = QScrollArea()
        self.uiMsg = QLabel("Welcome to Speedboard for GT7")
        self.uiMsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uiMsg.setAutoFillBackground(True)
        font = self.uiMsg.font()
        font.setPointSize(self.fontSizeNormal)
        font.setBold(True)
        self.uiMsg.setFont(font)
        pal = self.uiMsg.palette()
        pal.setColor(self.uiMsg.foregroundRole(), self.foregroundColor)
        self.uiMsg.setPalette(pal)

        self.uiMsgPageScroller.setWidget(self.uiMsg)
        self.uiMsgPageScroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.uiMsgPageScroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.uiMsgPageScroller.setWidgetResizable(True)

        self.statsPageScroller = QScrollArea()
        self.statsPage = QLabel(self.sessionName + "\nSession stats not available, yet")

        self.statsPageScroller.setWidget(self.statsPage)
        #self.statsPageScroller.setSizeAdjustPolicy(Qt.QAbstractScrollArea.AdjustToContents)
        self.statsPageScroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.statsPageScroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.statsPageScroller.setWidgetResizable(True)

        self.statsPage.setMargin(15)
        self.statsPage.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.statsPage.setAutoFillBackground(True)
        font = self.statsPage.font()
        font.setPointSize(self.fontSizeSmall)
        font.setBold(True)
        self.statsPage.setFont(font)
        self.statsPage.setTextFormat(Qt.TextFormat.RichText)
        pal = self.statsPage.palette()
        pal.setColor(self.statsPage.foregroundRole(), self.foregroundColor)
        self.statsPage.setPalette(pal)
        self.liveStats = ""
        self.runStats = ""

        self.masterWidget.addWidget(self.uiMsgPageScroller)
        self.masterWidget.addWidget(self.statsPageScroller)

        self.dashWidget.setLayout(masterLayout)

        masterLayout.setColumnStretch(0, 1)
        masterLayout.setColumnStretch(1, 1)
        masterLayout.setRowStretch(0, 1)
        masterLayout.setRowStretch(1, 1)
        masterLayout.setRowStretch(2, 10)
        masterLayout.setRowStretch(3, 1)
        masterLayout.setRowStretch(4, 4)
        masterLayout.addWidget(self.header, 0, 0, 1, 2)
        masterLayout.addWidget(headerFuel, 1, 1, 1, 1)
        masterLayout.addWidget(headerTyres, 3, 0, 1, 1)
        masterLayout.addWidget(self.headerSpeed, 1, 0, 1, 1)
        if self.circuitExperience:
            masterLayout.addWidget(self.mapViewCE, 2, 1, 3, 1)
        else:
            masterLayout.addWidget(fuelWidget, 2, 1, 3, 1)

        masterLayout.addWidget(tyreWidget, 4, 0, 1, 1)

        masterLayout.addWidget(speedWidget, 2, 0, 1, 1)

        pal = self.palette()
        pal.setColor(self.backgroundRole(), self.brightBackgroundColor)
        self.setPalette(pal)

    def startDash(self):
        self.circuitExperience = self.startWindow.mode.currentIndex() == 1

        if self.circuitExperience:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Are you sure you want to start in Circuit Experience Mode?")
            msg.setInformativeText("Circuit Experience Mode is experimental and causes unexpected behavior when used in normal races.")
            msg.setWindowTitle("Circuit Experience")
            msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            retval = msg.exec()
            if retval == QMessageBox.StandardButton.No:
                return

        ip = self.startWindow.ip.text()

        self.lapDecimals = self.startWindow.lapDecimals.isChecked()
        self.showOptimalLap = self.startWindow.cbOptimal.isChecked()
        self.showBestLap = self.startWindow.cbBest.isChecked()
        self.showMedianLap = self.startWindow.cbMedian.isChecked()
        self.showRefALap = self.startWindow.cbRefA.isChecked()
        self.refAFile = self.startWindow.refAFile
        self.showRefBLap = self.startWindow.cbRefB.isChecked()
        self.refBFile = self.startWindow.refBFile
        self.showRefCLap = self.startWindow.cbRefC.isChecked()
        self.refCFile = self.startWindow.refCFile
        self.showLastLap = self.startWindow.cbLast.isChecked()

        self.recordingEnabled = self.startWindow.recordingEnabled.isChecked()
        self.messagesEnabled = self.startWindow.messagesEnabled.isChecked()
        self.sessionName = self.startWindow.sessionName.text()
        saveSessionName = self.startWindow.saveSessionName.isChecked()
        self.storageLocation = self.startWindow.storageLocation
        
        self.linecomp = self.startWindow.linecomp.isChecked()
        self.timecomp = self.startWindow.timecomp.isChecked()
        self.loadMessagesFromFile = self.startWindow.cbCaution.isChecked()
        self.messageFile = self.startWindow.cautionFile
        
        self.brakepoints = self.startWindow.brakepoints.isChecked()
        self.throttlepoints = self.startWindow.throttlepoints.isChecked()
        self.countdownBrakepoint = self.startWindow.countdownBrakepoint.isChecked()
        self.bigCountdownBrakepoint = self.startWindow.bigCountdownTarget.currentIndex()
        self.initialBigCountdownBrakepoint = self.bigCountdownBrakepoint
        self.switchToBestLap = self.startWindow.switchToBestLap.isChecked()
        
        self.fuelMultiplier = self.startWindow.fuelMultiplier.value()
        self.maxFuelConsumption = self.startWindow.maxFuelConsumption.value()
        self.fuelWarning = self.startWindow.fuelWarning.value()

        self.fontScale = self.startWindow.fontScale.value()

        self.fontSizeSmall = int(round(self.fontSizeSmallPreset * self.fontScale))
        self.fontSizeNormal = int(round(self.fontSizeNormalPreset * self.fontScale))
        self.fontSizeLarge = int(round(self.fontSizeLargePreset * self.fontScale))

        
        if not os.path.exists(self.storageLocation):
            QMessageBox.critical(self, "Cannot start", "Storage location not found. Please choose a storage location before starting.")
            return

        if self.refAFile != "" and not os.path.exists(self.refAFile):
            QMessageBox.critical(self, "File not found", "Reference lap A not found. Please choose a file or disable the reference lap A.")
            return

        if self.refBFile != "" and not os.path.exists(self.refBFile):
            QMessageBox.critical(self, "File not found", "Reference lap B not found. Please choose a file or disable the reference lap B.")
            return

        if self.refCFile != "" and not os.path.exists(self.refCFile):
            QMessageBox.critical(self, "File not found", "Reference lap C not found. Please choose a file or disable the reference lap C.")
            return

        settings = QSettings()

        settings.setValue("mode", self.startWindow.mode.currentIndex())
        
        settings.setValue("ip", ip)
        

        settings.setValue("fontScale", self.fontScale)
        settings.setValue("lapDecimals", self.lapDecimals)
        settings.setValue("showOptimalLap", self.showOptimalLap)
        settings.setValue("showBestLap", self.showBestLap)
        settings.setValue("showMedianLap", self.showMedianLap)
        settings.setValue("showLastLap", self.showLastLap)

        settings.setValue("showRefALap", self.showRefALap)
        settings.setValue("showRefBLap", self.showRefBLap)
        settings.setValue("showRefCLap", self.showRefCLap)
        settings.setValue("refAFile", self.refAFile)
        settings.setValue("refBFile", self.refBFile)
        settings.setValue("refCFile", self.refCFile)
        
        settings.setValue("recordingEnabled", self.recordingEnabled)
        settings.setValue("messagesEnabled", self.messagesEnabled)
        settings.setValue("saveSessionName", saveSessionName)
        if saveSessionName:
            settings.setValue("sessionName", self.sessionName)
        else:
            settings.setValue("sessionName", "")
        settings.setValue("storageLocation", self.storageLocation)

        settings.setValue("linecomp", self.linecomp)
        settings.setValue("timecomp", self.timecomp)
        settings.setValue("loadMessagesFromFile", self.loadMessagesFromFile)
        settings.setValue("messageFile", self.messageFile)

        settings.setValue("brakepoints", self.brakepoints)
        settings.setValue("throttlepoints", self.throttlepoints)
        settings.setValue("countdownBrakepoint", self.countdownBrakepoint)
        settings.setValue("bigCountdownTarget", self.bigCountdownBrakepoint)
        settings.setValue("switchToBestLap", self.switchToBestLap)

        settings.setValue("fuelMultiplier", self.startWindow.fuelMultiplier.value())
        settings.setValue("maxFuelConsumption", self.startWindow.maxFuelConsumption.value())
        settings.setValue("fuelWarning", self.startWindow.fuelWarning.value())

        settings.sync()

        self.makeDashWidget()
        self.setCentralWidget(self.masterWidget)

        self.brakeOffset = 0
        self.lapOffset = 0

        self.initRace()
        self.messageWaitsForKey = False

        self.receiver = tele.GT7TelemetryReceiver(ip)

        self.refLaps = [ loadLap(self.refAFile), loadLap(self.refBFile), loadLap(self.refCFile) ]
        self.optimizedLap = Lap()
        self.curOptimizingLap = Lap()
        self.curOptimizingIndex = 0
        self.curOptimizingLiveIndex = 0
        self.curOptimizingBrake = False

        logPrint("Ref A:", msToTime(self.refLaps[0].time))

        self.receiver.setQueue(self.queue)
        self.thread = threading.Thread(target=self.receiver.runTelemetryReceiver)
        self.thread.start()

        if self.goFullscreen:
            self.showFullScreen()
        self.showUiMsg("Press ESC to return to the settings", 2)

        self.trackDetector = TrackDetector()
        self.trackPreviouslyIdentified = "Unknown Track"
        self.trackPreviouslyDescribed = ""
        self.previousPackageId = 0
        self.curLap = None
        self.resetCurrentLapData()

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(self.pollInterval)
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start()

        self.debugCount = 0
        self.noThrottleCount = 0

    def showUiMsg(self, msg, t, leftAlign=False, waitForKey=False):
        logPrint("showUiMsg")
        self.uiMsg.setText(msg)
        if leftAlign:
            self.uiMsg.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.uiMsg.setMargin(15)
        else:
            self.uiMsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.uiMsg.setMargin(0)
        self.masterWidgetIndex = self.masterWidget.currentIndex()
        if self.masterWidgetIndex == 1:
            self.masterWidgetIndex = 0
        self.masterWidget.setCurrentIndex(1)
        if waitForKey:
            self.messageWaitsForKey = True
        else:
            self.messageWaitsForKey = False
            self.returnTimer = QTimer()
            self.returnTimer.setInterval(int(1000 * t))
            self.returnTimer.setSingleShot(True)
            self.returnTimer.timeout.connect(self.returnToDash)
            self.returnTimer.start()


    def returnToDash(self):
        if self.centralWidget() == self.masterWidget:
            self.masterWidget.setCurrentIndex(self.masterWidgetIndex)
            self.masterWidgetIndex = 0

    def stopDash(self):
        if not self.trackDetector is None:
            self.trackDetector.stopDetection()

        if not self.receiver is None:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), self.brightBackgroundColor)
            self.setPalette(pal)

            self.timer.stop()
            self.receiver.running = False
            self.thread.join()
            while not self.queue.empty():
                self.queue.get_nowait()
            self.receiver = None


    def initRun(self):
        logPrint("initRun", self.sessionStats)
        if len(self.sessionStats) > 0 and self.sessionStats[-1].sessionStart == len(self.previousLaps):
            logPrint("Re-using untouched Run")
            return
        self.sessionStats.append (Run(len(self.previousLaps)))

    def markBigCountdownField(self):
        itBest = self.bigCountdownBrakepoint == 1
        itRefA = self.bigCountdownBrakepoint == 2
        itRefB = self.bigCountdownBrakepoint == 3
        itRefC = self.bigCountdownBrakepoint == 4
        itOptimized = self.bigCountdownBrakepoint == 5

        font = self.speedBest.font()
        font.setPointSize(self.fontSizeNormal)
        font.setUnderline(itBest)
        self.speedBest.setFont(font)

        font = self.speedRefA.font()
        font.setPointSize(self.fontSizeNormal)
        font.setUnderline(itRefA)
        self.speedRefA.setFont(font)

        font = self.speedRefB.font()
        font.setPointSize(self.fontSizeNormal)
        font.setUnderline(itRefB)
        self.speedRefB.setFont(font)

        font = self.speedRefC.font()
        font.setPointSize(self.fontSizeNormal)
        font.setUnderline(itRefC)
        self.speedRefC.setFont(font)

        font = self.speedOptimized.font()
        font.setPointSize(self.fontSizeNormal)
        font.setUnderline(itOptimized)
        self.speedOptimized.setFont(font)

    def initRace(self):

        if self.brakeOffset != 0:
            self.headerSpeed.setText("[" + str(round(self.brakeOffset/-60, 2)) + "] SPEED")
        else:
            self.headerSpeed.setText("SPEED")

        self.debugOldLapTime = datetime.datetime.now()
        logPrint("INIT RACE")
        self.newMessage = None
        self.lastLap = -1
        self.lastFuel = -1
        self.lastFuelUsage = []
        self.fuelFactor = 0
        self.refueled = 0
        self.manualPitStop = False
        self.optimizedLap = Lap()
        self.curOptimizingLap = Lap()
        self.curOptimizingIndex = 0
        self.curOptimizingLiveIndex = 0
        self.curOptimizingBrake = False

        self.bigCountdownBrakepoint = self.initialBigCountdownBrakepoint
        self.markBigCountdownField()

        self.newRunDescription = None

        self.previousPoint = None

        self.previousLaps = []
        self.bestLap = -1
        self.medianLap = -1

        pal = self.pedalLast.palette()
        self.pedalLast.setText("")
        pal.setColor(self.pedalLast.backgroundRole(), self.backgroundColor)
        self.pedalLast.setPalette(pal)

        pal = self.pedalBest.palette()
        self.pedalBest.setText("")
        pal.setColor(self.pedalBest.backgroundRole(), self.backgroundColor)
        self.pedalBest.setPalette(pal)

        pal = self.pedalMedian.palette()
        self.pedalMedian.setText("")
        pal.setColor(self.pedalMedian.backgroundRole(), self.backgroundColor)
        self.pedalMedian.setPalette(pal)

        pal = self.pedalRefA.palette()
        self.pedalRefA.setText("")
        pal.setColor(self.pedalRefA.backgroundRole(), self.backgroundColor)
        self.pedalRefA.setPalette(pal)

        pal = self.pedalRefB.palette()
        self.pedalRefB.setText("")
        pal.setColor(self.pedalRefB.backgroundRole(), self.backgroundColor)
        self.pedalRefB.setPalette(pal)

        pal = self.pedalRefC.palette()
        self.pedalRefC.setText("")
        pal.setColor(self.pedalRefC.backgroundRole(), self.backgroundColor)
        self.pedalRefC.setPalette(pal)

        pal = self.pedalOptimized.palette()
        self.pedalOptimized.setText("")
        pal.setColor(self.pedalOptimized.backgroundRole(), self.backgroundColor)
        self.pedalOptimized.setPalette(pal)

        self.lineBest.setPoints(None,None)
        self.lineBest.update()

        self.timeDiffBest.setDiff(0)
        self.timeDiffBest.update()

        self.lineLast.setPoints(None,None)
        self.lineLast.update()

        self.timeDiffLast.setDiff(0)
        self.timeDiffLast.update()

        self.lineMedian.setPoints(None,None)
        self.lineMedian.update()

        self.timeDiffMedian.setDiff(0)
        self.timeDiffMedian.update()

        self.lineRefA.setPoints(None,None)
        self.lineRefA.update()

        self.timeDiffRefA.setDiff(0)
        self.timeDiffRefA.update()

        self.lineRefB.setPoints(None,None)
        self.lineRefB.update()

        self.timeDiffRefB.setDiff(0)
        self.timeDiffRefB.update()

        self.lineRefC.setPoints(None,None)
        self.lineRefC.update()

        self.timeDiffRefC.setDiff(0)
        self.timeDiffRefC.update()

        self.lineOptimized.setPoints(None,None)
        self.lineOptimized.update()

        self.timeDiffOptimized.setDiff(0)
        self.timeDiffOptimized.update()

        self.loadMessages(self.messageFile)

        logPrint("Clear sessions")
        self.sessionStats = []
        self.sessionStart = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.updateRunStats()

    def resetCurrentLapData(self):
        logPrint("Reset cur lap storage") 
        if not self.curLap is None and len(self.curLap.points) > 1:
            logPrint(" Old lap:", len(self.curLap.points))#, self.curLap.distance(self.curLap.points[0], self.curLap.points[-1]), "m")
        self.curLap = Lap()
        self.closestILast = 0
        self.closestIBest = 0
        self.closestIMedian = 0
        self.closestIRefA = 0
        self.closestIRefB = 0
        self.closestIRefC = 0
        self.closestIOptimized = 0
        self.closestPointLast = None
        self.closestPointBest = None
        self.closestPointMedian = None
        self.closestPointRefA = None
        self.closestPointRefB = None
        self.closestPointRefC = None
        self.closestPointOptimized = None
        self.closestOffsetPointLast = None
        self.closestOffsetPointBest = None
        self.closestOffsetPointMedian = None
        self.closestOffsetPointRefA = None
        self.closestOffsetPointRefB = None
        self.closestOffsetPointRefC = None
        self.closestOffsetPointOptimized = None
        self.lapProgress = 0

    def speedDiffQColor(self, d):
        col = QColor()
        hue = self.speedDiffCenterHue - d/(self.speedDiffSpread/self.speedDiffCenterHue) 
        if hue < self.speedDiffMinHue:
            hue = self.speedDiffMinHue
        if hue > self.speedDiffMaxHue:
            hue = self.speedDiffMaxHue
        col.setHsvF (hue, self.speedDiffColorSaturation, self.speedDiffColorValue)

        return col

    def brakeQColor(self, d):
        col = QColor()
        col.setHsvF (self.brakeColorHue, self.brakeColorSaturation, self.brakeColorMinValue + d * (1 - self.brakeColorMinValue)/100)

        return col

    def findClosestPoint(self, lap, p, startIdx):
        shortestDistance = 100000000
        result = None
        for p2 in range(startIdx, len(lap)-10): #TODO why -10? Confusion at the finish line... Maybe do dynamic length
            curDist = p.distance(lap[p2])
            if curDist < self.closestPointValidDistance and curDist < shortestDistance:
                shortestDistance = curDist
                result = p2
            if not result is None and curDist > self.closestPointGetAwayDistance:
                break
            if curDist >= self.closestPointCancelSearchDistance:
                break

        if result is None:
            for p2 in range(100, len(lap)-10, 100):
                curDist = p.distance(lap[p2])
                if curDist < self.closestPointValidDistance:
                    logPrint("Found global position at", p2)
                    startIdx = p2-100
                    break
                
            return None, startIdx, None
        return lap[result], result, lap[min(len(lap)-1, max(0,result+self.brakeOffset))]

    def findClosestPointNoLimit(self, lap, p):
        shortestDistance = 100000000
        result = None
        for p2 in lap:
            curDist = p.distance(p2)
            if curDist < shortestDistance:
                shortestDistance = curDist
                result = p2

        return result

    def findNextBrake(self, lap, startI):
        startI += self.brakeOffset
        for i in range(max(startI,0), min(int(math.ceil(startI + self.psFPS * 3)), len(lap))):
            if lap[i].brake > self.brakeMinimumLevel:
                return max(i-startI,0)
        return None

    #def getLapLength(self, lap):
        #totalDist = 0
        #for i in range(1, len(lap)):
            #totalDist += self.distance(lap[i-1], lap[i])
        #return totalDist

    def purgeBadLapsCE(self):
        logPrint("PURGE laps")
        longestLength = 0
        longestLap = None
        for l in self.previousLaps:
            ll = l.length()
            if longestLength < ll:
                longestLength = ll
                longestLap = l

        if not longestLap is None:
            logPrint("Longest: ", longestLength, longestLap.time)
            temp = []
            for l in self.previousLaps:
                logPrint ("Check lap", l.time)
                d = longestLap.points[-1].distance(l.points[-1])
                c = self.findClosestPointNoLimit(l.points, longestLap.points[-1])
                d2 = -1
                d3 = -1
                if not c is None:
                    d2 = c.distance(longestLap.points[-1])
                c3 = self.findClosestPointNoLimit(longestLap.points, l.points[-1])
                if not c3 is None:
                    d3 = c3.distance(l.points[-1])
                logPrint("End distance:", d)
                if d > self.circuitExperienceEndPointPurgeDistance:
                    logPrint("PURGE lap", indexToTime (len(l.points)), d)
                else:
                    temp.append(l)
            logPrint("OUT")
            self.previousLaps = temp

    def cleanUpLapCE(self, lap):
        logPrint("Input:", len(lap.points))
        if len(lap.points) == 0:
            logPrint("Lap is empty")
            return lap
        if len(lap.points) < self.circuitExperienceShortLapSecondsThreshold * self.psFPS:
            logPrint("\nLap is short")
            return lap
        if (lap.points[-1].throttle > 0):
            logPrint("Throttle to the end")
            return lap
        afterLap = 0
        for i in range(1, len(lap.points)):
            if lap.points[-i].throttle == 0:
                afterLap+=1
            else:
                break
        logPrint("Remove", afterLap, "of", len(lap.points))
        if afterLap > 0:
            result = lap.points[:-afterLap]
        else:
            result = lap.points
        logPrint("Got", len(result))
        return Lap(lap.time, result, lap.valid, preceeding=lap.preceeding)

    def findBestLap(self):
        bestIndex = 0
        bestTime = 100000000.0
        for t in range(len(self.previousLaps)):
            if self.previousLaps[t].valid and self.previousLaps[t].time < bestTime:
                bestTime = self.previousLaps[t].time
                bestIndex = t
        return bestIndex

    def findMedianLap(self):
        sorter = []
        for e in self.previousLaps:
            if e.valid:
                sorter.append(e.time)

        if len(sorter) > 0:
            sorter = sorted(sorter)
            target = sorter[len(sorter)//2]
            for e in range(len(self.previousLaps)):
                if self.previousLaps[e].time == target:
                    return e
        return 0

    def updateStats(self):
        statTxt = '<font size="5">' + self.sessionName + '</font>' + self.liveStats + self.runStats
        self.statsPage.setText(statTxt)


    def updateRunStats(self, saveRuns = False):
        carStatTxt = '<br><font size="3">RUNS:</font><br>'
        carStatCSV = "Run;Valid laps;Car;Best lap;Best lap (ms);Median lap;Median lap (ms);Top speed (km/h);Description\n"
        sessionI = 1
        for i in self.sessionStats:
            if i.carId is None:
                continue
            bst = i.bestLap()
            mdn = i.medianLap()
            lapsWith = " laps with "
            if len(i.lapTimes) == 1:
                lapsWith = " lap with "
            carStatTxt += '<font size="1">R' + str(sessionI) + ": " + str(len(i.lapTimes)) + lapsWith + idToCar(i.carId) + " - Best: " + msToTime(bst[0]) + " | Median: " + msToTime(mdn[0]) + " | Top speed: " + str (round(i.topSpeed, 1)) + ' km/h</font><br><font size="1">' + i.description + "</font>"
            carStatCSV += str(sessionI) + ";" + str(len(i.lapTimes)) + ";" + idToCar(i.carId) + ";" + str(bst[1]) + ";" + str(bst[0]) + ";" + str(mdn[1]) + ";" + str(mdn[0]) + ";" + str(i.topSpeed) + ";" + i.description + "\n"
            sessionI += 1
        if saveRuns:
            prefix = self.storageLocation + "/"
            if len(self.sessionName) > 0:
                prefix += self.sessionName + " - "
            with open ( prefix + self.trackPreviouslyIdentified + " - runs - " + self.sessionStart + ".csv", "w") as f:
                f.write(carStatCSV)
        self.runStats = carStatTxt
        self.updateStats()

    def updateLiveStats(self, curPoint):
        liveStats = '<br><br><font size="3">CURRENT STATS:</font><br><font size="1">'
        liveStats += "Current track: " + self.trackDetector.getTrack() + "<br>"
        liveStats += "Current car: " + idToCar(curPoint.car_id) + "<br>"
        liveStats += "Current lap: " + str(curPoint.current_lap) + "<br>"
        if self.bestLap >= 0 and self.previousLaps[self.bestLap].valid:
            liveStats += "Best lap: " + msToTime (self.previousLaps[self.bestLap].time) + " (est. " + indexToTime (len(self.previousLaps[self.bestLap].points)) + ")<br>"
        if self.medianLap >= 0 and self.previousLaps[self.medianLap].valid:
            liveStats += "Median lap: " + msToTime (self.previousLaps[self.medianLap].time) + "<br>"
        if not self.refLaps[0] is None and self.refLaps[0].time > 0: 
            liveStats += "Reference lap A: " + msToTime (self.refLaps[0].time) + "<br>"
        if not self.refLaps[1] is None and self.refLaps[1].time > 0: 
            liveStats += "Reference lap B: " + msToTime (self.refLaps[1].time) + "<br>"
        if not self.refLaps[2] is None and self.refLaps[2].time > 0: 
            liveStats += "Reference lap C: " + msToTime (self.refLaps[2].time) + "<br>"
        if len(self.optimizedLap.points) > 0:
            self.optimizedLap.updateTime()
            liveStats += "Optimized lap: " + msToTime (self.optimizedLap.time) + "<br>"
        liveStats += "</font>"
        self.liveStats = liveStats
        self.updateStats()


    def updateOneSpeedEntry(self, refLap, curPoint):
        bgPal = self.palette()
        bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.brightBackgroundColor)

        if not refLap.closestPoint is None:
            # SPEED
            speedDiff = refLap.closestPoint.car_speed - curPoint.car_speed
            pal = refLap.speedWidget.palette()
            pal.setColor(refLap.speedWidget.backgroundRole(), self.speedDiffQColor(speedDiff))
            refLap.speedWidget.setPalette(pal)

            # BRAKE POINTS
            if self.throttlepoints or self.brakepoints:
                refLap.pedalWidget.setText("")
                pal = refLap.pedalWidget.palette()
                pal.setColor(refLap.pedalWidget.backgroundRole(), self.backgroundColor)

            if self.throttlepoints:
                if refLap.closestOffsetPoint.throttle > 98:
                    refLap.pedalWidget.setText("GAS")
                    pal.setColor(refLap.pedalWidget.backgroundRole(), QColor("#f2f"))
                    if self.bigCountdownBrakepoint == refLap.id and self.masterWidget.currentIndex() == 0:
                        bgPal.setColor(refLap.pedalWidget.backgroundRole(), QColor("#626"))

            if self.brakepoints:
                if refLap.closestOffsetPoint.brake > 0:
                    refLap.pedalWidget.setText("BRAKE")
                    pal.setColor(refLap.pedalWidget.backgroundRole(), self.brakeQColor(refLap.closestOffsetPoint.brake))
                    if self.bigCountdownBrakepoint == refLap.id and self.masterWidget.currentIndex() == 0:
                        bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.brakeQColor(refLap.closestOffsetPoint.brake))

                elif self.countdownBrakepoint and not refLap.nextBrake is None:
                    refLap.pedalWidget.setText(str(math.ceil (refLap.nextBrake/60)))
                    if refLap.nextBrake >= 120:
                        if refLap.nextBrake%60 >= 30:
                            pal.setColor(refLap.pedalWidget.backgroundRole(), self.countdownColor3)
                            if self.bigCountdownBrakepoint == refLap.id and self.masterWidget.currentIndex() == 0:
                                bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.countdownColor3)
                    elif refLap.nextBrake >= 60:
                        if refLap.nextBrake%60 >= 30:
                            pal.setColor(refLap.pedalWidget.backgroundRole(), self.countdownColor2)
                            if self.bigCountdownBrakepoint == refLap.id and self.masterWidget.currentIndex() == 0:
                                bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.countdownColor2)
                    else:
                        if refLap.nextBrake%30 >= 15:
                            pal.setColor(refLap.pedalWidget.backgroundRole(), self.countdownColor1)
                            if self.bigCountdownBrakepoint == refLap.id and self.masterWidget.currentIndex() == 0:
                                bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.countdownColor1)

            refLap.pedalWidget.setPalette(pal)
            refLap.lineWidget.setPoints(curPoint, refLap.closestPoint)
            refLap.lineWidget.update()

            if self.bigCountdownBrakepoint == refLap.id and self.masterWidget.currentIndex() == 0:
                self.setPalette(bgPal)

            # TIME DIFF
            refLap.timeDiffWidget.setDiff(refLap.closestIndex - len(self.curLap.points))
            refLap.timeDiffWidget.update()
        else:
            pal = refLap.speedWidget.palette()
            pal.setColor(refLap.speedWidget.backgroundRole(), self.backgroundColor)
            refLap.speedWidget.setPalette(pal)
            refLap.pedalWidget.setPalette(pal)
            refLap.pedalWidget.setText("")
            if self.bigCountdownBrakepoint == refLap.id and self.masterWidget.currentIndex() == 0:
                self.setPalette(bgPal)
            refLap.timeDiffWidget.setDiff(0)
            refLap.timeDiffWidget.update()

    def updateSpeed(self, curPoint):
        class SpeedData:
            def __init__(self):
                self.closestPoint = None
                self.closestOffsetPoint = None
                self.nextBrake = None
                self.closestIndex = None
                self.speedWidget = None
                self.pedalWidget = None
                self.lineWidget = None
                self.timeDiffWidget = None
                self.id = None

        best = SpeedData()
        best.closestIndex = self.closestIBest
        best.closestPoint = self.closestPointBest
        best.closestOffsetPoint = self.closestOffsetPointBest
        best.speedWidget = self.speedBest
        best.pedalWidget = self.pedalBest
        best.lineWidget = self.lineBest
        best.timeDiffWidget = self.timeDiffBest
        best.id = 1
             
        median = SpeedData()
        median.closestIndex = self.closestIMedian
        median.closestPoint = self.closestPointMedian
        median.closestOffsetPoint = self.closestOffsetPointMedian
        median.speedWidget = self.speedMedian
        median.pedalWidget = self.pedalMedian
        median.lineWidget = self.lineMedian
        median.timeDiffWidget = self.timeDiffMedian
        median.id = 101
             
        last = SpeedData()
        last.closestIndex = self.closestILast
        last.closestPoint = self.closestPointLast
        last.closestOffsetPoint = self.closestOffsetPointLast
        last.speedWidget = self.speedLast
        last.pedalWidget = self.pedalLast
        last.lineWidget = self.lineLast
        last.timeDiffWidget = self.timeDiffLast
        last.id = 102

        refA = SpeedData()
        refA.closestIndex = self.closestIRefA
        refA.closestPoint = self.closestPointRefA
        refA.closestOffsetPoint = self.closestOffsetPointRefA
        refA.speedWidget = self.speedRefA
        refA.pedalWidget = self.pedalRefA
        refA.lineWidget = self.lineRefA
        refA.timeDiffWidget = self.timeDiffRefA
        refA.id = 2

        refB = SpeedData()
        refB.closestIndex = self.closestIRefB
        refB.closestPoint = self.closestPointRefB
        refB.closestOffsetPoint = self.closestOffsetPointRefB
        refB.speedWidget = self.speedRefB
        refB.pedalWidget = self.pedalRefB
        refB.lineWidget = self.lineRefB
        refB.timeDiffWidget = self.timeDiffRefB
        refB.id = 3
             
        refC = SpeedData()
        refC.closestIndex = self.closestIRefC
        refC.closestPoint = self.closestPointRefC
        refC.closestOffsetPoint = self.closestOffsetPointRefC
        refC.speedWidget = self.speedRefC
        refC.pedalWidget = self.pedalRefC
        refC.lineWidget = self.lineRefC
        refC.timeDiffWidget = self.timeDiffRefC
        refC.id = 4
             
        opti = SpeedData()
        opti.closestIndex = self.closestIOptimized
        opti.closestPoint = self.closestPointOptimized
        opti.closestOffsetPoint = self.closestOffsetPointOptimized
        opti.speedWidget = self.speedOptimized
        opti.pedalWidget = self.pedalOptimized
        opti.lineWidget = self.lineOptimized
        opti.timeDiffWidget = self.timeDiffOptimized
        opti.id = 5
             
        refA.nextBrake = self.findNextBrake(self.refLaps[0].points, refA.closestIndex)
        refB.nextBrake = self.findNextBrake(self.refLaps[1].points, refB.closestIndex)
        refC.nextBrake = self.findNextBrake(self.refLaps[2].points, refC.closestIndex)
        opti.nextBrake = self.findNextBrake(self.optimizedLap.points, opti.closestIndex)

        if len(self.previousLaps) > 0 and self.previousLaps[self.bestLap].valid:
            best.nextBrake = self.findNextBrake(self.previousLaps[self.bestLap].points, best.closestIndex)

        pal = self.palette()
        pal.setColor(self.pedalBest.backgroundRole(), self.brightBackgroundColor)
        self.setPalette(pal)

        self.updateOneSpeedEntry(last, curPoint)
        self.updateOneSpeedEntry(refA, curPoint)
        self.updateOneSpeedEntry(refB, curPoint)
        self.updateOneSpeedEntry(refC, curPoint)
        self.updateOneSpeedEntry(best, curPoint)
        self.updateOneSpeedEntry(median, curPoint)
        self.updateOneSpeedEntry(opti, curPoint)

    def handleTrackDetect(self, curPoint):
        self.trackDetector.addPoint(curPoint)

        curTrack = self.trackDetector.getTrack()
        if self.trackPreviouslyDescribed != curTrack:
            if self.trackPreviouslyIdentified != curTrack and self.trackDetector.trackIdentified():
                logPrint("=== Welcome to " + curTrack)
                self.showUiMsg("Welcome to<br>" + curTrack, 1)
                self.trackPreviouslyIdentified = curTrack
                tempLap = self.lastLap
                tempMsg = self.messages
                self.initRace()
                self.lastLap = tempLap
                self.messages = tempMsg
                
            logPrint("Track:", curTrack, "prev:", self.trackPreviouslyIdentified, self.trackPreviouslyDescribed)
            self.trackPreviouslyDescribed = curTrack
            self.updateLiveStats(curPoint)

    def determineLapProgress(self, curPoint):
        self.closestPointRefA, self.closestIRefA, self.closestOffsetPointRefA = self.findClosestPoint (self.refLaps[0].points, curPoint, self.closestIRefA)
        self.closestPointRefB, self.closestIRefB, self.closestOffsetPointRefB = self.findClosestPoint (self.refLaps[1].points, curPoint, self.closestIRefB)
        self.closestPointRefC, self.closestIRefC, self.closestOffsetPointRefC = self.findClosestPoint (self.refLaps[2].points, curPoint, self.closestIRefC)
        self.closestPointOptimized, self.closestIOptimized, self.closestOffsetPointOptimized = self.findClosestPoint (self.optimizedLap.points, curPoint, self.closestIOptimized)
       
        if len(self.previousLaps) > 0:
            self.closestPointLast, self.closestILast, self.closestOffsetPointLast = self.findClosestPoint (self.previousLaps[-1].points, curPoint, self.closestILast)

            if self.bestLap >= 0 and self.previousLaps[self.bestLap].valid:
                self.closestPointBest, self.closestIBest, self.closestOffsetPointBest = self.findClosestPoint (self.previousLaps[self.bestLap].points, curPoint, self.closestIBest)
                self.closestPointMedian, self.closestIMedian, self.closestOffsetPointMedian = self.findClosestPoint (self.previousLaps[self.medianLap].points, curPoint, self.closestIMedian)

        lpBest = -1
        lpA = -1
        lpB = -1
        lpC = -1
        tp = -1

        if self.closestIRefA > 0:
            lpA = self.closestIRefA / len(self.refLaps[0].points)
        if self.closestIRefB > 0:
            lpB = self.closestIRefB / len(self.refLaps[1].points)
        if self.closestIRefC > 0:
            lpC = self.closestIRefC / len(self.refLaps[2].points)

        if self.bestLap >= 0 and self.closestIBest > 0:
            lpBest = self.closestIBest / len(self.previousLaps[self.bestLap].points)

        if self.trackDetector.trackIdentified():
            tp = self.trackDetector.determineTrackProgress(curPoint)
            if self.lapProgress > 0.9 and tp < 0.1:
                tp = 1.0

        if lpBest != -1:
            self.lapProgress = lpBest
        elif lpA != -1:
            self.lapProgress = lpA
        elif lpB != -1:
            self.lapProgress = lpB
        elif lpC != -1:
            self.lapProgress = lpC
        elif tp != -1:
            self.lapProgress = tp

    def optimizeLap(self, curPoint):
        if len(self.optimizedLap.points) == 0:
            self.curOptimizingLap.points.append(curPoint)
            self.curOptimizingLiveIndex = len(self.curLap.points)
            self.curOptimizingIndex = self.closestIOptimized
        else:
            nowBraking = curPoint.brake > 50 or self.optimizedLap.points[self.closestIOptimized].brake > 50
            if nowBraking != self.curOptimizingBrake:
                self.curOptimizingBrake = nowBraking
                if nowBraking:
                    #logPrint(nowBraking, len(self.curOptimizingLap.points), self.curOptimizingIndex, self.curOptimizingLiveIndex)
                    lenOpt = self.closestIOptimized - self.curOptimizingIndex
                    lenLive = len(self.curLap.points) - self.curOptimizingLiveIndex
                    if lenOpt > lenLive:
                        logPrint("Current segment was faster")
                        self.curOptimizingLap.points += self.curLap.points[self.curOptimizingLiveIndex:-1]
                    else:
                        logPrint("Previous segment was faster")
                        self.curOptimizingLap.points += self.optimizedLap.points[self.curOptimizingIndex:self.closestIOptimized-1]
                    self.curOptimizingLiveIndex = len(self.curLap.points)-1
                    self.curOptimizingIndex = self.closestIOptimized-1
                    logPrint("///////",len(self.curLap.points), len(self.curOptimizingLap.points), self.curOptimizingIndex, self.curOptimizingLiveIndex, len(self.optimizedLap.points))

    def updateOptimizedLap(self):
        lenOpt = self.closestIOptimized - self.curOptimizingIndex
        lenLive = len(self.curLap.points) - self.curOptimizingLiveIndex
        if lenOpt > lenLive:
            logPrint("Current segment was faster")
            self.curOptimizingLap.points += self.curLap.points[self.curOptimizingLiveIndex:]
        else:
            logPrint("Previous segment was faster")
            self.curOptimizingLap.points += self.optimizedLap.points[self.curOptimizingIndex:]
        self.optimizedLap = self.curOptimizingLap
        logPrint("Optimized lap:", len(self.optimizedLap.points), "points vs.", len(self.curLap.points))
        self.curOptimizingLap = Lap()
        self.curOptimizingLiveIndex = 0
        self.curOptimizingIndex = 0
        self.curOptimizingBrake = False

    def handleLapChanges(self, curPoint):
        if self.circuitExperienceShortLapSecondsThreshold and curPoint.current_lap > 1:
            logPrint("Not in Circuit Experience!")
            self.exitDash()
            QMessageBox.critical(self, "Not in Circuit Experience", "Circuit Experience mode is set, but not driven. Unfortunately, this is not supported. Please change to Laps mode or drive a Circuit Experience.")
            return
        fuel_capacity = curPoint.fuel_capacity
        if fuel_capacity == 0: # EV
            fuel_capacity = 100

        if (
            self.lastLap != curPoint.current_lap
            or (self.circuitExperience and (curPoint.distance(self.previousPoint) > self.circuitExperienceJumpDistance or self.noThrottleCount >= self.psFPS * self.circuitExperienceNoThrottleTimeout))
           ): # TODO Null error in circuit experience mode when doing laps: AttributeError: 'NoneType' object has no attribute 'position_x'

            # Clean up circuit experience laps
            if self.circuitExperience:
                if self.noThrottleCount >= self.psFPS * self.circuitExperienceNoThrottleTimeout:
                    logPrint("Lap ended", self.circuitExperienceNoThrottleTimeout ,"seconds ago")

                cleanLap = self.cleanUpLapCE(self.curLap)
                self.mapViewCE.endLap(cleanLap.points)
                self.mapViewCE.update()
            else:
                cleanLap = self.curLap
            lapLen = cleanLap.length()
            
            if lapLen == 0:
                logPrint("LAP CHANGE EMPTY")
                return
            # Handle short and "real" laps differently
            if lapLen < 10: # TODO const
                logPrint("LAP CHANGE short", lapLen, self.lastLap, curPoint.current_lap)
            else:
                logPrint("Track Detect Data:", self.trackDetector.totalPoints)
                debugNewLapTime = datetime.datetime.now()
                logPrint("LAP CHANGE", self.lastLap, curPoint.current_lap, str(round(lapLen, 3)) + " m", indexToTime(len (cleanLap.points)), debugNewLapTime - self.debugOldLapTime)
                self.debugOldLapTime = debugNewLapTime
                if curPoint.current_lap == 1 or self.lastLap >= curPoint.current_lap:
                    logPrint("lap is 1 -> init")
                    self.initRun()

            # Update live stats
            self.updateLiveStats(curPoint)

            if not (self.lastLap == -1 and curPoint.current_fuel < 99):
                if self.lastLap > 0 and ((self.circuitExperience and lapLen > 0) or curPoint.last_lap != -1):
                    # Determine lap time
                    if self.circuitExperience:
                        lastLapTime = 1000 * (len(cleanLap.points)/self.psFPS + 1/(2*self.psFPS))
                    else:
                        lastLapTime = curPoint.last_lap

                    showBestLapMessage = True

                    logPrint("Closed loop distance:", cleanLap.points[0].distance(cleanLap.points[-1])) 
                    # Process a completed valid lap (circuit experience laps are always valid)
                    if self.circuitExperience or cleanLap.points[0].distance(cleanLap.points[-1]) < self.validLapEndpointDistance:
                        if len(self.previousLaps) > 0:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, True, following=curPoint, preceeding=self.previousLaps[-1].points[-1]))
                        else:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, True, following=curPoint))

                        # Debug message
                        it = indexToTime(len(cleanLap.points))
                        mst = msToTime(lastLapTime)
                        tdiff = float(it[4:]) - float(mst[mst.index(":")+1:])
                        logPrint("Append valid lap", msToTime(lastLapTime), indexToTime(len(cleanLap.points)), lastLapTime, len(self.previousLaps), tdiff)

                        if not self.circuitExperience:
                            self.updateOptimizedLap()

                        # Check if the full screen color flashing should be for the best lap from now on
                        if self.switchToBestLap:
                            logPrint("Compare ref/best lap", msToTime(curPoint.last_lap), msToTime(self.refLaps[0].time))
                            if self.bigCountdownBrakepoint == 2 and (self.refLaps[0] is None or self.refLaps[0].time > curPoint.last_lap):
                                if not self.refLaps[0] is None:
                                    logPrint("Switch to best lap", msToTime(curPoint.last_lap), msToTime(self.refLaps[0].time))
                                    self.showUiMsg("BEAT REFERENCE LAP", 1)
                                showBestLapMessage = False
                                self.bigCountdownBrakepoint = 1
                                self.markBigCountdownField()
                            elif self.bigCountdownBrakepoint == 3 and (self.refLaps[1] is None or self.refLaps[1].time > curPoint.last_lap):
                                if not self.refLaps[1] is None:
                                    logPrint("Switch to best lap", msToTime(curPoint.last_lap), msToTime(self.refLaps[1].time))
                                    self.showUiMsg("BEAT REFERENCE LAP", 1)
                                showBestLapMessage = False
                                self.bigCountdownBrakepoint = 1
                                self.markBigCountdownField()
                            elif self.bigCountdownBrakepoint == 4 and (self.refLaps[2] is None or self.refLaps[2].time > curPoint.last_lap):
                                if not self.refLaps[2] is None:
                                    logPrint("Switch to best lap", msToTime(curPoint.last_lap), msToTime(self.refLaps[2].time))
                                    self.showUiMsg("BEAT REFERENCE LAP", 1)
                                showBestLapMessage = False
                                self.bigCountdownBrakepoint = 1
                                self.markBigCountdownField()

                        # Update session stats
                        if lastLapTime > 0:
                            if len(self.sessionStats) == 0: # Started app during lap
                                logPrint("no stats --> init")
                                self.initRun()
                            self.sessionStats[-1].carId = curPoint.car_id
                            self.sessionStats[-1].addLapTime(lastLapTime, self.lastLap)
                            pTop = self.previousLaps[-1].topSpeed()
                            if self.sessionStats[-1].topSpeed < pTop:
                                self.sessionStats[-1].topSpeed = pTop
                            logPrint(len(self.sessionStats), "sessions")
                            for i in self.sessionStats:
                                logPrint("Best:", msToTime(i.bestLap()[0]))
                                logPrint("Median:", msToTime(i.medianLap()[0]))

                        self.updateRunStats()
                    else: # Incomplete laps are sometimes useful, but can't be used for everything
                        logPrint("Append invalid lap", msToTime(lastLapTime), indexToTime(len(cleanLap.points)), lastLapTime, len(self.previousLaps))
                        if len(self.previousLaps) > 0:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, False, following=curPoint, preceeding=self.previousLaps[-1].points[-1]))
                        else:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, False, following=curPoint))

                    logPrint("Laps:", len(self.previousLaps))

                    # Clean up circuit experience laps
                    if self.circuitExperience:
                        self.purgeBadLapsCE()
                        logPrint("Laps after purge:", len(self.previousLaps))
                
                    # Reset comparison lap information
                    newBestLap = self.findBestLap()
                    ## Show best lap message
                    if showBestLapMessage and self.bestLap != newBestLap and self.previousLaps[newBestLap].valid:
                        self.showUiMsg("BEST LAP", 1)
                    ## Reset brake point offsets for new best lap
                    if self.bestLap != newBestLap and self.bigCountdownBrakepoint == 1:
                        self.brakeOffset = 0
                        self.headerSpeed.setText("SPEED")
                        self.headerSpeed.update()
                    self.bestLap = newBestLap
                    self.medianLap = self.findMedianLap()

                    self.resetCurrentLapData()

                    logPrint("Best lap:", self.bestLap, msToTime (self.previousLaps[self.bestLap].time), "/", indexToTime(len(self.previousLaps[self.bestLap].points)), "of", len(self.previousLaps))
                    logPrint("Median lap:", self.medianLap, msToTime(self.previousLaps[self.medianLap].time))
                    logPrint("Last lap:", len(self.previousLaps)-1, msToTime (self.previousLaps[-1].time))

                    # Update fuel usage and outlook
                    fuelDiff = self.lastFuel - curPoint.current_fuel/fuel_capacity
                    if fuelDiff > 0:
                        logPrint("Append fuel", fuelDiff)
                        self.lastFuelUsage.append(fuelDiff)
                    if len(self.lastFuelUsage) > self.fuelStatisticsLaps:
                        self.lastFuelUsage = self.lastFuelUsage[1:]
                    self.refueled += 1
                    self.lastFuel = curPoint.current_fuel/fuel_capacity
    
                    if len(self.lastFuelUsage) > 0:
                        self.fuelFactor = self.lastFuelUsage[0]
                        for i in range(1, len(self.lastFuelUsage)):
                            self.fuelFactor = (1-self.fuelLastLapFactor) * self.fuelFactor + self.fuelLastLapFactor * self.lastFuelUsage[i]

                else:
                    logPrint("Ignore pre-lap")
                    self.lastFuel = 1
                    self.resetCurrentLapData()

                # Update live stats
                self.updateLiveStats(curPoint)

            self.lastLap = curPoint.current_lap
            self.curOptimizingLap = Lap()
            self.curOptimizingIndex = 0
            self.curOptimizingLiveIndex = 0
            self.curOptimizingBrake = False
            logPrint("Fuel", self.fuelFactor, self.lastFuel, self.lastFuelUsage)

    def updateDisplay(self):
        # Grab all new telemetry packages
        while not self.queue.empty():
            self.debugCount += 1
            d = self.queue.get()
            newPoint = Point(d[0], d[1])

            # Check for dropped packages
            if not self.previousPoint is None:
                diff = newPoint.package_id - self.previousPackageId
            else:
                diff = 1

            self.previousPackageId = newPoint.package_id

            pointsToHandle = []

            if diff > 10:
                logPrint("Too many frame drops (" + str (diff) + ")! Data will be corrupted.")
                self.trackDetector.reset()
            elif diff > 1:
                logPrint("Frame drops propagated:", diff-1)
                for i in range(diff-1):
                    pi = copy.deepcopy(self.previousPoint)
                    pi.interpolate(newPoint, (i+1)/diff)
                    pointsToHandle.append(pi)

            pointsToHandle.append(newPoint)

            # Handle telemetry
            for curPoint in pointsToHandle:
                # Update local messages
                if self.messagesEnabled and not self.newMessage is None:
                    self.messages.append([self.curLap.points[-min(int(self.psFPS*self.messageAdvanceTime),len(self.curLap.points)-1)], self.newMessage])
                    self.newMessage = None

                # Only handle packages when driving
                if curPoint.is_paused or not curPoint.in_race: # TODO detect replay and allow storing laps from it
                    continue

                self.determineLapProgress(curPoint)

                self.handleLapChanges(curPoint)
                if not self.circuitExperience:
                    self.optimizeLap(curPoint)
                self.updateSpeed(curPoint)
                self.handleTrackDetect(curPoint)

                for c in self.components:
                    c.addPoint(curPoint, self.curLap)
                
                # Update live stats description
                if not self.newRunDescription is None and len(self.sessionStats) > 0:
                    self.sessionStats[-1].description = self.newRunDescription + "<br>"
                    self.newRunDescription = None
                    self.updateRunStats()

                self.previousPoint = curPoint
                self.curLap.points.append(curPoint)


    def closeEvent(self, event):
        self.stopDash()
        event.accept()


    def toggleRecording(self):
        if self.recordingEnabled:
            if self.isRecording:
                self.isRecording = False
                self.receiver.stopRecording()
            else:
                if not os.path.exists(self.storageLocation):
                    self.showUiMsg("Error: Storage location\n'" + self.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist", 2)
                    return
                prefix = self.storageLocation + "/"
                if len(self.sessionName) > 0:
                    prefix += self.sessionName + "-"
                self.receiver.startRecording(prefix)
                self.isRecording = True

    def exitDash(self):
        if self.isRecording:
            self.isRecording = False
            self.receiver.stopRecording()
        self.stopDash()
        self.showNormal()
        self.startWindow = StartWindow()
        self.startWindow.starter.clicked.connect(self.startDash)
        self.startWindow.ip.returnPressed.connect(self.startDash)
        self.setPalette(self.defaultPalette)
        self.setCentralWidget(self.startWindow)

    def keyPressEvent(self, e):
        if self.centralWidget() == self.masterWidget and self.messageWaitsForKey:
            if e.key() != Qt.Key.Key_Shift.value:
                self.messageWaitsForKey = False
                self.returnToDash()
        elif self.centralWidget() == self.masterWidget:
            if e.key() == Qt.Key.Key_R.value:
                self.toggleRecording()
            elif e.key() == Qt.Key.Key_Escape.value:
                self.exitDash()
            elif e.key() == Qt.Key.Key_Space.value:
                self.newMessage = "CAUTION"
            elif e.key() == Qt.Key.Key_B.value:
                if self.bestLap >= 0:
                    saveThread = Worker(self.saveLap, "Best lap saved.", 1.0, (self.bestLap, "best",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_L.value:
                if len(self.previousLaps) > 0:
                    saveThread = Worker(self.saveLap, "Last lap saved.", 1.0, (-1, "last",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_M.value:
                if self.medianLap >= 0:
                    saveThread = Worker(self.saveLap, "Median lap saved.", 1.0, (self.medianLap, "median",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_O.value:
                if len(self.optimizedLap.points) > 0:
                    saveThread = Worker(self.saveOptimizedLap, "Optimized lap saved.", 1.0, (self.optimizedLap, "optimized",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_A.value:
                if len(self.previousLaps) > 0:
                    saveThread = Worker(self.saveAllLaps, "All laps saved.", 1.0, ("combined",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_W.value:
                logPrint("store message positions")
                saveThread = Worker(self.saveMessages, "Messages saved.", 1.0, ())
                saveThread.signals.finished.connect(self.showUiMsg)
                self.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_D.value:
                text, ok = QInputDialog().getText(self, "Set run description", "Description:")
                if ok:
                    self.newRunDescription = text
            elif e.key() == Qt.Key.Key_C.value:
                self.initRace()
            elif e.key() == Qt.Key.Key_P.value:
                self.manualPitStop = True
                self.refueled = 0
                if self.lapProgress > 0.5:
                    self.refueled -= 1
            elif e.key() == Qt.Key.Key_0.value:
                self.brakeOffset = 0
                logPrint("Brake offset", self.brakeOffset)
                self.headerSpeed.setText("SPEED")
                self.headerSpeed.update()
            elif e.key() == Qt.Key.Key_Plus.value:
                self.lapOffset += 1
            elif e.key() == Qt.Key.Key_Minus.value:
                self.lapOffset -= 1
            elif e.key() == Qt.Key.Key_Up.value:
                self.brakeOffset -= 3
                logPrint("Brake offset", self.brakeOffset)
                if self.brakeOffset != 0:
                    self.headerSpeed.setText("[" + str(round(self.brakeOffset/-60, 2)) + "] SPEED")
                else:
                    self.headerSpeed.setText("SPEED")
                self.headerSpeed.update()
            elif e.key() == Qt.Key.Key_Down.value:
                self.brakeOffset += 3
                logPrint("Brake offset", self.brakeOffset)
                if self.brakeOffset != 0:
                    self.headerSpeed.setText("[" + str(round(self.brakeOffset/-60, 2)) + "] SPEED")
                else:
                    self.headerSpeed.setText("SPEED")
                self.headerSpeed.update()
            elif e.key() == Qt.Key.Key_S.value:
                if self.masterWidget.currentIndex() == 2:
                    self.returnToDash()
                else:
                    self.masterWidget.setCurrentIndex(2)
            elif e.key() == Qt.Key.Key_T.value:
                self.updateRunStats(saveRuns=True)
                self.showUiMsg("Run table saved.", 2)
            elif e.key() == Qt.Key.Key_Question:
                self.showUiMsg (shortcutText, 0, leftAlign=True, waitForKey=True)
            #elif e.key() == Qt.Key.Key_T.value:
                #tester = Worker(someDelay, "Complete", 0.2)
                #tester.signals.finished.connect(self.showUiMsg)
                #self.threadpool.start(tester)

    def keyReleaseEvent(self, e):
        if self.centralWidget() == self.masterWidget:
            if e.key() == Qt.Key.Key_Tab.value:
                self.returnToDash()

    def saveAllLaps(self, name):
        logPrint("store all laps:", name)
        if not os.path.exists(self.storageLocation):
            return "Error: Storage location\n'" + self.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        prefix = self.storageLocation + "/"
        if len(self.sessionName) > 0:
            prefix += self.sessionName + " - "
        with open ( prefix + self.trackPreviouslyIdentified + " - laps - " + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7laps", "wb") as f:
            if not self.previousLaps[0].preceeding is None:
                f.write(self.previousLaps[0].preceeding.raw)
            for index in range(len(self.previousLaps)):
                if index > 0 and not self.previousLaps[index].preceeding is None and self.previousLaps[index].preceeding != self.previousLaps[index-1].points[-1]:
                    f.write(self.previousLaps[index].preceeding.raw)
                for p in self.previousLaps[index].points:
                    f.write(p.raw)
                if index < len(self.previousLaps)-1 and not self.previousLaps[index].following is None and self.previousLaps[index].following != self.previousLaps[index+1].points[0]:
                    f.write(self.previousLaps[index].following.raw)
            if not self.previousLaps[-1].following is None:
                f.write(self.previousLaps[-1].following.raw)

    def saveOptimizedLap(self, index, name):
        for p in index.points:
            p.current_lap = 1
            p.recreatePackage()
        self.saveLap(index, name)

    def saveLap(self, index, name):
        logPrint("store lap:", name)
        if not os.path.exists(self.storageLocation):
            return "Error: Storage location\n'" + self.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        prefix = self.storageLocation + "/"
        if len(self.sessionName) > 0:
            prefix += self.sessionName + " - "
        with open ( prefix + self.trackPreviouslyIdentified + " - lap - " + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7lap", "wb") as f:
            if isinstance(index, Lap):
                lap = index
            else:
                lap = self.previousLaps[index]
            if not lap.preceeding is None:
                logPrint("Going from", lap.preceeding.current_lap)
                f.write(lap.preceeding.raw)
            logPrint("via", lap.points[0].current_lap)
            for p in lap.points:
                f.write(p.raw)
            if not lap.following is None:
                logPrint("to", lap.following.current_lap)
                f.write(lap.following.raw)

    def saveMessages(self):
        logPrint("Save messages")
        if not os.path.exists(self.storageLocation):
            return "Error: Storage location\n'" + self.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        d = []
        for m in self.messages:
            d.append({ "X": m[0].position_x, "Y": m[0].position_y, "Z": m[0].position_z, "message" :m[1]})

        j = json.dumps(d, indent=4)
        logPrint(j)
        prefix = self.storageLocation + "/"
        if len(self.sessionName) > 0:
            prefix += self.sessionName + " - "
        with open ( prefix + self.trackPreviouslyIdentified + " - messages - " + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".sblm", "w") as f:
            f.write(j)

    def loadMessages(self, fn):
        self.messages = []
        if self.loadMessagesFromFile:
            with open (fn, "r") as f:
                j = f.read()
                logPrint(j)
                d = json.loads(j)
                logPrint(d)
                for m in d:
                    p = PositionPoint()
                    p.position_x = m['X']
                    p.position_y = m['Y']
                    p.position_z = m['Z']
                    self.messages.append([p, m['message']])
                    logPrint("Message:", m)


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logPrint("=== EXCEPTION ===")
    logPrint("error message:\n", tb)
    with open ("gt7speedboard.log", "a") as f:
        f.write("=== EXCEPTION ===\n")
        f.write(str(datetime.datetime.now ()) + "\n\n")
        f.write(str(tb) + "\n")
    QApplication.quit()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setOrganizationName("pitstop.profittlich.com");
    app.setOrganizationDomain("pitstop.profittlich.com");
    app.setApplicationName("GT7 SpeedBoard");

    window = MainWindow()

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--ip" and i < len(sys.argv)-1:
            window.startWindow.ip.setText(sys.argv[i+1])
            i+=1
        elif sys.argv[i] == "--no-fs":
            window.goFullscreen = False
        elif sys.argv[i] == "--clearsettings":
            settings = QSettings()
            settings.clear()
            settings.sync()
            logPrint("Settings cleared")
            sys.exit(0)
        i+=1
    
    window.show()
    window.startWindow.ip.setFocus()


    sys.excepthook = excepthook
    with keep.presenting():
        app.exec()
        #cProfile.run("app.exec()")



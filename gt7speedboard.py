import sys
import os
import threading
import traceback
import json
from wakepy import keep
import math
import queue
import datetime
from cProfile import Profile
from pstats import SortKey, Stats

from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QSettings
from PyQt6.QtGui import QColor, QRegularExpressionValidator, QPixmap, QPainter, QPalette, QPen, QLinearGradient, QGradient
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox

from gt7telepoint import Point

import gt7telemetryreceiver as tele
from gt7widgets import *

class Lap:
    def __init__(self, time = None, pts = None, valid=True):
        self.time = time
        if pts is None:
            self.points = []
        else:
            self.points = pts
        self.valid = valid

    def distance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_y-p2.position_y)**2 + (p1.position_z-p2.position_z)**2)

    def length(self):
        totalDist = 0
        for i in range(1, len(self.points)):
            totalDist += self.distance(self.points[i-1], self.points[i])
        return totalDist


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.masterWidget = None

        self.startWindow = StartWindow()
        self.startWindow.starter.clicked.connect(self.startDash)
        self.startWindow.ip.returnPressed.connect(self.startDash)

        self.setWindowTitle("GT7 SpeedBoard 1.0")
        self.queue = queue.Queue()
        self.receiver = None
        self.isRecording = False

        self.circuitExperience = True
        self.lapDecimals = False
        self.recordingEnabled = False
        self.messagesEnabled = False
        self.linecomp = False
        self.brakepoints = False
        self.allowLoop = False
        self.countdownBrakepoint = False
        self.bigCountdownBrakepoint = 0

        self.showBestLap = True
        self.showLastLap = True
        self.showMedianLap = True
        self.showRefALap = False
        self.showRefBLap = False
        self.showRefCLap = False
        self.showOptimalLap = False # TODO implement

        self.keepLaps = False

        self.newMessage = None
        self.messages = []

        self.setCentralWidget(self.startWindow)

    def makeDashWidget(self):
        # Lvl 4
        self.fuel = QLabel("?%")
        self.fuel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fuel.setAutoFillBackground(True)
        font = self.fuel.font()
        font.setPointSize(64)
        font.setBold(True)
        self.fuel.setFont(font)

        self.fuelBar = FuelGauge()

        if self.circuitExperience:
            self.mapView = MapView()
        else:
            self.laps = QLabel("? LAPS LEFT")
            self.laps.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.laps.setAutoFillBackground(True)
            font = self.laps.font()
            font.setPointSize(64)
            font.setBold(True)
            self.laps.setFont(font)
            pal = self.laps.palette()
            pal.setColor(self.laps.backgroundRole(), QColor("#222"))
            pal.setColor(self.laps.foregroundRole(), QColor("#fff"))
            self.laps.setPalette(pal)

        self.tyreFR = QLabel("?°C")
        self.tyreFR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFR.setAutoFillBackground(True)
        font = self.tyreFR.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreFR.setFont(font)
        pal = self.tyreFR.palette()
        pal.setColor(self.tyreFR.backgroundRole(), QColor('#222'))
        pal.setColor(self.tyreFR.foregroundRole(), QColor("#fff"))
        self.tyreFR.setPalette(pal)

        self.tyreFL = QLabel("?°C")
        self.tyreFL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFL.setAutoFillBackground(True)
        font = self.tyreFL.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreFL.setFont(font)
        pal = self.tyreFL.palette()
        pal.setColor(self.tyreFL.backgroundRole(), QColor('#222'))
        pal.setColor(self.tyreFL.foregroundRole(), QColor("#fff"))
        self.tyreFL.setPalette(pal)
        
        self.tyreRR = QLabel("?°C")
        self.tyreRR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRR.setAutoFillBackground(True)
        font = self.tyreRR.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreRR.setFont(font)
        pal = self.tyreRR.palette()
        pal.setColor(self.tyreRR.backgroundRole(), QColor('#222'))
        pal.setColor(self.tyreRR.foregroundRole(), QColor("#fff"))
        self.tyreRR.setPalette(pal)

        self.tyreRL = QLabel("?°C")
        self.tyreRL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRL.setAutoFillBackground(True)
        font = self.tyreRL.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreRL.setFont(font)
        pal = self.tyreRL.palette()
        pal.setColor(self.tyreRL.backgroundRole(), QColor('#222'))
        pal.setColor(self.tyreRL.foregroundRole(), QColor("#fff"))
        self.tyreRL.setPalette(pal)

        self.pedalBest = QLabel("")
        self.pedalBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalBest.setAutoFillBackground(True)
        font = self.pedalBest.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalBest.setFont(font)
        pal = self.pedalBest.palette()
        pal.setColor(self.pedalBest.backgroundRole(), QColor('#222'))
        pal.setColor(self.pedalBest.foregroundRole(), QColor("#fff"))
        self.pedalBest.setPalette(pal)

        self.speedBest = QLabel("BEST")
        self.speedBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedBest.setAutoFillBackground(True)
        font = self.speedBest.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedBest.setFont(font)
        pal = self.speedBest.palette()
        pal.setColor(self.speedBest.backgroundRole(), QColor('#222'))
        pal.setColor(self.speedBest.foregroundRole(), QColor("#fff"))
        self.speedBest.setPalette(pal)

        self.lineBest = LineDeviation()

        self.pedalLast = QLabel("")
        self.pedalLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalLast.setAutoFillBackground(True)
        font = self.pedalLast.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalLast.setFont(font)
        pal = self.pedalLast.palette()
        pal.setColor(self.pedalLast.backgroundRole(), QColor('#222'))
        pal.setColor(self.pedalLast.foregroundRole(), QColor("#fff"))
        self.pedalLast.setPalette(pal)

        self.speedLast = QLabel("LAST")
        self.speedLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLast.setAutoFillBackground(True)
        font = self.speedLast.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedLast.setFont(font)
        pal = self.speedLast.palette()
        pal.setColor(self.speedLast.backgroundRole(), QColor('#222'))
        pal.setColor(self.speedLast.foregroundRole(), QColor("#fff"))
        self.speedLast.setPalette(pal)

        self.lineLast = LineDeviation()

        self.pedalRefA = QLabel("")
        self.pedalRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefA.setAutoFillBackground(True)
        font = self.pedalRefA.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalRefA.setFont(font)
        pal = self.pedalRefA.palette()
        pal.setColor(self.pedalRefA.backgroundRole(), QColor('#222'))
        pal.setColor(self.pedalRefA.foregroundRole(), QColor("#fff"))
        self.pedalRefA.setPalette(pal)

        self.speedRefA = QLabel("REF A")
        self.speedRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefA.setAutoFillBackground(True)
        font = self.speedRefA.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedRefA.setFont(font)
        pal = self.speedRefA.palette()
        pal.setColor(self.speedRefA.backgroundRole(), QColor('#222'))
        pal.setColor(self.speedRefA.foregroundRole(), QColor("#fff"))
        self.speedRefA.setPalette(pal)

        self.lineRefA = LineDeviation()

        self.pedalRefB = QLabel("")
        self.pedalRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefB.setAutoFillBackground(True)
        font = self.pedalRefB.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalRefB.setFont(font)
        pal = self.pedalRefB.palette()
        pal.setColor(self.pedalRefB.backgroundRole(), QColor('#222'))
        pal.setColor(self.pedalRefB.foregroundRole(), QColor("#fff"))
        self.pedalRefB.setPalette(pal)

        self.speedRefB = QLabel("REF B")
        self.speedRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefB.setAutoFillBackground(True)
        font = self.speedRefB.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedRefB.setFont(font)
        pal = self.speedRefB.palette()
        pal.setColor(self.speedRefB.backgroundRole(), QColor('#222'))
        pal.setColor(self.speedRefB.foregroundRole(), QColor("#fff"))
        self.speedRefB.setPalette(pal)

        self.lineRefB = LineDeviation()

        self.pedalRefC = QLabel("")
        self.pedalRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefC.setAutoFillBackground(True)
        font = self.pedalRefC.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalRefC.setFont(font)
        pal = self.pedalRefC.palette()
        pal.setColor(self.pedalRefC.backgroundRole(), QColor('#222'))
        pal.setColor(self.pedalRefC.foregroundRole(), QColor("#fff"))
        self.pedalRefC.setPalette(pal)

        self.speedRefC = QLabel("REF C")
        self.speedRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefC.setAutoFillBackground(True)
        font = self.speedRefC.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedRefC.setFont(font)
        pal = self.speedRefC.palette()
        pal.setColor(self.speedRefC.backgroundRole(), QColor('#222'))
        pal.setColor(self.speedRefC.foregroundRole(), QColor("#fff"))
        self.speedRefC.setPalette(pal)

        self.lineRefC = LineDeviation()

        self.pedalMedian = QLabel("")
        self.pedalMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalMedian.setAutoFillBackground(True)
        font = self.pedalMedian.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalMedian.setFont(font)
        pal = self.pedalMedian.palette()
        pal.setColor(self.pedalMedian.backgroundRole(), QColor('#222'))
        pal.setColor(self.pedalMedian.foregroundRole(), QColor("#fff"))
        self.pedalMedian.setPalette(pal)

        self.speedMedian = QLabel("MEDIAN")
        self.speedMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedMedian.setAutoFillBackground(True)
        font = self.speedMedian.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedMedian.setFont(font)
        pal = self.speedMedian.palette()
        pal.setColor(self.speedMedian.backgroundRole(), QColor('#222'))
        pal.setColor(self.speedMedian.foregroundRole(), QColor("#fff"))
        self.speedMedian.setPalette(pal)

        self.lineMedian = LineDeviation()

        # Lvl 3
        fuelWidget = QWidget()
        pal = self.fuel.palette()
        pal.setColor(self.fuel.backgroundRole(), QColor("#222"))
        pal.setColor(self.fuel.foregroundRole(), QColor("#fff"))
        self.fuel.setPalette(pal)
        fuelLayout = QGridLayout()
        fuelLayout.setContentsMargins(11,11,11,11)
        fuelWidget.setLayout(fuelLayout)
        fuelLayout.setColumnStretch(0, 1)
        fuelLayout.setColumnStretch(1, 1)

        fuelLayout.addWidget(self.fuel, 0, 0, 1, 1)
        fuelLayout.addWidget(self.fuelBar, 0, 1, 1, 1)
        if self.circuitExperience:
            fuelLayout.addWidget(self.mapView, 1, 0, 1, 2)
        else:
            fuelLayout.addWidget(self.laps, 1, 0, 1, 2)

        tyreWidget = QWidget()
        tyreLayout = QGridLayout()
        tyreWidget.setLayout(tyreLayout)
        tyreLayout.addWidget(self.tyreFL, 0, 0)
        tyreLayout.addWidget(self.tyreFR, 0, 1)
        tyreLayout.addWidget(self.tyreRL, 1, 0)
        tyreLayout.addWidget(self.tyreRR, 1, 1)

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
            speedLayout.setRowStretch(1, 1)
        if self.brakepoints:
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
            speedLayout.setRowStretch(0, 1)
        speedLayout.setRowStretch(2, 4)

        # Lvl 2
        self.header = QLabel("? LAPS LEFT")
        font = self.header.font()
        font.setPointSize(64)
        font.setBold(True)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pal = self.header.palette()
        pal.setColor(self.header.backgroundRole(), QColor('#222'))
        pal.setColor(self.header.foregroundRole(), QColor("#fff"))
        self.header.setPalette(pal)

        headerFuel = QLabel("FUEL")
        font = headerFuel.font()
        font.setPointSize(64)
        font.setBold(True)
        headerFuel.setFont(font)
        headerFuel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pal = headerFuel.palette()
        pal.setColor(headerFuel.backgroundRole(), QColor('#222'))
        pal.setColor(headerFuel.foregroundRole(), QColor("#fff"))
        headerFuel.setPalette(pal)

        headerTyres = QLabel("TYRES")
        font = headerTyres.font()
        font.setPointSize(64)
        font.setBold(True)
        headerTyres.setFont(font)
        headerTyres.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pal = headerTyres.palette()
        pal.setColor(headerTyres.backgroundRole(), QColor('#222'))
        pal.setColor(headerTyres.foregroundRole(), QColor("#fff"))
        headerTyres.setPalette(pal)

        self.headerSpeed = QLabel("SPEED")
        font = self.headerSpeed.font()
        font.setPointSize(64)
        font.setBold(True)
        self.headerSpeed.setFont(font)
        self.headerSpeed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.headerSpeed.setAutoFillBackground(True)
        pal = self.headerSpeed.palette()
        pal.setColor(self.headerSpeed.foregroundRole(), QColor("#fff"))
        self.headerSpeed.setPalette(pal)

        # Lvl 1
        masterLayout = QGridLayout()
        self.masterWidget = QWidget()
        self.masterWidget.setLayout(masterLayout)
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
        masterLayout.addWidget(fuelWidget, 2, 1, 3, 1)
        masterLayout.addWidget(tyreWidget, 4, 0, 1, 1)
        masterLayout.addWidget(speedWidget, 2, 0, 1, 1)

        pal = self.palette()
        pal.setColor(self.backgroundRole(), QColor('#333'))
        self.setPalette(pal)

    def startDash(self):
        self.circuitExperience = self.startWindow.mode.currentIndex() == 1

        ip = self.startWindow.ip.text()

        self.keepLaps = self.startWindow.keepLaps.isChecked()

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
        
        self.brakepoints = self.startWindow.brakepoints.isChecked()
        self.countdownBrakepoint = self.startWindow.countdownBrakepoint.isChecked()
        self.bigCountdownBrakepoint = self.startWindow.bigCountdownTarget.currentIndex()
        
        self.allowLoop = self.startWindow.allowLoop.isChecked()

        self.fuelMultiplier = self.startWindow.fuelMultiplier.value()
        self.maxFuelConsumption = self.startWindow.maxFuelConsumption.value()
        fuelWarning = self.startWindow.fuelWarning.value()
        

        settings = QSettings()

        settings.setValue("mode", self.startWindow.mode.currentIndex())
        
        settings.setValue("ip", ip)
        
        settings.setValue("keepLaps", self.keepLaps)

        settings.setValue("lapDecimals", self.lapDecimals)
        settings.setValue("showOptimalLap", self.showOptimalLap)
        settings.setValue("showBestLap", self.showBestLap)
        settings.setValue("showMedianLap", self.showMedianLap)
        settings.setValue("showLastLap", self.showLastLap)
        
        settings.setValue("recordingEnabled", self.recordingEnabled)
        settings.setValue("messagesEnabled", self.messagesEnabled)
        settings.setValue("saveSessionName", saveSessionName)
        if saveSessionName:
            settings.setValue("sessionName", self.sessionName)
        else:
            settings.setValue("sessionName", "")
        settings.setValue("storageLocation", self.storageLocation)

        settings.setValue("linecomp", self.linecomp)

        settings.setValue("brakepoints", self.brakepoints)
        settings.setValue("countdownBrakepoint", self.countdownBrakepoint)
        settings.setValue("bigCountdownTarget", self.bigCountdownBrakepoint)

        settings.setValue("allowLoop", self.allowLoop)
        
        settings.setValue("fuelMultiplier", self.startWindow.fuelMultiplier.value())
        settings.setValue("maxFuelConsumption", self.startWindow.maxFuelConsumption.value())
        settings.setValue("fuelWarning", self.startWindow.fuelWarning.value())

        settings.sync()

        self.makeDashWidget()
        self.fuelBar.setThreshold(self.fuelMultiplier * fuelWarning)
        self.fuelBar.setMaxLevel(self.fuelMultiplier * self.maxFuelConsumption)
        self.setCentralWidget(self.masterWidget)

        self.initRace()

        self.receiver = tele.GT7TelemetryReceiver(ip)

        self.refLaps = [ self.loadLap(self.refAFile), self.loadLap(self.refBFile), self.loadLap(self.refCFile) ]

        self.receiver.setQueue(self.queue)
        self.receiver.setIgnorePktId(self.allowLoop)
        self.thread = threading.Thread(target=self.receiver.runTelemetryReceiver)
        self.thread.start()

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start()

        self.debugCount = 0
        self.noThrottleCount = 0

    def stopDash(self):
        if not self.receiver is None:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), QColor("#333"))
            self.setPalette(pal)

            self.timer.stop()
            self.receiver.running = False
            self.thread.join()
            self.receiver = None

    def loadLap(self, fn):
        lap = Lap()
        if len(fn)>0:
            print(fn)
            with open(fn, "rb") as f:
                allData = f.read()
                curIndex = 0
                print(len(allData))
                while curIndex < len(allData):
                    data = allData[curIndex:curIndex + 296]
                    curIndex += 296
                    ddata = self.receiver.salsa20_dec(data)
                    curPoint = Point(ddata, data)
                    lap.points.append(curPoint)
        return lap



    def initRace(self):
        print("INIT RACE")
        self.lastLap = -1
        self.lastFuel = -1
        self.lastFuelUsage = []
        self.fuelFactor = 0
        self.refueled = 0

        self.previousPoint = None

        self.curLap = Lap()
        self.previousLaps = []
        self.bestLap = -1
        self.medianLap = -1

        self.closestILast = 0
        self.closestIBest = 0
        self.oldIBest = 0
        self.closestIMedian = 0
        self.closestIRefA = 0
        self.closestIRefB = 0
        self.closestIRefC = 0

        pal = self.pedalLast.palette()
        self.pedalLast.setText("")
        pal.setColor(self.pedalLast.backgroundRole(), QColor("#222"))
        self.pedalLast.setPalette(pal)

        pal = self.pedalBest.palette()
        self.pedalBest.setText("")
        pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
        self.pedalBest.setPalette(pal)

        pal = self.pedalMedian.palette()
        self.pedalMedian.setText("")
        pal.setColor(self.pedalMedian.backgroundRole(), QColor("#222"))
        self.pedalMedian.setPalette(pal)

        self.lineBest.setPoints(None,None)
        self.lineBest.update()

        self.lineLast.setPoints(None,None)
        self.lineLast.update()

        self.lineMedian.setPoints(None,None)
        self.lineMedian.update()

    def tyreTempColor(self, temp):
        col = QColor()
        hue = 0.333 - (temp - 70)/50
        if hue < 0:
            hue = 0
        if hue > 0.666:
            hue = 0.666
        col.setHsvF (hue, 1, 1)

        return "background-color: " + col.name() + ";"

    def tyreTempQColor(self, temp):
        col = QColor()
        hue = 0.333 - (temp - 70)/50
        if hue < 0:
            hue = 0
        if hue > 0.666:
            hue = 0.666
        col.setHsvF (hue, 1, 1)

        return col

    def speedDiffColor(self, d):
        col = QColor()
        hue = -d/60 + 60/360
        if hue < 0:
            hue = 0
        if hue > 120/360:
            hue = 120/360
        col.setHsvF (hue, 1, 1)

        return "background-color: " + col.name() + ";"

    def speedDiffQColor(self, d):
        col = QColor()
        hue = -d/60 + 60/360
        if hue < 0:
            hue = 0
        if hue > 120/360:
            hue = 120/360
        col.setHsvF (hue, 1, 1)

        return col

    def brakeQColor(self, d):
        col = QColor()
        col.setHsvF (0, 1, (0x22/0xff) + d * (1 - 0x22/0xff)/100)

        return col

    def distance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_y-p2.position_y)**2 + (p1.position_z-p2.position_z)**2)

    def findClosestPoint(self, lap, p, startIdx):
        shortestDistance = 100000000
        result = None
        dbgCount = 0
        for p2 in range(startIdx, len(lap)-10):
            dbgCount+=1
            curDist = self.distance(p, lap[p2])
            if curDist < 15 and curDist < shortestDistance:
                shortestDistance = curDist
                result = p2
            if not result is None and curDist > 20:
                break
            if curDist >= 500:
                break

        if result is None:
            return None, startIdx
        return lap[result], result

    def findClosestPointNoLimit(self, lap, p):
        shortestDistance = 100000000
        result = None
        for p2 in lap:
            curDist = self.distance(p, p2)
            if curDist < shortestDistance:
                shortestDistance = curDist
                result = p2

        return result

    def findNextBrake(self, lap, startI):
        #print("findNextBrake", startI)
        for i in range(startI, min(startI + 60 * 3, len(lap))):
            #print(startI, i, min(startI + 60, len(lap)))
            if lap[i].brake > 0.1:
                return i-startI
        return None

    def getLapLength(self, lap):
        totalDist = 0
        for i in range(1, len(lap)):
            totalDist += self.distance(lap[i-1], lap[i])
        return totalDist

    def purgeBadLaps(self):
        print("PURGE laps")
        longestLength = 0
        longestLap = None
        for l in self.previousLaps:
            ll = l.length()
            if longestLength < ll:
                longestLength = ll
                longestLap = l

        if not longestLap is None:
            print("Longest: ", longestLength, longestLap.time)
        temp = []
        for l in self.previousLaps:
            print ("\nCheck lap", l.time)
            d = self.distance(longestLap.points[-1], l.points[-1])
            c = self.findClosestPointNoLimit(l.points, longestLap.points[-1])
            d2 = -1
            d3 = -1
            if not c is None:
                d2 = self.distance(longestLap.points[-1], c)
            c3 = self.findClosestPointNoLimit(longestLap.points, l.points[-1])
            if not c3 is None:
                d3 = self.distance(l.points[-1], c3)
            print("End distance:", d)
            if d > 15:
                print("PURGE lap", len(l.points)/60, d)
            else:
                temp.append(l)
        self.previousLaps = temp




    def cleanUpLap(self, lap):
        print("Input:", len(lap.points))
        if len(lap.points) == 0:
            print("Lap is empty")
            return lap
        if len(lap.points) < 600:
            print("\nLap is short")
            return lap
        if (lap.points[-1].throttle > 0):# or lap[-1].brake > 0):
            print("Throttle to the end")
            return lap
        afterLap = 0
        for i in range(1, len(lap.points)):
            if lap.points[-i].throttle == 0:# and lap[-i].brake == 0:
                afterLap+=1
            else:
                break
        print("Remove", afterLap, "of", len(lap.points))
        if afterLap > 0:
            result = lap.points[:-afterLap]
        else:
            result = lap.points
        print("Got", len(result))
        return Lap(lap.time, result, lap.valid)

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
            

    def updateLaps(self, curPoint):
        lapSuffix = ""
        if self.isRecording:
            lapSuffix = " [RECORDING]"
        if self.circuitExperience:
            self.header.setText("CIRCUIT EXPERIENCE" + lapSuffix)
        elif curPoint.total_laps > 0:
            lapValue = curPoint.total_laps - curPoint.current_lap + 1
            if self.lapDecimals and self.closestILast > 0:
                lapValue -= (
                        self.closestILast / len(self.previousLaps[-1].points) +
                        self.closestIBest / len(self.previousLaps[self.bestLap].points) +
                        self.closestIMedian / len(self.previousLaps[self.medianLap].points)) / 3
                lapValue = round(lapValue, 2)
            self.header.setText(str(lapValue) + " LAPS LEFT" + lapSuffix)
        else:
            lapValue = curPoint.current_lap
            if self.lapDecimals and self.closestILast > 0:
                lapValue += (
                        self.closestILast / len(self.previousLaps[-1].points) +
                        self.closestIBest / len(self.previousLaps[self.bestLap].points) +
                        self.closestIMedian / len(self.previousLaps[self.medianLap].points)) / 3
                lapValue = round(lapValue, 2)
            self.header.setText("LAP " + str(lapValue) + lapSuffix)

    def updateFuelAndWarnings(self, curPoint):
        if self.refueled > 0:
            lapValue = self.refueled
            if self.lapDecimals and self.closestILast > 0:
                lapValue += (
                        self.closestILast / len(self.previousLaps[-1].points) +
                        self.closestIBest / len(self.previousLaps[self.bestLap].points) +
                        self.closestIMedian / len(self.previousLaps[self.medianLap].points)) / 3
                lapValue = round(lapValue, 2)
            refuelLaps = "<br>" + str (lapValue) + " SINCE REFUEL"
        else:
            refuelLaps = ""

        if self.fuelFactor != 0:
            fuelLapPercent = "<br>" + str(round(100 * self.fuelFactor,1)) + "% PER LAP<br>" + str(round(1 / self.fuelFactor,1)) + " FULL RANGE"
        else:
            fuelLapPercent = ""

        self.fuel.setTextFormat(Qt.TextFormat.RichText)
        self.fuel.setText("<font size=6>" + str(round(100 * curPoint.current_fuel / curPoint.fuel_capacity)) + "%</font><font size=1>" + fuelLapPercent + refuelLaps + "</font>")
        if False:
            refuelLaps = "<br>" + str (3.12) + " SINCE REFUEL" + "<br>" + str (14.2) + " FULL RANGE"
            fuelLapPercent = "<br>" + str(7.7) + "% PER LAP"
            self.fuel.setText("<font size=6>" + str(round(100 * 80 / 100)) + "%</font><font size=1>" + fuelLapPercent + refuelLaps + "</font>")
        if not self.previousPoint is None:
            fuelConsumption = self.previousPoint.current_fuel-curPoint.current_fuel 
            fuelConsumption *= 60 * 60 * 60 # l per hour
            if curPoint.car_speed > 0:
                fuelConsumption /= curPoint.car_speed # l per km
                fuelConsumption *= 100 # l per 100 km

            self.fuelBar.setLevel(max(0, fuelConsumption))
            self.fuelBar.update()

        self.laps.setTextFormat(Qt.TextFormat.RichText)
        messageShown = False
        if self.messagesEnabled: # TODO: put at end and remove messageShown?
            for m in self.messages:
                if not self.circuitExperience and self.distance(curPoint, m[0]) < 100:
                    pal = self.laps.palette()
                    if datetime.datetime.now().microsecond < 500000:
                        pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.red)
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    else:
                        pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.white)
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.red)
                    self.laps.setPalette(pal)
                    self.laps.setText(m[1])
                    messageShown = True


        if not self.circuitExperience and not messageShown:
            if self.fuelFactor > 0:
                lapsFuel = curPoint.current_fuel / curPoint.fuel_capacity / self.fuelFactor
                self.laps.setText("<font size=6>" + str(round(lapsFuel, 2)) + " LAPS</font><br><font color='#7f7f7f' size=1>FUEL REMAINING</font>")

                lapValue = 1
                if self.lapDecimals and self.closestILast > 0:
                    lapValue -= (
                            self.closestILast / len(self.previousLaps[-1].points) +
                            self.closestIBest / len(self.previousLaps[self.bestLap].points) +
                            self.closestIMedian / len(self.previousLaps[self.medianLap].points)) / 3
                
                if self.lapDecimals and round(lapsFuel, 2) < 1 and lapsFuel < lapValue:
                    pal = self.laps.palette()
                    if datetime.datetime.now().microsecond < 500000:
                        pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.red)
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    else:
                        pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.yellow)
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.black)
                    self.laps.setPalette(pal)
                elif round(lapsFuel, 2) < 1:
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.red)
                    pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    self.laps.setPalette(pal)
                elif round(lapsFuel, 2) < 2:
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                    pal.setColor(self.laps.foregroundRole(), QColor('#f80'))
                    self.laps.setPalette(pal)
                else:
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                    pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    self.laps.setPalette(pal)
            elif curPoint.current_fuel == curPoint.fuel_capacity:
                self.laps.setText("<font size=1>FOREVER</font>")
                pal = self.laps.palette()
                pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                self.laps.setPalette(pal)
            else:
                self.laps.setText("<font size=1>MEASURING</font>")
                pal = self.laps.palette()
                pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                self.laps.setPalette(pal)

    def updateSpeed(self, curPoint):
        closestPLast = None
        closestPBest = None
        closestPMedian = None
        closestPRefA = None
        closestPRefB = None
        closestPRefC = None
        nextBrakeBest = None
        closestPRefA, self.closestIRefA = self.findClosestPoint (self.refLaps[0].points, curPoint, self.closestIRefA)
        closestPRefB, self.closestIRefB = self.findClosestPoint (self.refLaps[1].points, curPoint, self.closestIRefB)
        closestPRefC, self.closestIRefC = self.findClosestPoint (self.refLaps[2].points, curPoint, self.closestIRefC)
        nextBrakeRefA = self.findNextBrake(self.refLaps[0].points, self.closestIRefA)
        nextBrakeRefB = self.findNextBrake(self.refLaps[1].points, self.closestIRefB)
        nextBrakeRefC = self.findNextBrake(self.refLaps[2].points, self.closestIRefC)
        if len(self.previousLaps) > 0:
            closestPLast, self.closestILast = self.findClosestPoint (self.previousLaps[-1].points, curPoint, self.closestILast)
            closestPBest, self.closestIBest = self.findClosestPoint (self.previousLaps[self.bestLap].points, curPoint, self.closestIBest)
            closestPMedian, self.closestIMedian = self.findClosestPoint (self.previousLaps[self.medianLap].points, curPoint, self.closestIMedian)
            nextBrakeBest = self.findNextBrake(self.previousLaps[self.bestLap].points, self.closestIBest)

        if not closestPLast is None:
            speedDiff = closestPLast.car_speed - curPoint.car_speed
            pal = self.speedLast.palette()
            pal.setColor(self.speedLast.backgroundRole(), self.speedDiffQColor(speedDiff))
            self.speedLast.setPalette(pal)

            if self.brakepoints:
                pal = self.pedalLast.palette()
                if closestPLast.brake > 0:
                    self.pedalLast.setText("BRAKE")
                    pal.setColor(self.pedalLast.backgroundRole(), self.brakeQColor(closestPLast.brake))
                else:
                    self.pedalLast.setText("")
                    pal.setColor(self.pedalLast.backgroundRole(), QColor("#222"))
                self.pedalLast.setPalette(pal)
                self.lineLast.setPoints(curPoint, closestPLast)
                self.lineLast.update()
        else:
            pal = self.speedLast.palette()
            pal.setColor(self.speedLast.backgroundRole(), QColor('#222'))
            self.speedLast.setPalette(pal)

        pal = self.palette()
        pal.setColor(self.pedalBest.backgroundRole(), QColor("#333"))
        self.setPalette(pal)

        if not closestPRefA is None:
            speedDiff = closestPRefA.car_speed - curPoint.car_speed
            pal = self.speedRefA.palette()
            pal.setColor(self.speedRefA.backgroundRole(), self.speedDiffQColor(speedDiff))
            self.speedRefA.setPalette(pal)

            if self.brakepoints:
                pal = self.pedalRefA.palette()
                if closestPRefA.brake > 0:
                    self.pedalRefA.setText("BRAKE")
                    pal.setColor(self.pedalRefA.backgroundRole(), self.brakeQColor(closestPRefA.brake))
                    if self.bigCountdownBrakepoint == 2:
                        self.setPalette(pal)
                elif self.countdownBrakepoint and not nextBrakeRefA is None:
                    self.pedalRefA.setText(str(math.ceil (nextBrakeRefA/60)))
                    if nextBrakeRefA >= 120:
                        if nextBrakeRefA%60 >= 30:
                            pal.setColor(self.pedalRefA.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 2:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefA.backgroundRole(), QColor("#222"))
                    elif nextBrakeRefA >= 60:
                        if nextBrakeRefA%60 >= 30:
                            pal.setColor(self.pedalRefA.backgroundRole(), QColor("#2FF"))
                            if self.bigCountdownBrakepoint == 2:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefA.backgroundRole(), QColor("#222"))
                    else:
                        if nextBrakeRefA%30 >= 15:
                            pal.setColor(self.pedalRefA.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 2:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefA.backgroundRole(), QColor("#222"))
                else:
                    self.pedalRefA.setText("")
                    pal.setColor(self.pedalRefA.backgroundRole(), QColor("#222"))
                self.pedalRefA.setPalette(pal)
                self.lineRefA.setPoints(curPoint, closestPRefA)
                self.lineRefA.update()
        else:
            pal = self.speedRefA.palette()
            pal.setColor(self.speedRefA.backgroundRole(), QColor('#222'))
            self.speedRefA.setPalette(pal)

        if not closestPRefB is None:
            speedDiff = closestPRefB.car_speed - curPoint.car_speed
            pal = self.speedRefB.palette()
            pal.setColor(self.speedRefB.backgroundRole(), self.speedDiffQColor(speedDiff))
            self.speedRefB.setPalette(pal)

            if self.brakepoints:
                pal = self.pedalRefB.palette()
                if closestPRefB.brake > 0:
                    self.pedalRefB.setText("BRAKE")
                    pal.setColor(self.pedalRefB.backgroundRole(), self.brakeQColor(closestPRefB.brake))
                    if self.bigCountdownBrakepoint == 3:
                        self.setPalette(pal)
                elif self.countdownBrakepoint and not nextBrakeRefB is None:
                    self.pedalRefB.setText(str(math.ceil (nextBrakeRefB/60)))
                    if nextBrakeRefB >= 120:
                        if nextBrakeRefB%60 >= 30:
                            pal.setColor(self.pedalRefB.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 3:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefB.backgroundRole(), QColor("#222"))
                    elif nextBrakeRefB >= 60:
                        if nextBrakeRefB%60 >= 30:
                            pal.setColor(self.pedalRefB.backgroundRole(), QColor("#2FF"))
                            if self.bigCountdownBrakepoint == 3:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefB.backgroundRole(), QColor("#222"))
                    else:
                        if nextBrakeRefB%30 >= 15:
                            pal.setColor(self.pedalRefB.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 3:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefB.backgroundRole(), QColor("#222"))
                else:
                    self.pedalRefB.setText("")
                    pal.setColor(self.pedalRefB.backgroundRole(), QColor("#222"))
                self.pedalRefB.setPalette(pal)
                self.lineRefB.setPoints(curPoint, closestPRefB)
                self.lineRefB.update()
        else:
            pal = self.speedRefB.palette()
            pal.setColor(self.speedRefB.backgroundRole(), QColor('#222'))
            self.speedRefB.setPalette(pal)

        if not closestPRefC is None:
            speedDiff = closestPRefC.car_speed - curPoint.car_speed
            pal = self.speedRefC.palette()
            pal.setColor(self.speedRefC.backgroundRole(), self.speedDiffQColor(speedDiff))
            self.speedRefC.setPalette(pal)

            if self.brakepoints:
                pal = self.pedalRefC.palette()
                if closestPRefC.brake > 0:
                    self.pedalRefC.setText("BRAKE")
                    pal.setColor(self.pedalRefC.backgroundRole(), self.brakeQColor(closestPRefC.brake))
                    if self.bigCountdownBrakepoint == 4:
                        self.setPalette(pal)
                elif self.countdownBrakepoint and not nextBrakeRefC is None:
                    self.pedalRefC.setText(str(math.ceil (nextBrakeRefC/60)))
                    if nextBrakeRefC >= 120:
                        if nextBrakeRefC%60 >= 30:
                            pal.setColor(self.pedalRefC.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 4:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefC.backgroundRole(), QColor("#222"))
                    elif nextBrakeRefC >= 60:
                        if nextBrakeRefC%60 >= 30:
                            pal.setColor(self.pedalRefC.backgroundRole(), QColor("#2FF"))
                            if self.bigCountdownBrakepoint == 4:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefC.backgroundRole(), QColor("#222"))
                    else:
                        if nextBrakeRefC%30 >= 15:
                            pal.setColor(self.pedalRefC.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 4:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalRefC.backgroundRole(), QColor("#222"))
                else:
                    self.pedalRefC.setText("")
                    pal.setColor(self.pedalRefC.backgroundRole(), QColor("#222"))
                self.pedalRefC.setPalette(pal)
                self.lineRefC.setPoints(curPoint, closestPRefC)
                self.lineRefC.update()
        else:
            pal = self.speedRefC.palette()
            pal.setColor(self.speedRefC.backgroundRole(), QColor('#222'))
            self.speedRefC.setPalette(pal)

        if not closestPBest is None:
            speedDiff = closestPBest.car_speed - curPoint.car_speed

            pal = self.speedBest.palette()
            pal.setColor(self.speedBest.backgroundRole(), self.speedDiffQColor(speedDiff))
            self.speedBest.setPalette(pal)
            if self.brakepoints:
                pal = self.pedalBest.palette()
                if closestPBest.brake > 0:
                    self.pedalBest.setText("BRAKE")
                    pal.setColor(self.pedalBest.backgroundRole(), self.brakeQColor(closestPBest.brake))
                    if self.bigCountdownBrakepoint == 1:
                        self.setPalette(pal)
                elif self.countdownBrakepoint and not nextBrakeBest is None:
                    self.pedalBest.setText(str(math.ceil (nextBrakeBest/60)))
                    if nextBrakeBest >= 120:
                        if nextBrakeBest%60 >= 30:
                            pal.setColor(self.pedalBest.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 1:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
                    elif nextBrakeBest >= 60:
                        if nextBrakeBest%60 >= 30:
                            pal.setColor(self.pedalBest.backgroundRole(), QColor("#2FF"))
                            if self.bigCountdownBrakepoint == 1:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
                    else:
                        if nextBrakeBest%30 >= 15:
                            pal.setColor(self.pedalBest.backgroundRole(), QColor("#22F"))
                            if self.bigCountdownBrakepoint == 1:
                                self.setPalette(pal)
                        else:
                            pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))

                else:
                    self.pedalBest.setText("")
                    pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
                self.pedalBest.setPalette(pal)

                self.lineBest.setPoints(curPoint, closestPBest)
                self.lineBest.update()
        else:
            pal = self.speedBest.palette()
            pal.setColor(self.speedBest.backgroundRole(), QColor('#222'))
            self.speedBest.setPalette(pal)

        if not closestPMedian is None:
            speedDiff = closestPMedian.car_speed - curPoint.car_speed
            pal = self.speedMedian.palette()
            pal.setColor(self.speedMedian.backgroundRole(), self.speedDiffQColor(speedDiff))
            self.speedMedian.setPalette(pal)
            if self.brakepoints:
                pal = self.pedalMedian.palette()
                if closestPMedian.brake > 0:
                    self.pedalMedian.setText("BRAKE")
                    pal.setColor(self.pedalMedian.backgroundRole(), self.brakeQColor(closestPMedian.brake))
                #elif closestPMedian.throttle > 0:
                else:
                    self.pedalMedian.setText("")
                    pal.setColor(self.pedalMedian.backgroundRole(), QColor("#222"))
                #else:
                    #self.pedalMedian.setText("COAST")
                    #pal.setColor(self.pedalMedian.backgroundRole(), self.speedDiffQColor(0))
                self.pedalMedian.setPalette(pal)
                self.lineMedian.setPoints(curPoint, closestPMedian)
                self.lineMedian.update()
        else:
            pal = self.speedMedian.palette()
            pal.setColor(self.speedMedian.backgroundRole(), QColor('#222'))
            self.speedMedian.setPalette(pal)

    def updateMap(self, curPoint):
        if self.circuitExperience and not self.previousPoint is None:
            color = Qt.GlobalColor.red
            if len(self.previousLaps) > 0:
                #speedDiff = self.previousLaps[self.bestLap].points[self.closestIBest].car_speed - curPoint.car_speed
                speedDiff = 10*((self.closestIBest - self.oldIBest) - 1)
                self.oldIBest = self.closestIBest
                if speedDiff == 0:
                    color = Qt.GlobalColor.black
                else:
                    color = self.speedDiffQColor(speedDiff)
            self.mapView.setPoints(self.previousPoint, curPoint, color)
            self.mapView.update()


        if curPoint.throttle == 0 and curPoint.brake == 0:
            self.noThrottleCount+=1
        elif self.noThrottleCount > 0:
            self.noThrottleCount=0

    def handleLapChanges(self, curPoint):
        if self.circuitExperience and self.noThrottleCount == 60 * 10:
            print("Lap ended 10 seconds ago")
        if (self.keepLaps and self.lastLap != curPoint.current_lap) or self.lastLap < curPoint.current_lap or (self.circuitExperience and (self.distance(curPoint, self.previousPoint) > 10 or self.noThrottleCount == 60 * 10)):
            if self.circuitExperience:
                cleanLap = self.cleanUpLap(self.curLap)
                self.mapView.endLap(cleanLap.points)
                self.mapView.update()
            else:
                cleanLap = self.curLap
            lapLen = cleanLap.length()
            
            if lapLen < 10:
                print("LAP CHANGE short")
            else:
                print("\nLAP CHANGE", self.lastLap, curPoint.current_lap, str(round(lapLen, 3)) + " m", round(len (cleanLap.points) / 60,3), "s")
                if (len(self.curLap.points)>0):
                    print("start", self.curLap.points[0].position_x, self.curLap.points[0].position_y, self.curLap.points[0].position_z)
                if not self.previousPoint is None:
                    print("end", self.previousPoint.position_x, self.previousPoint.position_y, self.previousPoint.position_z)

            if  not (self.lastLap == -1 and curPoint.current_fuel < 99):
                if self.lastLap > 0:
                    if self.circuitExperience:
                        lastLapTime = len(cleanLap.points)/60.0
                    else:
                        lastLapTime = curPoint.last_lap
                    print("Closed loop distance:", self.distance(cleanLap.points[0], cleanLap.points[-1])) 
                    if self.circuitExperience or self.distance(cleanLap.points[0], cleanLap.points[-1]) < 30: 
                        self.previousLaps.append(Lap(lastLapTime, cleanLap.points, True))
                        print("Append valid lap", lastLapTime, len(cleanLap.points), len(self.previousLaps))
                    else:
                        print("Append invalid lap", lastLapTime, len(cleanLap.points), len(self.previousLaps))
                        self.previousLaps.append(Lap(lastLapTime, cleanLap.points, False))
                    print("Laps:", len(self.previousLaps))
                    if self.circuitExperience:
                        self.purgeBadLaps()
                    print("Laps after purge:", len(self.previousLaps))
                
                    self.bestLap = self.findBestLap()
                    self.medianLap = self.findMedianLap()
                    print("Reset cur lap storage")
                    self.curLap = Lap()
                    print("Should be 0:", len(self.curLap.points))
                    self.closestILast = 0
                    self.closestIBest = 0
                    self.closestIMedian = 0
                    self.closestIRefA = 0
                    self.closestIRefB = 0
                    self.closestIRefC = 0

                    print("\nBest lap:", self.bestLap, self.previousLaps[self.bestLap].time)
                    print("Median lap:", self.medianLap, self.previousLaps[self.medianLap].time)
                    print("Last lap:", len(self.previousLaps)-1, self.previousLaps[-1].time)

                if self.lastFuel != -1:
                    fuelDiff = self.lastFuel - curPoint.current_fuel/curPoint.fuel_capacity
                    if fuelDiff > 0:
                        self.lastFuelUsage.append(fuelDiff)
                        self.refueled += 1
                    elif fuelDiff < 0:
                        self.refueled = 0
                    if len(self.lastFuelUsage) > 5:
                        self.lastFuelUsage = self.lastFuelUsage[1:]
                self.lastFuel = curPoint.current_fuel/curPoint.fuel_capacity

                if len(self.lastFuelUsage) > 0:
                    self.fuelFactor = self.lastFuelUsage[0]
                    for i in range(1, len(self.lastFuelUsage)):
                        self.fuelFactor = 0.333 * self.fuelFactor + 0.666 * self.lastFuelUsage[i]

            self.lastLap = curPoint.current_lap
        elif not self.keepLaps and (self.lastLap > curPoint.current_lap or curPoint.current_lap == 0) and not self.circuitExperience:
            self.initRace()

    def updateDisplay(self):
        while not self.queue.empty():
            self.debugCount += 1
            d = self.queue.get()

            curPoint = Point(d[0], d[1])

            if self.messagesEnabled and not self.newMessage is None:
                self.messages.append([self.curLap.points[-min(60*5,len(self.curLap.points)-1)], self.newMessage])
                self.newMessage = None
                print(self.messages)

            if curPoint.is_paused or not curPoint.in_race:
                continue

            if not self.keepLaps and curPoint.current_lap <= 0 and not self.circuitExperience:
                self.initRace()
                continue

            self.updateTyreTemps(curPoint)
            self.handleLapChanges(curPoint)
            self.updateFuelAndWarnings(curPoint)
            self.updateSpeed(curPoint)
            self.updateMap(curPoint)
            self.updateLaps(curPoint)

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
                prefix = self.storageLocation + "/"
                if len(self.sessionName) > 0:
                    prefix += self.sessionName + "-"
                self.receiver.startRecording(prefix)
                self.isRecording = True

    def keyPressEvent(self, e):
        if self.centralWidget() == self.masterWidget:
            if e.key() == Qt.Key.Key_R.value:
                self.toggleRecording()
            elif e.key() == Qt.Key.Key_Escape.value:
                if self.isRecording:
                    self.isRecording = False
                    self.receiver.stopRecording()
                self.stopDash()
                self.startWindow = StartWindow()
                self.startWindow.starter.clicked.connect(self.startDash)
                self.startWindow.ip.returnPressed.connect(self.startDash)
                self.setCentralWidget(self.startWindow)
            elif e.key() == Qt.Key.Key_Space.value:
                self.newMessage = "CAUTION"
            elif e.key() == Qt.Key.Key_B.value:
                if self.bestLap >= 0:
                    saveThread = threading.Thread(target=self.saveLap, args=(self.bestLap, "best"))
                    saveThread.start()
            elif e.key() == Qt.Key.Key_L.value:
                if len(self.previousLaps) > 0:
                    saveThread = threading.Thread(target=self.saveLap, args=(-1, "last"))
                    saveThread.start()
            elif e.key() == Qt.Key.Key_M.value:
                if self.medianLap >= 0:
                    saveThread = threading.Thread(target=self.saveLap, args=(self.medianLap, "median"))
                    saveThread.start()
            elif e.key() == Qt.Key.Key_A.value:
                if len(self.previousLaps) > 0:
                    saveThread = threading.Thread(target=self.saveAllLaps, args=("combined",))
                    saveThread.start()
            elif e.key() == Qt.Key.Key_W.value:
                print("store message positions")
                saveThread = threading.Thread(target=self.saveMessages)
                saveThread.start()

    def saveAllLaps(self, name):
        print("store all laps:", name)
        prefix = self.storageLocation + "/"
        if len(self.sessionName) > 0:
            prefix += self.sessionName + "-"
        with open ( prefix + "laps-" + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7", "wb") as f:
            for index in range(len(self.previousLaps)):
                for p in self.previousLaps[index].points:
                    f.write(p.raw)

    def saveLap(self, index, name):
        print("store lap:", name)
        prefix = self.storageLocation + "/"
        if len(self.sessionName) > 0:
            prefix += self.sessionName + "-"
        with open ( prefix + "lap-" + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7", "wb") as f:
            for p in self.previousLaps[index].points:
                f.write(p.raw)

    def saveMessages(self):
        d = []
        for m in self.messages:
            d.append({ "X": m[0].position_x, "Y": m[0].position_y, "Z": m[0].position_z, "message" :m[1]})

        j = json.dumps(d, indent=4)
        print(j)
        prefix = self.storageLocation + "/"
        if len(self.sessionName) > 0:
            prefix += self.sessionName + "-"
        with open ( prefix + "messages-" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json", "w") as f:
            f.write(j)


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("=== EXCEPTION ===")
    print("error message:\n", tb)
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
        i+=1
    
    window.show()
    window.startWindow.ip.setFocus()


    sys.excepthook = excepthook
    with keep.presenting():
        app.exec()


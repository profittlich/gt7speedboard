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
        self.bigCountdownBrakepoint = False

        self.showBestLap = True # TODO make ini entry
        self.showLastLap = True # TODO make ini entry
        self.showMedianLap = True # TODO make ini entry
        self.showRefALap = False # TODO implement
        self.showRefBLap = False
        self.showRefCLap = False
        self.showOptimalLap = False

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
            font.setPointSize(96)
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
        if self.showLastLap:
            speedLayout.addWidget(self.speedLast, 2, 2)
        if self.linecomp:
            if self.showBestLap:
                speedLayout.addWidget(self.lineBest, 1, 0)
            if self.showMedianLap:
                speedLayout.addWidget(self.lineMedian, 1, 1)
            if self.showLastLap:
                speedLayout.addWidget(self.lineLast, 1, 2)
            speedLayout.setRowStretch(1, 1)
        if self.brakepoints:
            if self.showBestLap:
                speedLayout.addWidget(self.pedalBest, 0, 0)
            if self.showMedianLap:
                speedLayout.addWidget(self.pedalMedian, 0, 1)
            if self.showLastLap:
                speedLayout.addWidget(self.pedalLast, 0, 2)
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

        self.lapDecimals = self.startWindow.lapDecimals.isChecked()
        self.showOptimalLap = self.startWindow.cbOptimal.isChecked()
        self.showBestLap = self.startWindow.cbBest.isChecked()
        self.showMedianLap = self.startWindow.cbMedian.isChecked()
        self.showRefALap = self.startWindow.cbRefA.isChecked()
        self.showRefBLap = self.startWindow.cbRefB.isChecked()
        self.showRefCLap = self.startWindow.cbRefC.isChecked()
        self.showLastLap = self.startWindow.cbLast.isChecked()

        self.recordingEnabled = self.startWindow.recordingEnabled.isChecked()
        self.messagesEnabled = self.startWindow.messagesEnabled.isChecked()
        self.sessionName = self.startWindow.sessionName.text()
        saveSessionName = self.startWindow.saveSessionName.isChecked()
        
        self.linecomp = self.startWindow.linecomp.isChecked()
        
        self.brakepoints = self.startWindow.brakepoints.isChecked()
        self.countdownBrakepoint = self.startWindow.countdownBrakepoint.isChecked()
        self.bigCountdownBrakepoint = self.startWindow.bigCountdownBrakepoint.isChecked()
        
        self.allowLoop = self.startWindow.allowLoop.isChecked()

        self.fuelMultiplier = self.startWindow.fuelMultiplier.value()
        self.maxFuelConsumption = self.startWindow.maxFuelConsumption.value()
        fuelWarning = self.startWindow.fuelWarning.value()
        

        print(__file__)
        settings = QSettings()#"./gt7speedboard.ini", QSettings.Format.IniFormat)

        settings.setValue("mode", self.startWindow.mode.currentIndex())
        
        settings.setValue("ip", ip)
        
        settings.setValue("lapDecimals", self.lapDecimals)
        settings.setValue("showOptimalLap", self.showOptimalLap)
        settings.setValue("showBestLap", self.showBestLap)
        settings.setValue("showMedianLap", self.showMedianLap)
        settings.setValue("showRefALap", self.showRefALap)
        settings.setValue("showRefBLap", self.showRefBLap)
        settings.setValue("showRefCLap", self.showRefCLap)
        settings.setValue("showLastLap", self.showLastLap)
        
        settings.setValue("recordingEnabled", self.recordingEnabled)
        settings.setValue("messagesEnabled", self.messagesEnabled)
        settings.setValue("saveSessionName", saveSessionName)
        if saveSessionName:
            settings.setValue("sessionName", self.sessionName)
        else:
            settings.setValue("sessionName", "")
        
        settings.setValue("linecomp", self.linecomp)

        settings.setValue("brakepoints", self.brakepoints)
        settings.setValue("countdownBrakepoint", self.countdownBrakepoint)
        settings.setValue("bigCountdownBrakepoint", self.bigCountdownBrakepoint)

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
            self.timer.stop()
            self.receiver.running = False
            self.thread.join()
            self.receiver = None

    def initRace(self):
        self.lastLap = -1
        self.lastFuel = -1
        self.lastFuelUsage = []
        self.fuelFactor = 0
        self.refueled = 0

        self.previousPoint = None

        self.newLapPos = []
        self.previousLaps = []
        self.bestLap = -1
        self.medianLap = -1

        self.closestILast = 0
        self.closestIBest = 0
        self.closestIMedian = 0

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

    def getAvgSpeed(self, lap):
        if len(lap) == 0:
            return 0
        sm = 0
        for s in lap:
            sm += s.car_speed
        return sm / len(lap)

    def purgeBadLaps(self):
        print("PURGE laps")
        longestLength = 0
        longestLap = None
        for l in self.previousLaps:
            ll = self.getLapLength(l[1])
            if longestLength < ll:
                longestLength = ll
                longestLap = l

        if not longestLap is None:
            print("Longest: ", longestLength, longestLap[0])
        temp = []
        for l in self.previousLaps:
            print ("\nCheck lap", l[0])
            d = self.distance(longestLap[1][-1], l[1][-1])
            c = self.findClosestPointNoLimit(l[1], longestLap[1][-1])
            d2 = -1
            d3 = -1
            if not c is None:
                d2 = self.distance(longestLap[1][-1], c)
            c3 = self.findClosestPointNoLimit(longestLap[1], l[1][-1])
            if not c3 is None:
                d3 = self.distance(l[1][-1], c3)
            print("End distance:", d)
            if d > 15:
                print("PURGE lap", len(l[1])/60, d)
            else:
                temp.append(l)
        self.previousLaps = temp




    def cleanUpLap(self, lap):
        if len(lap) == 0:
            print("Lap is empty")
            return lap
        if len(lap) < 600:
            print("\nLap is short")
            return lap
        if (lap[-1].throttle > 0):# or lap[-1].brake > 0):
            print("Throttle to the end")
            return lap
        afterLap = 0
        for i in range(1, len(lap)):
            if lap[-i].throttle == 0:# and lap[-i].brake == 0:
                afterLap+=1
            else:
                break
        print("Remove", afterLap, "of", len(lap))
        if afterLap > 0:
            result = lap[:-afterLap]
        else:
            result = lap
        print("Got", len(result))
        return result

    def findBestLap(self):
        bestIndex = 0
        bestTime = 100000000.0
        for t in range(len(self.previousLaps)):
            if self.previousLaps[t][2] and self.previousLaps[t][0] < bestTime:
                bestTime = self.previousLaps[t][0]
                bestIndex = t
        return bestIndex

    def findMedianLap(self):
        sorter = []
        for e in self.previousLaps:
            if e[2]:
                sorter.append(e[0])

        if len(sorter) > 0:
            sorter = sorted(sorter)
            target = sorter[len(sorter)//2]
            for e in range(len(self.previousLaps)):
                if self.previousLaps[e][0] == target:
                    return e
        return 0

    def makeFuelBar(self, val):
        if val > 1:
            color = "darkred"
        else:
            color = "orange"
        val = min (1, max(0.002, val))
        return "background: qlineargradient( x1:0 y1:1, x2:0 y2:0, stop:" + str(val-0.001) + " " + color + ", stop:" + str (val) + " #222);"

    def updateDisplay(self):

        while not self.queue.empty():
            self.debugCount += 1
            d = self.queue.get()

            curPoint = Point(d[0], d[1])

            if self.messagesEnabled and not self.newMessage is None:
                print(len(self.newLapPos), -min(60*5,len(self.newLapPos)-1))
                self.messages.append([self.newLapPos[-min(60*5,len(self.newLapPos)-1)], self.newMessage])
                self.newMessage = None
                print(self.messages)

            if curPoint.is_paused or not curPoint.in_race:
                continue

            if curPoint.current_lap <= 0 and not self.circuitExperience:
                self.initRace()
                continue

            #print(len(self.newLapPos))

            if self.circuitExperience and not self.previousPoint is None:
                self.mapView.setPoints(self.previousPoint, curPoint)
                self.mapView.update()


            if curPoint.throttle == 0 and curPoint.brake == 0:
                self.noThrottleCount+=1
            elif self.noThrottleCount > 0:
                self.noThrottleCount=0

            # TYRE TEMPS
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


            #print("LAP ", self.lastLap, curPoint.current_lap, curPoint.total_laps, curPoint.time_on_track)
            # LAP CHANGE
            if self.circuitExperience and self.noThrottleCount == 60 * 10:
                print("Lap ended 10 seconds ago")
            if self.lastLap < curPoint.current_lap or (self.circuitExperience and (self.distance(curPoint, self.previousPoint) > 10 or self.noThrottleCount == 60 * 10)):
                if self.circuitExperience:
                    cleanLap = self.cleanUpLap(self.newLapPos)
                    self.mapView.endLap(cleanLap)
                    self.mapView.update()
                else:
                    cleanLap = self.newLapPos
                #print(len(self.newLapPos), len(cleanLap))
                lapLen = self.getLapLength(cleanLap)
                
                if lapLen < 10:
                    print("LAP CHANGE short")
                else:
                    print("\nLAP CHANGE", self.lastLap, curPoint.current_lap, str(round(lapLen, 3)) + " m", round(len (cleanLap) / 60,3), "s")
                    if (len(self.newLapPos)>0):
                        print("start", self.newLapPos[0].position_x, self.newLapPos[0].position_y, self.newLapPos[0].position_z)
                    if not self.previousPoint is None:
                        print("end", self.previousPoint.position_x, self.previousPoint.position_y, self.previousPoint.position_z)

                if  not (self.lastLap == -1 and curPoint.current_fuel < 99):
                    if self.lastLap > 0:
                        if self.circuitExperience:
                            lastLapTime = len(cleanLap)/60.0
                        else:
                            lastLapTime = curPoint.last_lap
                        print("Closed loop distance:", self.distance(cleanLap[0], cleanLap[-1])) 
                        if self.circuitExperience or self.distance(cleanLap[0], cleanLap[-1]) < 30: 
                            self.previousLaps.append([lastLapTime, cleanLap, True])
                            print("Append valid lap", lastLapTime, len(cleanLap))
                        else:
                            print("Append invalid lap", lastLapTime, len(cleanLap))
                            self.previousLaps.append([lastLapTime, cleanLap, False])
                        if self.circuitExperience:
                            self.purgeBadLaps()
                        #self.previousLaps.append([lastLapTime, self.newLapPos])
                        #for pl in self.previousLaps:
                            #print(pl[0], len(pl[1]), len(pl[1]) / 60)
                    
                        self.bestLap = self.findBestLap()
                        self.medianLap = self.findMedianLap()
                        self.newLapPos = []
                        self.closestILast = 0
                        self.closestIBest = 0
                        self.closestIMedian = 0

                        print("\nBest lap:", self.bestLap, self.previousLaps[self.bestLap][0])
                        print("Median lap:", self.medianLap, self.previousLaps[self.medianLap][0])
                        print("Last lap:", len(self.previousLaps)-1, self.previousLaps[-1][0])

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
            elif (self.lastLap > curPoint.current_lap or curPoint.current_lap == 0) and not self.circuitExperience:
                self.initRace()

            # FUEL
            if self.refueled > 0:
                lapValue = self.refueled
                if self.lapDecimals and self.closestILast > 0:
                    lapValue += (
                            self.closestILast / len(self.previousLaps[-1][1]) +
                            self.closestIBest / len(self.previousLaps[self.bestLap][1]) +
                            self.closestIMedian / len(self.previousLaps[self.medianLap][1])) / 3
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

            messageShown = False
            if self.messagesEnabled:
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
                    self.laps.setText(str(round(lapsFuel, 2)) + " LAPS FUEL")

                    lapValue = 1
                    if self.lapDecimals and self.closestILast > 0:
                        lapValue -= (
                                self.closestILast / len(self.previousLaps[-1][1]) +
                                self.closestIBest / len(self.previousLaps[self.bestLap][1]) +
                                self.closestIMedian / len(self.previousLaps[self.medianLap][1])) / 3
                    
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
                    self.laps.setText("FOREVER")
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                    pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    self.laps.setPalette(pal)
                else:
                    self.laps.setText("measuring")
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                    pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    self.laps.setPalette(pal)

            # SPEED
            closestPLast = None
            closestPBest = None
            closestPMedian = None
            nextBrakeBest = None
            if len(self.previousLaps) > 0:
                closestPLast, self.closestILast = self.findClosestPoint (self.previousLaps[-1][1], curPoint, self.closestILast)
                closestPBest, self.closestIBest = self.findClosestPoint (self.previousLaps[self.bestLap][1], curPoint, self.closestIBest)
                closestPMedian, self.closestIMedian = self.findClosestPoint (self.previousLaps[self.medianLap][1], curPoint, self.closestIMedian)
                nextBrakeBest = self.findNextBrake(self.previousLaps[self.bestLap][1], self.closestIBest)

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

            if not closestPBest is None:
                speedDiff = closestPBest.car_speed - curPoint.car_speed
                pal = self.speedBest.palette()
                pal.setColor(self.speedBest.backgroundRole(), self.speedDiffQColor(speedDiff))
                self.speedBest.setPalette(pal)
                pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
                self.fuel.setPalette(pal)
                if self.brakepoints:
                    pal = self.pedalBest.palette()
                    if closestPBest.brake > 0:
                        self.pedalBest.setText("BRAKE")
                        pal.setColor(self.pedalBest.backgroundRole(), self.brakeQColor(closestPBest.brake))
                    elif self.countdownBrakepoint and not nextBrakeBest is None:
                        self.pedalBest.setText(str(math.ceil (nextBrakeBest/60)))
                        if nextBrakeBest >= 120:
                            if nextBrakeBest%60 >= 30:
                                pal.setColor(self.pedalBest.backgroundRole(), QColor("#22F"))
                                if self.bigCountdownBrakepoint:
                                    self.fuel.setPalette(pal)
                            else:
                                pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
                        elif nextBrakeBest >= 60:
                            if nextBrakeBest%60 >= 30:
                                pal.setColor(self.pedalBest.backgroundRole(), QColor("#2FF"))
                                if self.bigCountdownBrakepoint:
                                    self.fuel.setPalette(pal)
                            else:
                                pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
                        else:
                            if nextBrakeBest%30 >= 15:
                                pal.setColor(self.pedalBest.backgroundRole(), QColor("#22F"))
                                if self.bigCountdownBrakepoint:
                                    self.fuel.setPalette(pal)
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

            # LAP DISPLAY
            lapSuffix = ""
            if self.isRecording:
                lapSuffix = " [RECORDING]"
            if curPoint.total_laps > 0:
                lapValue = curPoint.total_laps - curPoint.current_lap + 1
                if self.lapDecimals and self.closestILast > 0:
                    lapValue -= (
                            self.closestILast / len(self.previousLaps[-1][1]) +
                            self.closestIBest / len(self.previousLaps[self.bestLap][1]) +
                            self.closestIMedian / len(self.previousLaps[self.medianLap][1])) / 3
                    lapValue = round(lapValue, 2)
                self.header.setText(str(lapValue) + " LAPS LEFT" + lapSuffix)
            else:
                lapValue = curPoint.current_lap
                if self.lapDecimals and self.closestILast > 0:
                    lapValue += (
                            self.closestILast / len(self.previousLaps[-1][1]) +
                            self.closestIBest / len(self.previousLaps[self.bestLap][1]) +
                            self.closestIMedian / len(self.previousLaps[self.medianLap][1])) / 3
                    lapValue = round(lapValue, 2)
                self.header.setText("LAP " + str(lapValue) + lapSuffix)

            self.previousPoint = curPoint
            self.newLapPos.append(curPoint)


    def closeEvent(self, event):
        self.stopDash()
        event.accept()


    def toggleRecording(self):
        if self.recordingEnabled:
            if self.isRecording:
                self.isRecording = False
                self.receiver.stopRecording()
            else:
                prefix = ""
                if len(self.sessionName) > 0:
                    prefix = self.sessionName + "-"
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
        prefix = ""
        if len(self.sessionName) > 0:
            prefix = self.sessionName + "-"
        with open ( prefix + "laps-" + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7", "wb") as f:
            for index in range(len(self.previousLaps)):
                for p in self.previousLaps[index][1]:
                    f.write(p.raw)

    def saveLap(self, index, name):
        print("store lap:", name)
        prefix = ""
        if len(self.sessionName) > 0:
            prefix = self.sessionName + "-"
        with open ( prefix + "lap-" + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7", "wb") as f:
            for p in self.previousLaps[index][1]:
                f.write(p.raw)

    def saveMessages(self):
        d = []
        for m in self.messages:
            d.append({ "X": m[0].position_x, "Y": m[0].position_y, "Z": m[0].position_z, "message" :m[1]})

        j = json.dumps(d, indent=4)
        print(j)
        prefix = ""
        if len(self.sessionName) > 0:
            prefix = self.sessionName + "-"
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
    window.show()
    window.startWindow.ip.setFocus()


    sys.excepthook = excepthook
    with keep.presenting():
        app.exec()



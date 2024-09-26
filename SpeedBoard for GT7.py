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
from sb.helpers import Worker
from sb.trackdetector import TrackDetector

import sb.gt7telemetryreceiver as tele
from sb.gt7widgets import *

import sb.configuration

import sb.components.tyretemps
import sb.components.fuelandmessages
import sb.components.lapheader
import sb.components.mapce
import sb.components.speed
import sb.components.stats
import sb.components.help


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = sb.configuration.Configuration()

        self.defaultPalette = self.palette()

        loadCarIds()

        self.trackDetector = None
        self.goFullscreen = True

        logPrint("Clear sessions")
        self.sessionStats = []

        self.masterWidget = None
        self.masterWidgetIndex = 0
        self.cfg.loadConstants()
        self.threadpool = QThreadPool()

        self.startWindow = StartWindow()
        self.startWindow.starter.clicked.connect(self.startDash)
        self.startWindow.ip.returnPressed.connect(self.startDash)

        self.setWindowTitle("SpeedBoard for GT7 (v5+dev)")
        self.queue = queue.Queue()
        self.receiver = None
        self.isRecording = False

        self.newMessage = None
        self.messages = []

        self.setCentralWidget(self.startWindow)


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

    def makeDashWidget(self):
        self.components = []

        if self.cfg.circuitExperience:
            mapCEComponent = sb.components.mapce.MapCE(self.cfg, self)
            self.components.append(mapCEComponent)
            self.mapViewCE = mapCEComponent.getWidget()
            headerFuel = self.makeHeaderWidget(mapCEComponent.title())
        else:
            fuelComponent = sb.components.fuelandmessages.FuelAndMessages(self.cfg, self)
            self.components.append(fuelComponent)
            fuelWidget = fuelComponent.getWidget()
            headerFuel = self.makeHeaderWidget(fuelComponent.title())

        tyreComponent = sb.components.tyretemps.TyreTemps(self.cfg, self)
        self.components.append(tyreComponent)
        tyreWidget = tyreComponent.getWidget()
        headerTyres = self.makeHeaderWidget(tyreComponent.title())

        speedComponent = sb.components.speed.Speed(self.cfg, self)
        self.components.append(speedComponent)
        speedWidget = speedComponent.getWidget()
        self.headerSpeed = self.makeHeaderWidget(speedComponent.title())

        headerComponent = sb.components.lapheader.LapHeader(self.cfg, self)
        self.components.append(headerComponent)
        self.header = headerComponent.getWidget()

        helpComponent = sb.components.help.Help(self.cfg, self)
        self.components.append(helpComponent)
        self.help = helpComponent.getWidget()

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
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.uiMsg.setFont(font)
        pal = self.uiMsg.palette()
        pal.setColor(self.uiMsg.foregroundRole(), self.cfg.foregroundColor)
        self.uiMsg.setPalette(pal)

        self.uiMsgPageScroller.setWidget(self.uiMsg)
        self.uiMsgPageScroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.uiMsgPageScroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.uiMsgPageScroller.setWidgetResizable(True)

        self.statsComponent = sb.components.stats.Stats(self.cfg, self)
        self.components.append(self.statsComponent)
        self.statsPageScroller = self.statsComponent.getWidget()

        self.masterWidget.addWidget(self.uiMsgPageScroller)
        self.masterWidget.addWidget(self.statsPageScroller)
        self.masterWidget.addWidget(self.help)

        if not self.cfg.circuitExperience:
            mapComponent = sb.components.mapce.MapCE(self.cfg, self)
            self.components.append(mapComponent)
            self.mapView = mapComponent.getWidget()
            self.masterWidget.addWidget(self.mapView)

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
        if self.cfg.circuitExperience:
            masterLayout.addWidget(self.mapViewCE, 2, 1, 3, 1)
        else:
            masterLayout.addWidget(fuelWidget, 2, 1, 3, 1)

        masterLayout.addWidget(tyreWidget, 4, 0, 1, 1)

        masterLayout.addWidget(speedWidget, 2, 0, 1, 1)

        pal = self.palette()
        pal.setColor(self.backgroundRole(), self.cfg.brightBackgroundColor)
        self.setPalette(pal)

    def startDash(self):
        self.cfg.circuitExperience = self.startWindow.mode.currentIndex() == 1

        if self.cfg.circuitExperience:
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

        # TODO consider moving to Configuration class
        self.cfg.lapDecimals = self.startWindow.lapDecimals.isChecked()
        self.cfg.showOptimalLap = self.startWindow.cbOptimal.isChecked()
        self.cfg.showBestLap = self.startWindow.cbBest.isChecked()
        self.cfg.showMedianLap = self.startWindow.cbMedian.isChecked()
        self.cfg.showRefALap = self.startWindow.cbRefA.isChecked()
        self.cfg.refAFile = self.startWindow.refAFile
        self.cfg.showRefBLap = self.startWindow.cbRefB.isChecked()
        self.cfg.refBFile = self.startWindow.refBFile
        self.cfg.showRefCLap = self.startWindow.cbRefC.isChecked()
        self.cfg.refCFile = self.startWindow.refCFile
        self.cfg.showLastLap = self.startWindow.cbLast.isChecked()

        self.cfg.recordingEnabled = self.startWindow.recordingEnabled.isChecked()
        self.cfg.messagesEnabled = self.startWindow.messagesEnabled.isChecked()
        self.cfg.sessionName = self.startWindow.sessionName.text()
        saveSessionName = self.startWindow.saveSessionName.isChecked()
        self.cfg.storageLocation = self.startWindow.storageLocation
        
        self.cfg.linecomp = self.startWindow.linecomp.isChecked()
        self.cfg.timecomp = self.startWindow.timecomp.isChecked()
        self.cfg.loadMessagesFromFile = self.startWindow.cbCaution.isChecked()
        self.cfg.messageFile = self.startWindow.cautionFile
        
        self.cfg.brakepoints = self.startWindow.brakepoints.isChecked()
        self.cfg.throttlepoints = self.startWindow.throttlepoints.isChecked()
        self.cfg.countdownBrakepoint = self.startWindow.countdownBrakepoint.isChecked()
        self.cfg.bigCountdownBrakepoint = self.startWindow.bigCountdownTarget.currentIndex()
        self.cfg.initialBigCountdownBrakepoint = self.cfg.bigCountdownBrakepoint
        self.cfg.switchToBestLap = self.startWindow.switchToBestLap.isChecked()
        self.cfg.optimizedSeed = self.startWindow.optimizedSeed.currentIndex()
        
        self.cfg.fuelMultiplier = self.startWindow.fuelMultiplier.value()
        self.cfg.maxFuelConsumption = self.startWindow.maxFuelConsumption.value()
        self.cfg.fuelWarning = self.startWindow.fuelWarning.value()

        self.cfg.fontScale = self.startWindow.fontScale.value()

        self.cfg.fontSizeVerySmall = int(round(self.cfg.fontSizeVerySmallPreset * self.cfg.fontScale))
        self.cfg.fontSizeSmall = int(round(self.cfg.fontSizeSmallPreset * self.cfg.fontScale))
        self.cfg.fontSizeNormal = int(round(self.cfg.fontSizeNormalPreset * self.cfg.fontScale))
        self.cfg.fontSizeLarge = int(round(self.cfg.fontSizeLargePreset * self.cfg.fontScale))

        
        if not os.path.exists(self.cfg.storageLocation):
            QMessageBox.critical(self, "Cannot start", "Storage location not found. Please choose a storage location before starting.")
            return

        if self.cfg.refAFile != "" and not os.path.exists(self.cfg.refAFile):
            QMessageBox.critical(self, "File not found", "Reference lap A not found. Please choose a file or disable the reference lap A.")
            return

        if self.cfg.refBFile != "" and not os.path.exists(self.cfg.refBFile):
            QMessageBox.critical(self, "File not found", "Reference lap B not found. Please choose a file or disable the reference lap B.")
            return

        if self.cfg.refCFile != "" and not os.path.exists(self.cfg.refCFile):
            QMessageBox.critical(self, "File not found", "Reference lap C not found. Please choose a file or disable the reference lap C.")
            return

        # TODO move to Configuration
        settings = QSettings()

        settings.setValue("mode", self.startWindow.mode.currentIndex())
        settings.setValue("optimizedSeed", self.startWindow.optimizedSeed.currentIndex())
        
        settings.setValue("ip", ip)
        

        settings.setValue("fontScale", self.cfg.fontScale)
        settings.setValue("lapDecimals", self.cfg.lapDecimals)
        settings.setValue("showOptimalLap", self.cfg.showOptimalLap)
        settings.setValue("showBestLap", self.cfg.showBestLap)
        settings.setValue("showMedianLap", self.cfg.showMedianLap)
        settings.setValue("showLastLap", self.cfg.showLastLap)

        settings.setValue("showRefALap", self.cfg.showRefALap)
        settings.setValue("showRefBLap", self.cfg.showRefBLap)
        settings.setValue("showRefCLap", self.cfg.showRefCLap)
        settings.setValue("refAFile", self.cfg.refAFile)
        settings.setValue("refBFile", self.cfg.refBFile)
        settings.setValue("refCFile", self.cfg.refCFile)
        
        settings.setValue("recordingEnabled", self.cfg.recordingEnabled)
        settings.setValue("messagesEnabled", self.cfg.messagesEnabled)
        settings.setValue("saveSessionName", saveSessionName)
        if saveSessionName:
            settings.setValue("sessionName", self.cfg.sessionName)
        else:
            settings.setValue("sessionName", "")
        settings.setValue("storageLocation", self.cfg.storageLocation)

        settings.setValue("linecomp", self.cfg.linecomp)
        settings.setValue("timecomp", self.cfg.timecomp)
        settings.setValue("loadMessagesFromFile", self.cfg.loadMessagesFromFile)
        settings.setValue("messageFile", self.cfg.messageFile)

        settings.setValue("brakepoints", self.cfg.brakepoints)
        settings.setValue("throttlepoints", self.cfg.throttlepoints)
        settings.setValue("countdownBrakepoint", self.cfg.countdownBrakepoint)
        settings.setValue("bigCountdownTarget", self.cfg.bigCountdownBrakepoint)
        settings.setValue("switchToBestLap", self.cfg.switchToBestLap)

        settings.setValue("fuelMultiplier", self.startWindow.fuelMultiplier.value())
        settings.setValue("maxFuelConsumption", self.startWindow.maxFuelConsumption.value())
        settings.setValue("fuelWarning", self.startWindow.fuelWarning.value())

        settings.sync()

        self.makeDashWidget()
        self.setCentralWidget(self.masterWidget)

        self.brakeOffset = 0
        self.lapOffset = 0

        self.refLaps = [ loadLap(self.cfg.refAFile), loadLap(self.cfg.refBFile), loadLap(self.cfg.refCFile) ]

        self.initRace()
        self.messageWaitsForKey = False

        self.receiver = tele.GT7TelemetryReceiver(ip)

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
        self.timer.setInterval(self.cfg.pollInterval)
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start()

        self.debugCount = 0
        self.noThrottleCount = 0

    def initOptimizedLap(self):
        if self.cfg.optimizedSeed == 0:
            self.optimizedLap = Lap()
        elif self.cfg.optimizedSeed == 1:
            self.optimizedLap = copy.deepcopy(self.refLaps[0])
        elif self.cfg.optimizedSeed == 2:
            self.optimizedLap = copy.deepcopy(self.refLaps[1])
        elif self.cfg.optimizedSeed == 3:
            self.optimizedLap = copy.deepcopy(self.refLaps[2])
        self.curOptimizingLap = Lap()
        self.curOptimizingIndex = 0
        self.curOptimizingLiveIndex = 0
        self.curOptimizingBrake = False

    def showUiMsg(self, msg, t, leftAlign=False, waitForKey=False):
        logPrint("showUiMsg")
        self.uiMsg.setText(msg)
        if leftAlign:
            self.uiMsg.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.uiMsg.setMargin(15)
        else:
            self.uiMsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.uiMsg.setMargin(0)
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
            self.flipPage(self.masterWidgetIndex)

    def stopDash(self):
        if not self.trackDetector is None:
            self.trackDetector.stopDetection()

        if not self.receiver is None:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), self.cfg.brightBackgroundColor)
            self.setPalette(pal)

            self.timer.stop()
            self.receiver.running = False
            self.thread.join()
            while not self.queue.empty():
                self.queue.get_nowait()
            self.receiver = None

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
        
        self.initOptimizedLap()

        self.cfg.bigCountdownBrakepoint = self.cfg.initialBigCountdownBrakepoint

        self.newRunDescription = None

        self.previousPoint = None

        self.previousLaps = []
        self.bestLap = -1
        self.medianLap = -1

        for c in self.components:
            c.initRace()

        self.loadMessages(self.cfg.messageFile)


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

    # TODO: consider using versions from Lap class
    def findClosestPoint(self, lap, p, startIdx):
        shortestDistance = 100000000
        result = None
        for p2 in range(startIdx, len(lap)-10): #TODO why -10? Confusion at the finish line... Maybe do dynamic length
            curDist = p.distance(lap[p2])
            if curDist < self.cfg.closestPointValidDistance and curDist < shortestDistance:
                shortestDistance = curDist
                result = p2
            if not result is None and curDist > self.cfg.closestPointGetAwayDistance:
                break
            if curDist >= self.cfg.closestPointCancelSearchDistance:
                break

        if result is None:
            for p2 in range(100, len(lap)-10, 100):
                curDist = p.distance(lap[p2])
                if curDist < self.cfg.closestPointValidDistance:
                    logPrint("Found global position at", p2)
                    startIdx = p2-100
                    break
                
            return None, startIdx, None
        return lap[result], result, lap[min(len(lap)-1, max(0,result+self.brakeOffset))]

    # TODO: consider using versions from Lap class
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
        for i in range(max(startI,0), min(int(math.ceil(startI + self.cfg.psFPS * 3)), len(lap))):
            if lap[i].brake > self.cfg.brakeMinimumLevel:
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
                if d > self.cfg.circuitExperienceEndPointPurgeDistance:
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
        if len(lap.points) < self.cfg.circuitExperienceShortLapSecondsThreshold * self.cfg.psFPS:
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
            self.statsComponent.updateLiveStats(curPoint)

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
        if self.cfg.circuitExperience and curPoint.current_lap > 1:
            logPrint("Not in Circuit Experience!")
            self.exitDash()
            QMessageBox.critical(self, "Not in Circuit Experience", "Circuit Experience mode is set, but not driven. Unfortunately, this is not supported. Please switch to Laps mode or drive a Circuit Experience.")
            return
        fuel_capacity = curPoint.fuel_capacity
        if fuel_capacity == 0: # EV
            fuel_capacity = 100

        if (
            self.lastLap != curPoint.current_lap
            or (self.cfg.circuitExperience and (curPoint.distance(self.previousPoint) > self.cfg.circuitExperienceJumpDistance or self.noThrottleCount >= self.cfg.psFPS * self.cfg.circuitExperienceNoThrottleTimeout))
           ): # TODO Null error in circuit experience mode when doing laps: AttributeError: 'NoneType' object has no attribute 'position_x'

            # Clean up circuit experience laps
            if self.cfg.circuitExperience:
                if self.noThrottleCount >= self.cfg.psFPS * self.cfg.circuitExperienceNoThrottleTimeout:
                    logPrint("Lap ended", self.cfg.circuitExperienceNoThrottleTimeout ,"seconds ago")

                cleanLap = self.cleanUpLapCE(self.curLap)
                self.mapViewCE.endLap(cleanLap.points)
                self.mapViewCE.update()
            else:
                cleanLap = self.curLap
                self.mapView.endLap(cleanLap.points) # TODO into component
                self.mapView.update()
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
                    self.statsComponent.initRun()

            # Update live stats
            self.statsComponent.updateLiveStats(curPoint)

            if not (self.lastLap == -1 and curPoint.current_fuel < 99):
                if self.lastLap > 0 and ((self.cfg.circuitExperience and lapLen > 0) or curPoint.last_lap != -1):
                    # Determine lap time
                    if self.cfg.circuitExperience:
                        lastLapTime = 1000 * (len(cleanLap.points)/self.cfg.psFPS + 1/(2*self.cfg.psFPS))
                    else:
                        lastLapTime = curPoint.last_lap

                    showBestLapMessage = True

                    logPrint("Closed loop distance:", cleanLap.points[0].distance(cleanLap.points[-1])) 
                    # Process a completed valid lap (circuit experience laps are always valid)
                    if self.cfg.circuitExperience or cleanLap.points[0].distance(cleanLap.points[-1]) < self.cfg.validLapEndpointDistance:
                        if len(self.previousLaps) > 0:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, True, following=curPoint, preceeding=self.previousLaps[-1].points[-1]))
                        else:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, True, following=curPoint))

                        # Debug message
                        it = indexToTime(len(cleanLap.points))
                        mst = msToTime(lastLapTime)
                        tdiff = float(it[4:]) - float(mst[mst.index(":")+1:])
                        logPrint("Append valid lap", msToTime(lastLapTime), indexToTime(len(cleanLap.points)), lastLapTime, len(self.previousLaps), tdiff)

                        if not self.cfg.circuitExperience:
                            self.updateOptimizedLap()

                        for c in self.components:
                            c.newLap(curPoint, cleanLap)


                    else: # Incomplete laps are sometimes useful, but can't be used for everything
                        logPrint("Append invalid lap", msToTime(lastLapTime), indexToTime(len(cleanLap.points)), lastLapTime, len(self.previousLaps))
                        if len(self.previousLaps) > 0:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, False, following=curPoint, preceeding=self.previousLaps[-1].points[-1]))
                        else:
                            self.previousLaps.append(Lap(lastLapTime, cleanLap.points, False, following=curPoint))

                    logPrint("Laps:", len(self.previousLaps))

                    # Clean up circuit experience laps
                    if self.cfg.circuitExperience:
                        self.purgeBadLapsCE()
                        logPrint("Laps after purge:", len(self.previousLaps))
                
                    # Reset comparison lap information
                    newBestLap = self.findBestLap()
                    ## Show best lap message
                    if showBestLapMessage and self.bestLap != newBestLap and self.previousLaps[newBestLap].valid:
                        self.showUiMsg("BEST LAP", 1)
                    ## Reset brake point offsets for new best lap
                    if self.bestLap != newBestLap and self.cfg.bigCountdownBrakepoint == 1:
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
                    if len(self.lastFuelUsage) > self.cfg.fuelStatisticsLaps:
                        self.lastFuelUsage = self.lastFuelUsage[1:]
                    self.refueled += 1
                    self.lastFuel = curPoint.current_fuel/fuel_capacity
    
                    if len(self.lastFuelUsage) > 0:
                        self.fuelFactor = self.lastFuelUsage[0]
                        for i in range(1, len(self.lastFuelUsage)):
                            self.fuelFactor = (1-self.cfg.fuelLastLapFactor) * self.fuelFactor + self.cfg.fuelLastLapFactor * self.lastFuelUsage[i]

                else:
                    logPrint("Ignore pre-lap")
                    self.lastFuel = 1
                    self.resetCurrentLapData()

                # Update live stats
                self.statsComponent.updateLiveStats(curPoint)

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
                if self.cfg.messagesEnabled and not self.newMessage is None:
                    self.messages.append([self.curLap.points[-min(int(self.cfg.psFPS*self.cfg.messageAdvanceTime),len(self.curLap.points)-1)], self.newMessage])
                    self.newMessage = None

                # Only handle packages when driving
                if curPoint.is_paused or not curPoint.in_race: # TODO detect replay and allow storing laps from it
                    continue

                self.determineLapProgress(curPoint)
                self.handleLapChanges(curPoint)

                if not self.cfg.circuitExperience:
                    self.optimizeLap(curPoint)

                self.handleTrackDetect(curPoint)

                for c in self.components:
                    c.addPoint(curPoint, self.curLap)
                
                self.previousPoint = curPoint
                self.curLap.points.append(curPoint)


    def closeEvent(self, event):
        self.stopDash()
        event.accept()


    def toggleRecording(self):
        if self.cfg.recordingEnabled:
            if self.isRecording:
                self.isRecording = False
                self.receiver.stopRecording()
            else:
                if not os.path.exists(self.cfg.storageLocation):
                    self.showUiMsg("Error: Storage location\n'" + self.storageLocation[self.cfg.storageLocation.rfind("/")+1:] + "'\ndoes not exist", 2)
                    return
                prefix = self.cfg.storageLocation + "/"
                if len(self.cfg.sessionName) > 0:
                    prefix += self.cfg.sessionName + "-"
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

    def cycleBigCountdownBreakponts(self):
        self.cfg.bigCountdownBrakepoint += 1
        hit = False
        while not hit:
            if self.cfg.bigCountdownBrakepoint > 5:
                self.cfg.bigCountdownBrakepoint = 0
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 1 and self.cfg.showBestLap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 2 and self.cfg.showRefALap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 3 and self.cfg.showRefBLap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 4 and self.cfg.showRefCLap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 5 and self.cfg.showOptimalLap:
                hit = True
            else:
                self.cfg.bigCountdownBrakepoint += 1

    def keyPressEvent(self, e):
        if self.centralWidget() == self.masterWidget and self.messageWaitsForKey:
            if e.key() != Qt.Key.Key_Shift.value:
                self.messageWaitsForKey = False
                self.returnToDash()
        elif self.centralWidget() == self.masterWidget and not e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if e.key() == Qt.Key.Key_R.value:
                self.toggleRecording()
            elif e.key() == Qt.Key.Key_Escape.value:
                self.exitDash()
            elif e.key() == Qt.Key.Key_Space.value:
                self.newMessage = "CAUTION"
            elif e.key() == Qt.Key.Key_Tab.value:
                self.cycleBigCountdownBreakponts()
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
                    self.flipPage(0)
                else:
                    self.flipPage(2)
            elif e.key() == Qt.Key.Key_T.value:
                self.statsComponent.updateRunStats(saveRuns=True)
                self.showUiMsg("Run table saved.", 2)
            elif e.key() == Qt.Key.Key_Question:
                if self.masterWidget.currentIndex() == 3:
                    self.flipPage(0)
                else:
                    self.flipPage(3)
            #elif e.key() == Qt.Key.Key_T.value:
                #tester = Worker(someDelay, "Complete", 0.2)
                #tester.signals.finished.connect(self.showUiMsg)
                #self.threadpool.start(tester)
        elif self.centralWidget() == self.masterWidget and e.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if e.key() >= Qt.Key.Key_1.value and e.key() <= Qt.Key.Key_9.value:
                self.flipPage(e.key() - Qt.Key.Key_1.value)

    def flipPage(self, nr):
        logPrint("Flip to page", nr)
        self.masterWidget.setCurrentIndex(nr)
        self.masterWidgetIndex = self.masterWidget.currentIndex()

    # TODO consider moving to Lap class
    def saveAllLaps(self, name):
        logPrint("store all laps:", name)
        if not os.path.exists(self.cfg.storageLocation):
            return "Error: Storage location\n'" + self.cfg.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        prefix = self.cfg.storageLocation + "/"
        if len(self.cfg.sessionName) > 0:
            prefix += self.cfg.sessionName + " - "
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

    # TODO consider moving to Lap class
    def saveOptimizedLap(self, index, name):
        for p in index.points:
            p.current_lap = 1
            p.recreatePackage()
        self.saveLap(index, name)

    # TODO consider moving to Lap class
    def saveLap(self, index, name):
        logPrint("store lap:", name)
        if not os.path.exists(self.cfg.storageLocation):
            return "Error: Storage location\n'" + self.cfg.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        prefix = self.cfg.storageLocation + "/"
        if len(self.cfg.sessionName) > 0:
            prefix += self.cfg.sessionName + " - "
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
        if not os.path.exists(self.cfg.storageLocation):
            return "Error: Storage location\n'" + self.cfg.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        d = []
        for m in self.messages:
            d.append({ "X": m[0].position_x, "Y": m[0].position_y, "Z": m[0].position_z, "message" :m[1]})

        j = json.dumps(d, indent=4)
        logPrint(j)
        prefix = self.cfg.storageLocation + "/"
        if len(self.cfg.sessionName) > 0:
            prefix += self.cfg.sessionName + " - "
        with open ( prefix + self.trackPreviouslyIdentified + " - messages - " + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".sblm", "w") as f:
            f.write(j)

    def loadMessages(self, fn):
        self.messages = []
        if self.cfg.loadMessagesFromFile:
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



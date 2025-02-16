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

import sb.dash

import sb.configuration

class RuntimeData:
    def __init__(self):
        self.receiver = None

        self.curLap = None
        self.curLapInvalidated = None
        self.lastLap = None
        self.previousLaps = None
        self.previousPoint = None
        
        self.refLaps = None
        
        self.bestLap = None
        self.medianLap = None
        
        self.optimizedLap = None
        self.curOptimizingLap = None
        
        self.lapOffset = None
        
        self.closestIBest = None
        self.closestILast = None
        self.closestIMedian = None
        self.closestIOptimized = None
        self.closestIRefA = None
        self.closestIRefB = None
        self.closestIRefC = None
        
        self.closestPointBest = None
        self.closestPointLast = None
        self.closestPointMedian = None
        self.closestPointOptimized = None
        self.closestPointRefA = None
        self.closestPointRefB = None
        self.closestPointRefC = None
        
        self.pageKeys = None
        self.componentKeys = None
        
        self.fuelFactor = None
        self.refueled = None
        self.lapProgress = None
        self.noThrottleCount = None # TODO messy in mapce
        
        self.threadpool = None
        
        self.trackDetector = None
        self.trackPreviouslyIdentified = None
        
        self.masterWidget = None # TODO messy in speed
        self.isRecording = None

class Callbacks:
    def __init__(self):
        self.setColor = None
        self.showUiMsg = None

class MainWindow(ColorMainWidget):
    def __init__(self):
        super().__init__()
        self.cfg = sb.configuration.Configuration()
        self.cfg.developmentMode = False

        self.data = RuntimeData()
        self.callbacks = Callbacks()
        self.callbacks.setColor = self.setColor
        self.callbacks.showUiMsg = self.showUiMsg

        self.defaultPalette = self.palette()
        self.specWidgets = []

        loadCarIds()

        self.components = []

        self.goFullscreen = True

        self.cfg.loadConstants()

        self.startWindow = StartWindow(True)
        self.startWindow.starter.clicked.connect(self.startDash)
        self.startWindow.ip.returnPressed.connect(self.startDash)

        self.setWindowTitle("SpeedBoard for GT7 (v7.5)")
        self.queue = queue.Queue()

        self.messageWaitsForKey = False

        self.setCentralWidget(self.startWindow)

    def loadLayout(self, fn):
        with open(fn, "r") as f:
            txt = f.read()
            logPrint(txt)
            self.selectedLayout = json.loads(txt)
            logPrint(self.selectedLayout)

    def makeDashWidget(self):
        self.components = []
        self.data.pageKeys = {}
        self.data.componentKeys = {}
        self.data.threadpool = QThreadPool()
        self.data.isRecording = False
        self.data.curOptimizingLap = Lap()

        self.data.pageKeys = {}

        maker = sb.dash.DashMaker(self, self.cfg, self.data, self.callbacks, self.components)
        self.specWidgets = maker.makeDashFromSpec(self.selectedLayout)

        i = 1
        for s in self.specWidgets:
            s.setWindowTitle("SpeedBoard for GT7 - Screen " + str(i))
            i += 1
            s.show()

        # Lvl 1
        self.data.masterWidget = QStackedWidget()

        uiMsgPageScroller = QScrollArea()
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

        uiMsgPageScroller.setWidget(self.uiMsg)
        uiMsgPageScroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        uiMsgPageScroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        uiMsgPageScroller.setWidgetResizable(True)

        self.data.masterWidget.addWidget(self.specWidgets[0])
        self.data.masterWidget.addWidget(uiMsgPageScroller)

        pal = self.palette()
        pal.setColor(self.backgroundRole(), self.cfg.brightBackgroundColor)
        self.setPalette(pal)

    def startDash(self):
        self.lastPointTimeStamp = time.perf_counter()
        self.congestion = None
        self.cfg.circuitExperience = "Circuit Experience" in self.startWindow.mode.currentText()

        if self.startWindow.mode.currentText().endswith(".sblayout"):
            logPrint(self.startWindow.mode.currentText())
            self.loadLayout(self.startWindow.mode.currentText())
        elif self.startWindow.mode.currentIndex() < self.startWindow.numInternalLayouts:
            logPrint(self.startWindow.layoutPath + self.startWindow.mode.currentText() + ".sblayout")
            self.loadLayout(self.startWindow.layoutPath + "/" + self.startWindow.mode.currentText() + ".sblayout")
        else:
            logPrint(self.startWindow.storageLocation + self.startWindow.mode.currentText() + ".sblayout")
            self.loadLayout(self.startWindow.storageLocation + "/" + self.startWindow.mode.currentText() + ".sblayout")
        logPrint(self.selectedLayout)

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
        
        self.cfg.speedcomp = self.startWindow.speedcomp.isChecked()
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

        
        # TODO maybe move to Configuration
        settings = QSettings()

        settings.setValue("mode", self.startWindow.mode.currentIndex())
        settings.setValue("modeFile", self.startWindow.mode.currentText())
        settings.setValue("optimizedSeed", self.startWindow.optimizedSeed.currentIndex())
        
        settings.setValue("ip", ip)

        self.cfg.saveConstants()

        settings.setValue("saveSessionName", saveSessionName)
        if saveSessionName:
            settings.setValue("sessionName", self.cfg.sessionName)
        else:
            settings.setValue("sessionName", "")
        settings.setValue("fuelMultiplier", self.startWindow.fuelMultiplier.value())
        settings.setValue("maxFuelConsumption", self.startWindow.maxFuelConsumption.value())
        settings.setValue("fuelWarning", self.startWindow.fuelWarning.value())

        settings.sync()

        self.data = RuntimeData()

        self.makeDashWidget()
        self.setCentralWidget(self.data.masterWidget)

        self.data.lapOffset = 0

        self.data.refLaps = [ loadLap(self.cfg.refAFile), loadLap(self.cfg.refBFile), loadLap(self.cfg.refCFile) ]
        self.data.curLap = Lap()
        self.data.curLapInvalidated = False

        self.newSession()

        self.messageWaitsForKey = False

        self.data.receiver = tele.GT7TelemetryReceiver(ip)

        self.data.receiver.setQueue(self.queue)
        self.thread = threading.Thread(target=self.data.receiver.runTelemetryReceiver)
        self.thread.start()

        if self.goFullscreen and len(self.selectedLayout) == 1:
            self.showFullScreen()
        self.showUiMsg("Press ESC to return to the settings", 2)

        if self.cfg.developmentMode:
            for c in self.components:
                if c.__class__ == sb.components.recordingcontroller.RecordingController:
                    c.callAction("toggleRecording")
                    break

        self.data.trackDetector = TrackDetector()
        self.data.trackPreviouslyIdentified = "Unknown Track"
        self.trackPreviouslyDescribed = ""
        self.previousPackageId = 0
        self.resetCurrentLapData()

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(self.cfg.pollInterval)
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start()

        self.data.noThrottleCount = 0

    def returnToDash(self):
        if self.centralWidget() == self.data.masterWidget:
            self.data.masterWidget.setCurrentIndex(0)

    def stopDash(self):
        if not self.data.trackDetector is None:
            self.data.trackDetector.stopDetection()

        if not self.data.receiver is None:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), self.cfg.brightBackgroundColor)
            self.setPalette(pal)

            self.timer.stop()
            self.data.receiver.running = False
            self.thread.join()
            while not self.queue.empty():
                self.queue.get_nowait()
            self.data.receiver = None
        for c in self.components:
            c.stop()

        for s in range (1, len(self.specWidgets)):
            self.specWidgets[s].close()

    def exitDash(self): # TODO stopDash vs exitDash
        if self.data.isRecording:
            self.data.isRecording = False
            self.data.receiver.stopRecording()
        self.stopDash()
        self.showNormal()
        self.startWindow = StartWindow(False)
        self.startWindow.starter.clicked.connect(self.startDash)
        self.startWindow.ip.returnPressed.connect(self.startDash)
        self.setPalette(self.defaultPalette)
        self.setCentralWidget(self.startWindow)
        self.setColor(self.defaultPalette.color(self.backgroundRole()))

    def newSession(self, notifyComponents = True):

        logPrint("INIT RACE")
        self.data.lastLap = -1
        self.lastFuel = -1
        self.lastFuelUsage = []
        self.data.fuelFactor = 0
        self.data.refueled = 0
        logPrint("PIT STOP:", self.data.refueled)
        self.manualPitStop = False
        
        self.cfg.bigCountdownBrakepoint = self.cfg.initialBigCountdownBrakepoint

        self.data.previousPoint = None

        self.data.previousLaps = []
        self.data.bestLap = -1
        self.data.medianLap = -1

        if notifyComponents:
            for c in self.components:
                c.newSession()

    def resetCurrentLapData(self):
        logPrint("Reset cur lap storage") 
        if not self.data.curLap is None and len(self.data.curLap.points) > 1:
            logPrint(" Old lap:", len(self.data.curLap.points))#, self.data.curLap.distance(self.data.curLap.points[0], self.data.curLap.points[-1]), "m")
        self.data.curLap = Lap()
        self.data.curLapInvalidated = False
        self.data.closestILast = 0
        self.data.closestIBest = 0
        self.data.closestIMedian = 0
        self.data.closestIRefA = 0
        self.data.closestIRefB = 0
        self.data.closestIRefC = 0
        self.data.closestIOptimized = 0
        self.data.closestPointLast = None
        self.data.closestPointBest = None
        self.data.closestPointMedian = None
        self.data.closestPointRefA = None
        self.data.closestPointRefB = None
        self.data.closestPointRefC = None
        self.data.closestPointOptimized = None
        self.data.lapProgress = 0

    def purgeBadLapsCE(self): # TODO consider Circuit Experience component
        logPrint("PURGE laps")
        longestLength = 0
        longestLap = None
        for l in self.data.previousLaps:
            ll = l.length()
            if longestLength < ll:
                longestLength = ll
                longestLap = l

        if not longestLap is None:
            logPrint("Longest: ", longestLength, longestLap.time)
            temp = []
            for l in self.data.previousLaps:
                logPrint ("Check lap", l.time)
                d = longestLap.points[-1].distance(l.points[-1])
                c = l.findClosestPointNoLimit(longestLap.points[-1])[0]
                d2 = -1
                d3 = -1
                if not c is None:
                    d2 = c.distance(longestLap.points[-1])
                c3 = longestLap.findClosestPointNoLimit(l.points[-1])[0]
                if not c3 is None:
                    d3 = c3.distance(l.points[-1])
                logPrint("End distance:", d)
                if d > self.cfg.circuitExperienceEndPointPurgeDistance:
                    logPrint("PURGE lap", indexToTime (len(l.points)), d)
                else:
                    temp.append(l)
            self.data.previousLaps = temp

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
        for t in range(len(self.data.previousLaps)):
            if self.data.previousLaps[t].valid and self.data.previousLaps[t].time < bestTime:
                bestTime = self.data.previousLaps[t].time
                bestIndex = t
        return bestIndex

    def findMedianLap(self):
        sorter = []
        for e in self.data.previousLaps:
            if e.valid:
                sorter.append(e.time)

        if len(sorter) > 0:
            sorter = sorted(sorter)
            target = sorter[len(sorter)//2]
            for e in range(len(self.data.previousLaps)):
                if self.data.previousLaps[e].time == target:
                    return e
        return 0


    def handleTrackDetect(self, curPoint): # TODO consider track detect component
        self.data.trackDetector.addPoint(curPoint)

        curTrack = self.data.trackDetector.getTrack()
        if self.trackPreviouslyDescribed != curTrack:
            for c in self.components:
                c.maybeNewTrack(curPoint, curTrack)

            if self.data.trackPreviouslyIdentified != curTrack and self.data.trackDetector.trackIdentified():
                logPrint("=== Welcome to " + curTrack)
                self.showUiMsg("Welcome to<br>" + curTrack, 1)
                self.data.trackPreviouslyIdentified = curTrack
                tempLap = self.data.lastLap
                self.newSession(False)
                self.data.lastLap = tempLap

                for c in self.components:
                    c.newTrack(curPoint, curTrack)
                
            logPrint("Track:", curTrack, "prev:", self.data.trackPreviouslyIdentified, self.trackPreviouslyDescribed)
            self.trackPreviouslyDescribed = curTrack

    def determineLapProgress(self, curPoint):
        self.data.closestPointRefA, self.data.closestIRefA = self.data.refLaps[0].findClosestPoint (curPoint, self.data.closestIRefA, self.cfg)
        self.data.closestPointRefB, self.data.closestIRefB = self.data.refLaps[1].findClosestPoint (curPoint, self.data.closestIRefB, self.cfg)
        self.data.closestPointRefC, self.data.closestIRefC = self.data.refLaps[2].findClosestPoint (curPoint, self.data.closestIRefC, self.cfg)
        if not self.data.optimizedLap is None:
            self.data.closestPointOptimized, self.data.closestIOptimized = self.data.optimizedLap.findClosestPoint (curPoint, self.data.closestIOptimized, self.cfg)
       
        if len(self.data.previousLaps) > 0:
            self.data.closestPointLast, self.data.closestILast = self.data.previousLaps[-1].findClosestPoint (curPoint, self.data.closestILast, self.cfg)

            if self.data.bestLap >= 0 and self.data.previousLaps[self.data.bestLap].valid:
                self.data.closestPointBest, self.data.closestIBest = self.data.previousLaps[self.data.bestLap].findClosestPoint (curPoint, self.data.closestIBest, self.cfg)
                self.data.closestPointMedian, self.data.closestIMedian = self.data.previousLaps[self.data.medianLap].findClosestPoint (curPoint, self.data.closestIMedian, self.cfg)

        lpBest = -1
        lpA = -1
        lpB = -1
        lpC = -1
        tp = -1

        if self.data.closestIRefA > 0:
            lpA = self.data.closestIRefA / len(self.data.refLaps[0].points)
        if self.data.closestIRefB > 0:
            lpB = self.data.closestIRefB / len(self.data.refLaps[1].points)
        if self.data.closestIRefC > 0:
            lpC = self.data.closestIRefC / len(self.data.refLaps[2].points)

        if self.data.bestLap >= 0 and self.data.closestIBest > 0:
            lpBest = self.data.closestIBest / len(self.data.previousLaps[self.data.bestLap].points)

        if self.data.trackDetector.trackIdentified():
            tp = self.data.trackDetector.determineTrackProgress(curPoint)
            if self.data.lapProgress > 0.9 and tp < 0.1:
                tp = 1.0

        if lpBest != -1:
            self.data.lapProgress = lpBest
        elif lpA != -1:
            self.data.lapProgress = lpA
        elif lpB != -1:
            self.data.lapProgress = lpB
        elif lpC != -1:
            self.data.lapProgress = lpC
        elif tp != -1:
            self.data.lapProgress = tp

    def checkCircuitExperienceMode(self, curPoint):
        if self.cfg.circuitExperience and curPoint.current_lap > 1:
            logPrint("Not in Circuit Experience!")
            self.exitDash()
            QMessageBox.critical(self, "Not in Circuit Experience", "Circuit Experience mode is set, but not driven. Unfortunately, this is not supported. Please switch to Laps mode or drive a Circuit Experience.")

    def handleLapChanges(self, curPoint):
        if (
            self.data.lastLap != curPoint.current_lap
            or (self.cfg.circuitExperience and (curPoint.distance(self.data.previousPoint) > self.cfg.circuitExperienceJumpDistance or self.data.noThrottleCount >= self.cfg.psFPS * self.cfg.circuitExperienceNoThrottleTimeout))
           ):

            # Clean up circuit experience laps
            if self.cfg.circuitExperience:
                if self.data.noThrottleCount >= self.cfg.psFPS * self.cfg.circuitExperienceNoThrottleTimeout:
                    logPrint("Lap ended", self.cfg.circuitExperienceNoThrottleTimeout ,"seconds ago")

                cleanLap = self.cleanUpLapCE(self.data.curLap)
            else:
                cleanLap = self.data.curLap
                    
            lapLen = cleanLap.length()
            
            if lapLen == 0:
                logPrint("LAP CHANGE EMPTY")
                return True
            # Handle short and "real" laps differently
            if lapLen < 10: # TODO const
                logPrint("LAP CHANGE short", lapLen, self.data.lastLap, curPoint.current_lap)
            else:
                logPrint("Track Detect Data:", self.data.trackDetector.totalPoints)
                logPrint("LAP CHANGE", self.data.lastLap, curPoint.current_lap, str(round(lapLen, 3)) + " m", indexToTime(len (cleanLap.points)))

            if not (self.data.lastLap == -1 and curPoint.current_fuel < 99):
                if self.data.lastLap > 0 and ((self.cfg.circuitExperience and lapLen > 0) or curPoint.last_lap != -1):
                    # Determine lap time
                    if self.cfg.circuitExperience:
                        lastLapTime = 1000 * (len(cleanLap.points)/self.cfg.psFPS + 1/(2*self.cfg.psFPS)) # TODO use helper function
                    else:
                        lastLapTime = curPoint.last_lap

                    showBestLapMessage = True

                    logPrint("Closed loop distance:", cleanLap.points[0].distance(cleanLap.points[-1]), "vs.", self.cfg.validLapEndpointDistance, self.data.curLapInvalidated) 
                    # Process a completed valid lap (circuit experience laps are always valid)
                    if self.cfg.circuitExperience or cleanLap.points[0].distance(cleanLap.points[-1]) < self.cfg.validLapEndpointDistance and not self.data.curLapInvalidated:
                        if len(self.data.previousLaps) > 0:
                            self.data.previousLaps.append(Lap(lastLapTime, cleanLap.points, True, following=curPoint, preceeding=self.data.previousLaps[-1].points[-1]))
                        else:
                            self.data.previousLaps.append(Lap(lastLapTime, cleanLap.points, True, following=curPoint))

                        # Debug message
                        it = indexToTime(len(cleanLap.points))
                        mst = msToTime(lastLapTime)
                        tdiff = float(it[4:]) - float(mst[mst.index(":")+1:])
                        logPrint("Append valid lap", msToTime(lastLapTime), indexToTime(len(cleanLap.points)), lastLapTime, len(self.data.previousLaps), tdiff)

                        for c in self.components:
                            c.completedLap(curPoint, cleanLap, True)


                    else: # Incomplete laps are sometimes useful, but can't be used for everything
                        logPrint("Append invalid lap", msToTime(lastLapTime), indexToTime(len(cleanLap.points)), lastLapTime, len(self.data.previousLaps))
                        if len(self.data.previousLaps) > 0:
                            self.data.previousLaps.append(Lap(lastLapTime, cleanLap.points, False, following=curPoint, preceeding=self.data.previousLaps[-1].points[-1]))
                        else:
                            self.data.previousLaps.append(Lap(lastLapTime, cleanLap.points, False, following=curPoint))

                        for c in self.components:
                            c.completedLap(curPoint, self.data.previousLaps[-1], False)

                    logPrint("Laps:", len(self.data.previousLaps))

                    # Clean up circuit experience laps
                    if self.cfg.circuitExperience:
                        self.purgeBadLapsCE()
                        logPrint("Laps after purge:", len(self.data.previousLaps))
                
                    # Reset comparison lap information
                    newBestLap = self.findBestLap()
                    ## Show best lap message
                    if showBestLapMessage and self.data.bestLap != newBestLap and self.data.previousLaps[newBestLap].valid:
                        self.showUiMsg("BEST LAP", 1)
                    ## Reset brake point offsets for new best lap
                    self.data.bestLap = newBestLap
                    self.data.medianLap = self.findMedianLap()

                    self.resetCurrentLapData()

                    logPrint("Best lap:", self.data.bestLap, msToTime (self.data.previousLaps[self.data.bestLap].time), "/", indexToTime(len(self.data.previousLaps[self.data.bestLap].points)), "of", len(self.data.previousLaps))
                    logPrint("Median lap:", self.data.medianLap, msToTime(self.data.previousLaps[self.data.medianLap].time))
                    logPrint("Last lap:", len(self.data.previousLaps)-1, msToTime (self.data.previousLaps[-1].time))

                    # Update fuel usage and outlook
                    fuel_capacity = curPoint.fuel_capacity
                    if fuel_capacity == 0: # EV
                        fuel_capacity = 100

                    fuelDiff = self.lastFuel - curPoint.current_fuel/fuel_capacity
                    if fuelDiff > 0 and self.data.previousLaps[-1].valid:
                        logPrint("Append fuel", fuelDiff)
                        self.lastFuelUsage.append(fuelDiff)
                    if len(self.lastFuelUsage) > self.cfg.fuelStatisticsLaps:
                        self.lastFuelUsage = self.lastFuelUsage[1:]
                    self.data.refueled += 1
                    logPrint("PIT STOP:", self.data.refueled)
                    self.lastFuel = curPoint.current_fuel/fuel_capacity
    
                    if len(self.lastFuelUsage) > 0:
                        self.data.fuelFactor = self.lastFuelUsage[0]
                        for i in range(1, len(self.lastFuelUsage)):
                            self.data.fuelFactor = (1-self.cfg.fuelLastLapFactor) * self.data.fuelFactor + self.cfg.fuelLastLapFactor * self.lastFuelUsage[i]

                else:
                    logPrint("Ignore pre-lap")
                    self.lastFuel = 1
                    self.resetCurrentLapData()

            self.data.lastLap = curPoint.current_lap
            logPrint("new optimizing lap")
            self.data.curOptimizingLap = Lap()
            self.curOptimizingIndex = 0
            self.curOptimizingLiveIndex = 0
            self.curOptimizingBrake = False
            logPrint("Fuel", self.data.fuelFactor, self.lastFuel, self.lastFuelUsage)
            return True
        return False

    def checkPitStop(self, curPoint):
        if self.data.previousPoint is None:
            logPrint("FIRST")
        if not self.data.previousPoint is None and curPoint.distance(self.data.previousPoint) > 10.0: # TODO const
            self.data.curLapInvalidated = True
            logPrint ("JUMP by", curPoint.distance(self.data.previousPoint), "to", curPoint.position_x, " / ", curPoint.position_z, " laps ", self.data.previousPoint.current_lap, curPoint.current_lap, "driving", curPoint.car_speed, "km/h")
            if curPoint.current_lap <= 0:
                self.data.refueled = 0
                logPrint("PIT STOP:", self.data.refueled)
                if self.data.lapProgress > 0.5:
                    self.data.refueled -= 1
                    logPrint("PIT STOP:", self.data.refueled)
                for c in self.components:
                    c.leftCircuit()
            elif (curPoint.current_lap == self.data.previousPoint.current_lap or curPoint.current_lap-1 == self.data.previousPoint.current_lap) and curPoint.car_speed > 0.001:
                # TODO difference to reset to track: Standing time?
                self.data.refueled = 0
                logPrint("PIT STOP:", self.data.refueled)
                if self.data.lapProgress > 0.5:
                    self.data.refueled -= 1
                    logPrint("PIT STOP:", self.data.refueled)
                for c in self.components:
                    c.pitStop()
            elif curPoint.current_lap == self.data.previousPoint.current_lap and curPoint.car_speed < 0.1:
                logPrint("RESET TO TRACK", curPoint.current_lap, self.data.previousPoint.current_lap, curPoint.car_speed)
            else:
                logPrint("WARNING: Unknown jump constellation")


    def updateDisplay(self):
        # Grab all new telemetry packages
        while not self.queue.empty():
            d = self.queue.get()
            newPoint = Point(d[0], d[1])

            # Check for dropped packages
            if not self.data.previousPoint is None:
                diff = newPoint.package_id - self.previousPackageId
            else:
                diff = 1

            self.previousPackageId = newPoint.package_id

            pointsToHandle = []

            if diff > 10:
                logPrint("Too many frame drops (" + str (diff) + ")! Data will be corrupted.")
                self.data.trackDetector.reset()
            elif diff > 1:
                logPrint("Frame drops propagated:", diff-1)
                for i in range(diff-1):
                    pi = copy.deepcopy(self.data.previousPoint)
                    pi.interpolate(newPoint, (i+1)/diff)
                    pointsToHandle.append(pi)

            pointsToHandle.append(newPoint)

            # Handle telemetry
            lenPointsToHandle = len(pointsToHandle)
            for i, curPoint in zip (range(lenPointsToHandle), pointsToHandle):
                # Only handle packages when driving
                if curPoint.is_paused or not curPoint.in_race: # TODO detect replay and allow storing laps from it
                    loadCarIds()
                    continue

                self.checkCircuitExperienceMode(curPoint)

                self.determineLapProgress(curPoint)
                isNewLap = self.handleLapChanges(curPoint)
                self.checkPitStop(curPoint)
 
                self.handleTrackDetect(curPoint)

                for c in self.components:
                    c.addPoint(curPoint, self.data.curLap)
                
                self.data.previousPoint = curPoint
                self.data.curLap.points.append(curPoint)

                qs = self.queue.qsize()
                newPointTimeStamp = time.perf_counter()
                #logPrint(round(1000*(newPointTimeStamp-self.lastPointTimeStamp),2))
                dt = round(1000*(newPointTimeStamp-self.lastPointTimeStamp),2)
                if qs>1 and dt > 2000 / self.cfg.psFPS:
                    self.congestion = newPointTimeStamp
                    logPrint("Telemetry data congestion:", qs, dt, "LATENCY:", round(qs * 1000/self.cfg.psFPS, 2), "ms @" + str(self.cfg.psFPS), "FPS")
                elif not self.congestion is None and qs <= 1:
                    logPrint("Congestion resolved after", round(1000*(newPointTimeStamp-self.congestion),2), "ms")
                    self.congestion = None
                self.lastPointTimeStamp = newPointTimeStamp


    def closeEvent(self, event):
        self.stopDash()
        event.accept()


    def keyPressEvent(self, e):
        if not self.data is None and self.centralWidget() == self.data.masterWidget:
            if self.messageWaitsForKey:
                if e.key() != Qt.Key.Key_Shift.value:
                    self.messageWaitsForKey = False
                    self.returnToDash()
            elif not e.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if e.key() == Qt.Key.Key_Escape.value:
                    self.exitDash()
                elif e.key() == Qt.Key.Key_C.value:
                    self.newSession()
                elif e.key() == Qt.Key.Key_P.value:
                    self.manualPitStop = True
                    self.data.refueled = 0
                    logPrint("PIT STOP:", self.data.refueled)
                    if self.data.lapProgress > 0.5:
                        self.data.refueled -= 1
                        logPrint("PIT STOP:", self.data.refueled)
                elif e.key() == Qt.Key.Key_Plus.value or e.key() == Qt.Key.Key_Equal.value:
                    self.data.lapOffset += 1
                elif e.key() == Qt.Key.Key_Minus.value:
                    self.data.lapOffset -= 1
                elif e.key() == Qt.Key.Key_Left.value:
                     cur = self.specWidgets[0].currentIndex()
                     if cur == 0:
                         self.specWidgets[0].setCurrentIndex(self.specWidgets[0].count()-1)
                     else:
                         self.specWidgets[0].setCurrentIndex(cur-1)
                elif e.key() == Qt.Key.Key_Right.value:
                     cur = self.specWidgets[0].currentIndex()
                     if cur == self.specWidgets[0].count() - 1:
                         self.specWidgets[0].setCurrentIndex(0)
                     else:
                         self.specWidgets[0].setCurrentIndex(cur+1)
                elif e.key() in self.data.pageKeys:
                    k = self.data.pageKeys[e.key()]
                    if k[0].currentIndex() == k[1]:
                        k[0].setCurrentIndex(0)
                    else:
                        k[0].setCurrentIndex(k[1])
                elif e.key() in self.data.componentKeys:
                    self.data.componentKeys[e.key()][0].callAction(self.data.componentKeys[e.key()][1])
            elif e.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if e.key() >= Qt.Key.Key_1.value and e.key() <= Qt.Key.Key_9.value:
                    self.flipPage(e.key() - Qt.Key.Key_1.value)

    def showUiMsg(self, msg, t, leftAlign=False, waitForKey=False):
        logPrint("showUiMsg")
        self.uiMsg.setText(msg)
        if leftAlign:
            self.uiMsg.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.uiMsg.setMargin(15)
        else:
            self.uiMsg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.uiMsg.setMargin(0)
        self.data.masterWidget.setCurrentIndex(1)
        if waitForKey:
            self.messageWaitsForKey = True
        else:
            self.messageWaitsForKey = False
            self.returnTimer = QTimer()
            self.returnTimer.setInterval(int(1000 * t))
            self.returnTimer.setSingleShot(True)
            self.returnTimer.timeout.connect(self.returnToDash)
            self.returnTimer.start()


    def flipPage(self, nr):
        logPrint("Flip to page", nr)
        self.specWidgets[0].setCurrentIndex(nr)



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

    customIP = None
    fullscreen = True
    developmentMode = False
    customLayout = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--ip" and i < len(sys.argv)-1:
            customIP = sys.argv[i+1]
            i+=1
        elif sys.argv[i] == "--layout" and i < len(sys.argv)-1:
            customLayout = sys.argv[i+1]
            i+=1
        elif sys.argv[i] == "--dev":
            developmentMode = True
        elif sys.argv[i] == "--no-fs":
            fullscreen = False
        elif sys.argv[i] == "--clear-settings":
            settings = QSettings()
            settings.clear()
            settings.sync()
            logPrint("Settings cleared")
            sys.exit(0)
        elif sys.argv[i] == "--list-components":
            print ("")
            print ("Available components:")
            print ("")
            for i in sb.component.componentLibrary:
                print(i, " " * (30 - len(i)), sb.component.componentLibrary[i].description())
            print ("")
            sys.exit(0)
        i+=1
    
    window = MainWindow()

    window.goFullscreen = fullscreen
    window.cfg.developmentMode = developmentMode
    if not customIP is None:
        window.startWindow.ip.setText(customIP)
    if not customLayout is None:
        window.loadLayout(customLayout)

    window.show()
    window.startWindow.ip.setFocus()


    sys.excepthook = excepthook
    with keep.presenting():
        app.exec()
        #cProfile.run("app.exec()")



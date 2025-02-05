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
import sb.components.pedals
import sb.components.brakeboard
import sb.components.mapopt
import sb.components.mapopting

defaultLayout = [
                    [ # Screen 1
                        [ # Page 1
                            { "component" : "LapHeader", "stretch" : 1},
                            { "list" :
                                [
                                    { "list" :
                                        [
                                            { "component" : "Speed", "stretch" : 2, "actions" : { "Key_Tab" : "cycleFocusReference" }},
                                            { "component" : "TyreTemps", "stretch" : 1},
                                        ], "stretch" : 1
                                    },
                                    { "component" : "FuelAndMessages", "stretch" : 1, "actions" : { "Key_Space" : "setCautionMarker", "Key_W" : "saveMessages" }},
                                ], "stretch" : 100
                            }
                        ],
                        # Pages 2..
                        { "component" : "Stats", "stretch" : 1, "actions" : { "Key_T" : "saveRuns", "Key_D" : "setRunDescription" }},
                        { "component" : "Help", "stretch" : 1},
                        { "component" : "Map", "stretch" : 1},
                    ],
                    #[ # Screen 2
                        #{ "component" : "Map", "stretch" : 1},
                    #]
                ]

multiScreenLayout = [
                    [ # Screen 1
                        [ # Page 1
                            { "component" : "LapHeader", "stretch" : 1},
                            { "list" :
                                [
                                    { "list" :
                                        [
                                            { "component" : "Speed", "stretch" : 2, "actions" : { "Key_Tab" : "cycleFocusReference" }},
                                            { "component" : "TyreTemps", "stretch" : 1},
                                        ], "stretch" : 1
                                    },
                                    { "component" : "FuelAndMessages", "stretch" : 1, "actions" : { "Key_Space" : "setCautionMarker", "Key_W" : "saveMessages" }},
                                ], "stretch" : 100
                            }
                        ],
                        # Pages 2..
                        { "component" : "Help", "stretch" : 1},
                    ],
                    [ # Screen 2
                        { "component" : "Map", "stretch" : 1},
                    ],
                    [ # Screen 2
                        { "component" : "Stats", "stretch" : 1, "actions" : { "Key_T" : "saveRuns", "Key_D" : "setRunDescription" }},
                    ]
                ]

#j = json.dumps(defaultLayout, indent = 4)
#with open("defaultLayout.json", "w") as jf:
    #jf.write(j)

bigLayout = [
    [
        [
            {
                "component": "LapHeader",
                "stretch": 1
            },
            {
                "list": [
                    {
                        "list": [
                            { "component" : "Speed", "stretch" : 2, "actions" : { "Key_Tab" : "cycleFocusReference" }},
                            {
                                "list": [
                                    {
                                        "component": "Map",
                                        "stretch": 1
                                    },
                                    {
                                        "component": "TyreTemps",
                                        "stretch": 1
                                    }
                                ],
                                "stretch": 1
                            }
                        ],
                        "stretch": 1
                    },
                    {
                        "list": [
                            {
                                "component": "Pedals",
                                "stretch": 1
                            },
                            { "component" : "FuelAndMessages", "stretch" : 4, "actions" : { "Key_Space" : "setCautionMarker", "Key_W" : "saveMessages" }},
                        ],
                        "stretch": 1
                    }
                ],
                "stretch": 100
            }
        ],
        { "component" : "Stats", "stretch" : 1, "actions" : { "Key_T" : "saveRuns", "Key_D" : "setRunDescription" }},
        {
            "component": "Help",
            "stretch": 1
        },
        {
            "component": "Map",
            "stretch": 1
        },
    ]
]

circuitExperienceLayout = [
                    [ # Screen 1
                        [ # Page 1
                            { "component" : "LapHeader", "stretch" : 1},
                            { "list" :
                                [
                                    { "list" :
                                        [
                                            { "component" : "Speed", "stretch" : 2},
                                            { "component" : "TyreTemps", "stretch" : 1},
                                        ], "stretch" : 1
                                    },
                                    { "component" : "Map", "stretch" : 1},
                                ], "stretch" : 100
                            }
                        ],
                        # Pages 2..
                        { "component" : "Stats", "stretch" : 1},
                        { "component" : "Help", "stretch" : 1},
                    ],
                ]

brakeBoardLayout = [
                    [ # Screen 1
                        # Pages 2..
                        { "component" : "BrakeBoard", "stretch" : 1, "actions" : { "Key_Tab" : "cycleModes", "Key_D" : "cycleDifficulty" }},
                        { "component" : "Help", "stretch" : 1},
                    ],
                ]

class Screen(QStackedWidget):
    def __init__(self, keyRedirect):
        super().__init__()
        self.keyRedirect = keyRedirect

    def keyPressEvent(self, e):
        self.keyRedirect.keyPressEvent(e)

class RuntimeData:
    def __init__(self):
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
        
        self.brakeOffset = None
        self.lapOffset = None
        
        self.closestIBest = None
        self.closestILast = None
        self.closestIMedian = None
        self.closestIOptimized = None
        self.closestIRefA = None
        self.closestIRefB = None
        self.closestIRefC = None
        
        self.closestOffsetPointBest = None
        self.closestOffsetPointLast = None
        self.closestOffsetPointMedian = None
        self.closestOffsetPointOptimized = None
        self.closestOffsetPointRefA = None
        self.closestOffsetPointRefB = None
        self.closestOffsetPointRefC = None
        
        self.closestPointBest = None
        self.closestPointLast = None
        self.closestPointMedian = None
        self.closestPointOptimized = None
        self.closestPointRefA = None
        self.closestPointRefB = None
        self.closestPointRefC = None
        
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

        self.setColor = None

class MainWindow(ColorMainWidget):
    def __init__(self):
        super().__init__()
        self.cfg = sb.configuration.Configuration()
        self.cfg.developmentMode = False

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
        self.receiver = None

        self.messageWaitsForKey = False

        self.setCentralWidget(self.startWindow)

        logPrint("new optimizing lap")

    def loadLayout(self, fn):
        with open(fn, "r") as f:
            txt = f.read()
            self.selectedLayout = json.loads(txt)

    def createComponent(self, e):
        newComponent = sb.component.componentLibrary[e['component']](self.cfg, self.data)
        self.components.append(newComponent)
        if 'actions' in e:
            for k in e['actions']:
                if k in Qt.Key.__dict__:
                    if not Qt.Key.__dict__[k] in self.data.componentKeys:
                        self.data.componentKeys[Qt.Key.__dict__[k]] = (newComponent, e['actions'][k], k)
                    else:
                        QMessageBox.critical(self, "Duplicate keyboard shortcut", "Duplicate keyboard shortcut in configuration.\n" + k + " will not be used for component " + e['component'] + "!")
        title = newComponent.title()
        widget = None
        if title is None:
            print("New component:", e['component'])
            widget = newComponent.getWidget()
        else:
            print("New component:", title)
            widget = newComponent.getTitledWidget(newComponent.title())
        return widget

    def makeDashEntry(self, e, horizontal = True):
        page = QWidget()
        if horizontal:
            layout = QHBoxLayout()
        else:
            layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        page.setLayout(layout)
        if "list" in e:
            for c in e['list']:
                w = self.makeDashEntry(c, not horizontal)
                layout.addWidget(w[0], w[1])
        elif "component" in e:
            print(e['component'])
            compWidget = self.createComponent(e)
            if not compWidget is None:
                layout.addWidget (compWidget)
        return [page, e['stretch']]

    def makeDashPage(self, e):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        page.setLayout(layout)
        if isinstance(e, list):
            print("Page with multiple components")
            for c in e:
                w = self.makeDashEntry(c)
                layout.addWidget(w[0], w[1])
        elif isinstance(e, dict):
            print("Page:", e['component'])
            compWidget = self.createComponent(e)
            if not compWidget is None:
                layout.addWidget (compWidget)
        return page


    def makeDashScreen(self, e):
        print("Screen")
        screen = Screen(self)
        for c in e:
            screen.addWidget(self.makeDashPage(c))
        return screen

    def makeDashFromSpec(self, spec):
        screens = []
        for c in spec:
            screens.append(self.makeDashScreen(c))
        logPrint(self.data.componentKeys)
        return screens
        

    def makeDashWidget(self):
        self.data = RuntimeData()
        self.components = []
        self.data.componentKeys = {}
        self.data.threadpool = QThreadPool()
        self.data.isRecording = False
        self.data.curOptimizingLap = Lap()
        self.data.setColor = self.setColor

        if self.cfg.circuitExperience:
            self.specWidgets = self.makeDashFromSpec(circuitExperienceLayout)
        else:
            self.specWidgets = self.makeDashFromSpec(self.selectedLayout)

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
        self.cfg.circuitExperience = self.startWindow.mode.currentIndex() == self.startWindow.circuitExperienceIndex
        if not self.cfg.circuitExperience:
            ci = self.startWindow.mode.currentIndex()
            if ci == 0:
                self.selectedLayout = defaultLayout
            elif ci == 1:
                self.selectedLayout = bigLayout
            elif ci == 2:
                self.selectedLayout = multiScreenLayout
            #elif ci == 3:
                #self.selectedLayout = circuitExperienceLayout
            elif ci == 4:
                self.selectedLayout = brakeBoardLayout

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

        settings.setValue("speedcomp", self.cfg.speedcomp)
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
        self.setCentralWidget(self.data.masterWidget)

        self.data.brakeOffset = 0
        self.data.lapOffset = 0

        self.data.refLaps = [ loadLap(self.cfg.refAFile), loadLap(self.cfg.refBFile), loadLap(self.cfg.refCFile) ]
        self.data.curLap = Lap()
        self.data.curLapInvalidated = False

        self.newSession()

        self.messageWaitsForKey = False

        self.receiver = tele.GT7TelemetryReceiver(ip)

        self.receiver.setQueue(self.queue)
        self.thread = threading.Thread(target=self.receiver.runTelemetryReceiver)
        self.thread.start()

        if self.goFullscreen and self.selectedLayout != multiScreenLayout:
            self.showFullScreen()
        self.showUiMsg("Press ESC to return to the settings", 2)

        if self.cfg.developmentMode:
            self.toggleRecording()

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
        for c in self.components:
            c.stop()

        for s in range (1, len(self.specWidgets)):
            self.specWidgets[s].close()

    def exitDash(self):
        if self.data.isRecording:
            self.data.isRecording = False
            self.receiver.stopRecording()
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
        
        self.initOptimizedLap()

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
        self.data.closestOffsetPointLast = None
        self.data.closestOffsetPointBest = None
        self.data.closestOffsetPointMedian = None
        self.data.closestOffsetPointRefA = None
        self.data.closestOffsetPointRefB = None
        self.data.closestOffsetPointRefC = None
        self.data.closestOffsetPointOptimized = None
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
                c = l.findClosestPointNoLimit(longestLap.points[-1])
                d2 = -1
                d3 = -1
                if not c is None:
                    d2 = c.distance(longestLap.points[-1])
                c3 = longestLap.findClosestPointNoLimit(l.points[-1])
                if not c3 is None:
                    d3 = c3.distance(l.points[-1])
                logPrint("End distance:", d)
                if d > self.cfg.circuitExperienceEndPointPurgeDistance:
                    logPrint("PURGE lap", indexToTime (len(l.points)), d)
                else:
                    temp.append(l)
            logPrint("OUT")
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


    def handleTrackDetect(self, curPoint):
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
        self.data.closestPointRefA, self.data.closestIRefA, self.data.closestOffsetPointRefA = self.data.refLaps[0].findClosestPoint (curPoint, self.data.closestIRefA, self.cfg, self.data.brakeOffset)
        self.data.closestPointRefB, self.data.closestIRefB, self.data.closestOffsetPointRefB = self.data.refLaps[1].findClosestPoint (curPoint, self.data.closestIRefB, self.cfg, self.data.brakeOffset)
        self.data.closestPointRefC, self.data.closestIRefC, self.data.closestOffsetPointRefC = self.data.refLaps[2].findClosestPoint (curPoint, self.data.closestIRefC, self.cfg, self.data.brakeOffset)
        self.data.closestPointOptimized, self.data.closestIOptimized, self.data.closestOffsetPointOptimized = self.data.optimizedLap.findClosestPoint (curPoint, self.data.closestIOptimized, self.cfg, self.data.brakeOffset)
       
        if len(self.data.previousLaps) > 0:
            self.data.closestPointLast, self.data.closestILast, self.data.closestOffsetPointLast = self.data.previousLaps[-1].findClosestPoint (curPoint, self.data.closestILast, self.cfg, self.data.brakeOffset)

            if self.data.bestLap >= 0 and self.data.previousLaps[self.data.bestLap].valid:
                self.data.closestPointBest, self.data.closestIBest, self.data.closestOffsetPointBest = self.data.previousLaps[self.data.bestLap].findClosestPoint (curPoint, self.data.closestIBest, self.cfg, self.data.brakeOffset)
                self.data.closestPointMedian, self.data.closestIMedian, self.data.closestOffsetPointMedian = self.data.previousLaps[self.data.medianLap].findClosestPoint (curPoint, self.data.closestIMedian, self.cfg, self.data.brakeOffset)

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

    def initOptimizedLap(self): # TODO: consider Lap Optimization component
        if self.cfg.optimizedSeed == 0:
            self.data.optimizedLap = Lap()
        elif self.cfg.optimizedSeed == 1:
            self.data.optimizedLap = copy.deepcopy(self.data.refLaps[0])
        elif self.cfg.optimizedSeed == 2:
            self.data.optimizedLap = copy.deepcopy(self.data.refLaps[1])
        elif self.cfg.optimizedSeed == 3:
            self.data.optimizedLap = copy.deepcopy(self.data.refLaps[2])
        logPrint("discard", len(self.data.curOptimizingLap.points))
        logPrint("new optimizing lap")
        self.data.curOptimizingLap = Lap()
        self.curOptimizingIndex = 0
        self.curOptimizingLiveIndex = 0
        self.curOptimizingBrake = False

    def optimizeLap(self, curPoint):
        if len(self.data.optimizedLap.points) == 0:
            self.data.curOptimizingLap.points.append(copy.deepcopy(curPoint))
            if len(self.data.curOptimizingLap.points) != len(self.data.curLap.points):
                self.data.curOptimizingLap.points = copy.deepcopy(self.data.curLap.points)
            self.curOptimizingLiveIndex = len(self.data.curLap.points)
            self.curOptimizingIndex = self.data.closestIOptimized
        else:
            nowBraking = curPoint.brake > 50 or self.data.optimizedLap.points[self.data.closestIOptimized].brake > 50
            if nowBraking != self.curOptimizingBrake:
                self.curOptimizingBrake = nowBraking
                if nowBraking:
                    #logPrint(nowBraking, len(self.data.curOptimizingLap.points), self.curOptimizingIndex, self.curOptimizingLiveIndex)
                    lenOpt = self.data.closestIOptimized - self.curOptimizingIndex
                    lenLive = len(self.data.curLap.points) - self.curOptimizingLiveIndex
                    if lenOpt > lenLive or lenOpt == 0:
                        logPrint("Current segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex, len(self.data.curOptimizingLap.points), len(self.data.curLap.points))
                        self.data.curOptimizingLap.points += copy.deepcopy(self.data.curLap.points[self.curOptimizingLiveIndex:-1])
                    else:
                        logPrint("Previous segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex)
                        self.data.curOptimizingLap.points += self.data.optimizedLap.points[self.curOptimizingIndex:self.data.closestIOptimized-1]
                    self.curOptimizingLiveIndex = len(self.data.curLap.points)-1
                    self.curOptimizingIndex = self.data.closestIOptimized-1
                    if lenOpt > lenLive:
                        logPrint("///////",len(self.data.curLap.points), len(self.data.curOptimizingLap.points), self.curOptimizingIndex, self.curOptimizingLiveIndex, len(self.data.optimizedLap.points))
        #logPrint( len(self.data.curOptimizingLap.points), len(self.data.curLap.points))

    def updateOptimizedLap(self):
        lenOpt = self.data.closestIOptimized - self.curOptimizingIndex
        lenLive = len(self.data.curLap.points) - self.curOptimizingLiveIndex
        if lenOpt > lenLive or lenOpt == 0:
            logPrint("Current final segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex)
            self.data.curOptimizingLap.points += copy.deepcopy(self.data.curLap.points[self.curOptimizingLiveIndex:])
        else:
            logPrint("Previous final segment was faster", lenOpt, lenLive, self.data.closestIOptimized, self.curOptimizingIndex, self.curOptimizingLiveIndex)
            self.data.curOptimizingLap.points += copy.deepcopy(self.data.optimizedLap.points[self.curOptimizingIndex:])
        self.data.optimizedLap = self.data.curOptimizingLap
        if self.cfg.developmentMode:
            saveThread = Worker(self.appendOptimizedLap, "Optimized lap saved.", 1.0, (self.data.optimizedLap, "optimized",))
            self.data.threadpool.start(saveThread)
        logPrint("Optimized lap:", len(self.data.optimizedLap.points), "points vs.", len(self.data.curLap.points))
        logPrint("new optimizing lap")
        self.data.curOptimizingLap = Lap()
        self.curOptimizingLiveIndex = 0
        self.curOptimizingIndex = 0
        self.curOptimizingBrake = False

    def checkCircuitExperienceMode(self, curPoint):
        if self.cfg.circuitExperience and curPoint.current_lap > 1:
            logPrint("Not in Circuit Experience!")
            self.exitDash()
            QMessageBox.critical(self, "Not in Circuit Experience", "Circuit Experience mode is set, but not driven. Unfortunately, this is not supported. Please switch to Laps mode or drive a Circuit Experience.")

    def handleLapChanges(self, curPoint):
        if (
            self.data.lastLap != curPoint.current_lap
            or (self.cfg.circuitExperience and (curPoint.distance(self.data.previousPoint) > self.cfg.circuitExperienceJumpDistance or self.data.noThrottleCount >= self.cfg.psFPS * self.cfg.circuitExperienceNoThrottleTimeout))
           ): # TODO Null error in circuit experience mode when doing laps: AttributeError: 'NoneType' object has no attribute 'position_x'

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

                        if not self.cfg.circuitExperience:
                            self.updateOptimizedLap()

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
                    if self.data.bestLap != newBestLap and self.cfg.bigCountdownBrakepoint == 1:
                        self.data.brakeOffset = 0
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
                # TODO difference to reaet to track: Standing time?
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
 
                if not self.cfg.circuitExperience:
                    self.optimizeLap(curPoint)

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


    def toggleRecording(self): # TODO: consider recording component
        if self.cfg.recordingEnabled or self.cfg.developmentMode:
            if self.data.isRecording:
                self.data.isRecording = False
                self.receiver.stopRecording()
            else:
                if not os.path.exists(self.cfg.storageLocation):
                    self.showUiMsg("Error: Storage location\n'" + self.storageLocation[self.cfg.storageLocation.rfind("/")+1:] + "'\ndoes not exist", 2)
                    return
                prefix = self.cfg.storageLocation + "/"
                if len(self.cfg.sessionName) > 0:
                    prefix += self.cfg.sessionName + "-"
                self.receiver.startRecording(prefix, not self.cfg.developmentMode)
                self.data.isRecording = True

    def keyPressEvent(self, e):
        if self.centralWidget() == self.data.masterWidget and self.messageWaitsForKey:
            if e.key() != Qt.Key.Key_Shift.value:
                self.messageWaitsForKey = False
                self.returnToDash()
        elif self.centralWidget() == self.data.masterWidget and not e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if e.key() == Qt.Key.Key_R.value: # TODO move to component
                self.toggleRecording()
            elif e.key() == Qt.Key.Key_Escape.value:
                self.exitDash()
            elif e.key() == Qt.Key.Key_B.value: # TODO move to component
                if self.data.bestLap >= 0:
                    saveThread = Worker(self.saveLap, "Best lap saved.", 1.0, (self.data.bestLap, "best",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.data.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_L.value: # TODO move to component
                if len(self.data.previousLaps) > 0:
                    saveThread = Worker(self.saveLap, "Last lap saved.", 1.0, (-1, "last",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.data.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_M.value: # TODO move to component
                if self.data.medianLap >= 0:
                    saveThread = Worker(self.saveLap, "Median lap saved.", 1.0, (self.data.medianLap, "median",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.data.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_O.value: # TODO move to component
                if len(self.data.optimizedLap.points) > 0:
                    saveThread = Worker(self.saveOptimizedLap, "Optimized lap saved.", 1.0, (self.data.optimizedLap, "optimized",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.data.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_A.value: # TODO move to component
                if len(self.data.previousLaps) > 0:
                    saveThread = Worker(self.saveAllLaps, "All laps saved.", 1.0, ("combined",))
                    saveThread.signals.finished.connect(self.showUiMsg)
                    self.data.threadpool.start(saveThread)
            elif e.key() == Qt.Key.Key_C.value:
                self.newSession()
            elif e.key() == Qt.Key.Key_P.value:
                self.manualPitStop = True
                self.data.refueled = 0
                logPrint("PIT STOP:", self.data.refueled)
                if self.data.lapProgress > 0.5:
                    self.data.refueled -= 1
                    logPrint("PIT STOP:", self.data.refueled)
            elif e.key() == Qt.Key.Key_0.value:
                self.data.brakeOffset = 0
                logPrint("Brake offset", self.data.brakeOffset)
            elif e.key() == Qt.Key.Key_Plus.value or e.key() == Qt.Key.Key_Equal.value:
                self.data.lapOffset += 1
            elif e.key() == Qt.Key.Key_Minus.value:
                self.data.lapOffset -= 1
            elif e.key() == Qt.Key.Key_Up.value:
                self.data.brakeOffset -= 3
                logPrint("Brake offset", self.data.brakeOffset)
            elif e.key() == Qt.Key.Key_Down.value:
                self.data.brakeOffset += 3
                logPrint("Brake offset", self.data.brakeOffset)
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
            elif e.key() == Qt.Key.Key_S.value: # TODO redesign page shortcuts
                if self.specWidgets[0].currentIndex() == 1:
                    self.flipPage(0)
                else:
                    self.flipPage(1)
            elif e.key() == Qt.Key.Key_V.value: # TODO redesign page shortcuts
                if self.specWidgets[0].currentIndex() == 3:
                    self.flipPage(0)
                else:
                    self.flipPage(3)
            elif e.key() == Qt.Key.Key_Question: # TODO redesign page shortcuts
                if self.specWidgets[0].currentIndex() == 2:
                    self.flipPage(0)
                else:
                    self.flipPage(2)
            elif e.key() in self.data.componentKeys:
                self.data.componentKeys[e.key()][0].callAction(self.data.componentKeys[e.key()][1])
        elif self.centralWidget() == self.data.masterWidget and e.modifiers() == Qt.KeyboardModifier.ControlModifier:
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

    # TODO consider moving to Lap class
    def saveAllLaps(self, name):
        logPrint("store all laps:", name)
        if not os.path.exists(self.cfg.storageLocation):
            return "Error: Storage location\n'" + self.cfg.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        prefix = self.cfg.storageLocation + "/"
        if len(self.cfg.sessionName) > 0:
            prefix += self.cfg.sessionName + " - "
        with open ( prefix + self.data.trackPreviouslyIdentified + " - laps - " + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7laps", "wb") as f:
            if not self.data.previousLaps[0].preceeding is None:
                f.write(self.data.previousLaps[0].preceeding.raw)
            for index in range(len(self.data.previousLaps)):
                if index > 0 and not self.data.previousLaps[index].preceeding is None and self.data.previousLaps[index].preceeding != self.data.previousLaps[index-1].points[-1]:
                    f.write(self.data.previousLaps[index].preceeding.raw)
                for p in self.data.previousLaps[index].points:
                    f.write(p.raw)
                if index < len(self.data.previousLaps)-1 and not self.data.previousLaps[index].following is None and self.data.previousLaps[index].following != self.data.previousLaps[index+1].points[0]:
                    f.write(self.data.previousLaps[index].following.raw)
            if not self.data.previousLaps[-1].following is None:
                f.write(self.data.previousLaps[-1].following.raw)

    # TODO consider moving to Lap class
    def saveOptimizedLap(self, index, name):
        for p in index.points:
            p.current_lap = 1
            p.recreatePackage()
        self.saveLap(index, name)

    # TODO consider moving to Lap class
    def appendOptimizedLap(self, index, name):
        if not hasattr(self, 'dev_contLap'):
            self.dev_contLap = 1
        else:
            self.dev_contLap += 1
        for p in index.points:
            p.current_lap = self.dev_contLap
            p.recreatePackage()
        self.appendLap(index, name)

    # TODO consider moving to Lap class
    def saveLap(self, index, name):
        logPrint("store lap:", name)
        if not os.path.exists(self.cfg.storageLocation):
            return "Error: Storage location\n'" + self.cfg.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        prefix = self.cfg.storageLocation + "/"
        if len(self.cfg.sessionName) > 0:
            prefix += self.cfg.sessionName + " - "
        with open ( prefix + self.data.trackPreviouslyIdentified + " - lap - " + name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7lap", "wb") as f:
            if isinstance(index, Lap):
                lap = index
            else:
                lap = self.data.previousLaps[index]
            if not lap.preceeding is None:
                logPrint("Going from", lap.preceeding.current_lap)
                f.write(lap.preceeding.raw)
            logPrint("via", lap.points[0].current_lap)
            for p in lap.points:
                f.write(p.raw)
            if not lap.following is None:
                logPrint("to", lap.following.current_lap)
                f.write(lap.following.raw)

    # TODO consider moving to Lap class
    def appendLap(self, index, name):
        logPrint("append lap:", name)
        if not os.path.exists(self.cfg.storageLocation):
            return "Error: Storage location\n'" + self.cfg.storageLocation[self.storageLocation.rfind("/")+1:] + "'\ndoes not exist"
        prefix = self.cfg.storageLocation + "/"
        if len(self.cfg.sessionName) > 0:
            prefix += self.cfg.sessionName + " - "
        with open ( prefix + self.data.trackPreviouslyIdentified + " - lap - " + name + ".gt7laps", "ab") as f:
            if isinstance(index, Lap):
                lap = index
            else:
                lap = self.data.previousLaps[index]
            if not lap.preceeding is None:
                logPrint("Going from", lap.preceeding.current_lap)
                f.write(lap.preceeding.raw)
            logPrint("via", lap.points[0].current_lap)
            for p in lap.points:
                f.write(p.raw)
            if not lap.following is None:
                logPrint("to", lap.following.current_lap)
                f.write(lap.following.raw)


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



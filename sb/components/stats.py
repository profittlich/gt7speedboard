from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint
from sb.helpers import indexToTime, msToTime
from sb.helpers import idToCar

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

class Stats(sb.component.Component):
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

        self.statsPageScroller = QScrollArea()
        self.statsPage = QLabel(self.cfg.sessionName + "\nSession stats not available, yet")

        self.statsPageScroller.setWidget(self.statsPage)
        #self.statsPageScroller.setSizeAdjustPolicy(Qt.QAbstractScrollArea.AdjustToContents)
        self.statsPageScroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.statsPageScroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.statsPageScroller.setWidgetResizable(True)

        self.statsPage.setMargin(15)
        self.statsPage.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.statsPage.setAutoFillBackground(True)
        font = self.statsPage.font()
        font.setPointSize(self.cfg.fontSizeSmall)
        font.setBold(True)
        self.statsPage.setFont(font)
        self.statsPage.setTextFormat(Qt.TextFormat.RichText)
        pal = self.statsPage.palette()
        pal.setColor(self.statsPage.foregroundRole(), self.cfg.foregroundColor)
        self.statsPage.setPalette(pal)
        self.liveStats = ""
        self.runStats = ""
        self.assumedTrack = ""

    def getWidget(self):
        return self.statsPageScroller

    def addPoint(self, curPoint, curLap):
        # Update live stats description
        if not self.data.newRunDescription is None and len(self.sessionStats) > 0:
            self.sessionStats[-1].description = self.data.newRunDescription + "<br>"
            self.data.newRunDescription = None
            self.updateRunStats()


    def updateStats(self):
        statTxt = '<font size="5">' + self.cfg.sessionName + '</font>' + self.liveStats + self.runStats
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
            prefix = self.cfg.storageLocation + "/"
            if len(self.cfg.sessionName) > 0:
                prefix += self.cfg.sessionName + " - "
            with open ( prefix + self.data.trackPreviouslyIdentified + " - runs - " + self.sessionStart + ".csv", "w") as f:
                f.write(carStatCSV)
        self.runStats = carStatTxt
        self.updateStats()

    def updateLiveStats(self, curPoint):
        liveStats = '<br><br><font size="3">CURRENT STATS:</font><br><font size="1">'
        liveStats += "Current track: " + self.data.trackDetector.getTrack() + "<br>"
        liveStats += "Assumed track: " + self.assumedTrack + "<br>"
        liveStats += "Current car: " + idToCar(curPoint.car_id) + "<br>"
        liveStats += "Current lap: " + str(curPoint.current_lap) + "<br>"
        if self.data.bestLap >= 0 and self.data.previousLaps[self.data.bestLap].valid:
            liveStats += "Best lap: " + msToTime (self.data.previousLaps[self.data.bestLap].time) + " (est. " + indexToTime (len(self.data.previousLaps[self.data.bestLap].points)) + ")<br>"
        if self.data.medianLap >= 0 and self.data.previousLaps[self.data.medianLap].valid:
            liveStats += "Median lap: " + msToTime (self.data.previousLaps[self.data.medianLap].time) + "<br>"
        if not self.data.refLaps[0] is None and self.data.refLaps[0].time > 0: 
            liveStats += "Reference lap A: " + msToTime (self.data.refLaps[0].time) + "<br>"
        if not self.data.refLaps[1] is None and self.data.refLaps[1].time > 0: 
            liveStats += "Reference lap B: " + msToTime (self.data.refLaps[1].time) + "<br>"
        if not self.data.refLaps[2] is None and self.data.refLaps[2].time > 0: 
            liveStats += "Reference lap C: " + msToTime (self.data.refLaps[2].time) + "<br>"
        if len(self.data.optimizedLap.points) > 0:
            self.data.optimizedLap.updateTime()
            liveStats += "Optimized lap (est.): " + msToTime (self.data.optimizedLap.time) + "<br>"
        liveStats += "</font>"
        self.liveStats = liveStats
        self.updateStats()

    def newRun(self):
        logPrint("newRun", self.sessionStats)
        if len(self.sessionStats) > 0 and self.sessionStats[-1].sessionStart == len(self.data.previousLaps):
            logPrint("Re-using untouched Run")
            return
        self.sessionStats.append (Run(len(self.data.previousLaps)))


    def newSession(self):
        logPrint("newSession")
        logPrint("Clear sessions")
        self.sessionStats = []
        self.sessionStart = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.newRun()
        self.updateRunStats()

    def leftCircuit(self):
        self.newRun()

    def completedLap(self, curPoint, cleanLap, isFullLap):
        logPrint("completedLap", isFullLap, self.data.lastLap, "->", curPoint.current_lap)
        if curPoint.current_lap == 1 or self.data.lastLap >= curPoint.current_lap:
            logPrint("lap is 1 -> init")
            self.newRun()

        if self.cfg.circuitExperience:
            lastLapTime = 1000 * (len(cleanLap.points)/self.cfg.psFPS + 1/(2*self.cfg.psFPS))
        else:
            lastLapTime = curPoint.last_lap

        logPrint(lastLapTime)

        # Update session stats
        if lastLapTime > 0 and isFullLap:
            if len(self.sessionStats) == 0: # Started app during lap
                logPrint("no stats --> init")
                self.newRun()
            self.sessionStats[-1].carId = curPoint.car_id
            self.sessionStats[-1].addLapTime(lastLapTime, self.data.lastLap)
            pTop = self.data.previousLaps[-1].topSpeed()
            if self.sessionStats[-1].topSpeed < pTop:
                self.sessionStats[-1].topSpeed = pTop
            logPrint(len(self.sessionStats), "sessions")
            for i in self.sessionStats:
                logPrint("Best:", msToTime(i.bestLap()[0]))
                logPrint("Median:", msToTime(i.medianLap()[0]))

        self.updateRunStats()
        self.updateLiveStats(curPoint)

    def newTrack(self, curPoint, track):
        logPrint("newTrack")
        self.assumedTrack = track
        self.newRun()
        self.updateLiveStats(curPoint)
   

    def maybeNewTrack(self, curPoint, track):
        self.updateLiveStats(curPoint)

    def title(self):
        return "Statistics"

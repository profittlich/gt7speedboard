from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import os
import datetime

import sb.component
from sb.gt7telepoint import Point
from sb.helpers import logPrint
from sb.gt7widgets import PedalWidget
from sb.helpers import Worker
from sb.laps import Lap

class SaveLaps(sb.component.Component):
    def description():
        return "Handle saving lap data to the data directory"
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

    def defaultTitle(self):
        return "Saving lap data"

    def actions():
        return {
                "saveBest":"Save best lap",
                "saveLast":"Save last lap",
                "saveMedian":"Save median lap",
                "saveOptimized":"Save optimized lap",
                "saveAll":"Save all laps"
               }
    
    def getWidget(self):
        return None

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

    def callAction(self, a):
        if a == "saveBest":
            if self.data.bestLap >= 0:
                saveThread = Worker(self.saveLap, "Best lap saved.", 1.0, (self.data.bestLap, "best",))
                saveThread.signals.finished.connect(self.data.showUiMsg)
                self.data.threadpool.start(saveThread)
        elif a == "saveLast":
            if len(self.data.previousLaps) > 0:
                saveThread = Worker(self.saveLap, "Last lap saved.", 1.0, (-1, "last",))
                saveThread.signals.finished.connect(self.data.showUiMsg)
                self.data.threadpool.start(saveThread)
        elif a == "saveMedian":
            if self.data.medianLap >= 0:
                saveThread = Worker(self.saveLap, "Median lap saved.", 1.0, (self.data.medianLap, "median",))
                saveThread.signals.finished.connect(self.data.showUiMsg)
                self.data.threadpool.start(saveThread)
        elif a == "saveOptimized":
            if len(self.data.optimizedLap.points) > 0:
                saveThread = Worker(self.saveOptimizedLap, "Optimized lap saved.", 1.0, (self.data.optimizedLap, "optimized",))
                saveThread.signals.finished.connect(self.data.showUiMsg)
                self.data.threadpool.start(saveThread)
        elif a == "saveAll":
            if len(self.data.previousLaps) > 0:
                saveThread = Worker(self.saveAllLaps, "All laps saved.", 1.0, ("combined",))
                saveThread.signals.finished.connect(self.data.showUiMsg)
                self.data.threadpool.start(saveThread)

sb.component.componentLibrary['SaveLaps'] = SaveLaps

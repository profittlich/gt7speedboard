from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import sb.component
from sb.gt7telepoint import Point
from sb.helpers import logPrint
from sb.gt7widgets import PedalWidget
from sb.laps import Lap
from sb.helpers import Worker
import os

import copy

class LapOptimizer(sb.component.Component):
    def description():
        return "Generate synthetic laps with optimized brake points from previous laps"
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

    def getWidget(self):
        return None

    def addPoint(self, curPoint, curLap):
        if not self.cfg.circuitExperience:
            self.optimizeLap(curPoint)

    def newSession(self):
        logPrint("=== CALL ===")
        self.initOptimizedLap()

    def completedLap(self, curPoint, lastLap, isFullLap):
        if not self.cfg.circuitExperience:
            self.updateOptimizedLap()

    def defaultTitle(self):
        return "Lap optimizer"

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

    def appendOptimizedLap(self, index, name):
        if not hasattr(self, 'dev_contLap'):
            self.dev_contLap = 1
        else:
            self.dev_contLap += 1
        for p in index.points:
            p.current_lap = self.dev_contLap
            p.recreatePackage()
        self.appendLap(index, name)

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

sb.component.componentLibrary['LapOptimizer'] = LapOptimizer

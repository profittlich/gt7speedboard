import sys
from sb.gt7telepoint import Point
from sb.helpers import logPrint
from sb.laps import loadLap
from sb.laps import Lap
import platform
import copy
import glob
import threading
import time
from pathlib import Path

class TrackInfo:
    def __init__(self):
        self.lap = None
        self.name = None
        self.hits = []
        self.firstHit = None
        self.curPos = 0
        self.forwardCount = 0
        self.reverseCount = 0
        self.identifiedAt = 2**31

class TrackDetector:
    def __init__(self):
        self.curLap = Lap()
        self.totalPoints = 0
        self.curLapQueue = Lap()
        self.cooldown = 0
        self.loadedTracks = []
        self.tracks = []
        self.eliminateDistance = 30
        self.minHitsForTrack = 5
        self.validAngle = 15
        self.maxGapLength = 10
        self.minPointsForDetection = 300
        self.thread = threading.Thread(target=self.detectionLoop, args=())
        self.running = True
        self.thread.start()


    def reset(self):
        logPrint("Reset track detector")
        self.curLap = Lap()
        self.totalPoints = 0
        self.curLapQueue = Lap()
        self.tracks = copy.deepcopy(self.loadedTracks)
        self.cooldown = 1200



    def loadRefs(self, refs):
        self.loadedTracks = []
        for r in refs:
            curTrack = TrackInfo()
            curTrack.lap = loadLap(r)
            curTrack.hits = [ False ] * len(curTrack.lap.points)
            curTrack.name = r.replace(".gt7track", "")
            curTrack.name = curTrack.name[curTrack.name.rfind("/")+1:]
            self.loadedTracks.append(curTrack)
        self.tracks = copy.deepcopy(self.loadedTracks)

    def loadRefsFromDirectory(self, drctry):
        self.loadedTracks = []
        fns = glob.glob('*.gt7track', root_dir=drctry)
        for fn in fns:
            curTrack = TrackInfo()
            curTrack.lap = loadLap(drctry + "/" + fn)
            curTrack.hits = [ False ] * len(curTrack.lap.points)
            curTrack.name = fn.replace(".gt7track", "")
            self.loadedTracks.append(curTrack)
        self.tracks = copy.deepcopy(self.loadedTracks)
            

    def loadTarget (self, fni):
        self.loadedLap = loadLap(fni)

    def hasGaps(self, t):
        hits = t.hits
        gapCountdown = self.maxGapLength
        if not True in hits:
            return False
        if t.firstHit is None:
            rhits = hits
        else:
            rhits = hits[t.firstHit:]
        rhits = list(reversed(rhits))
        for h in rhits[rhits.index(True):-1]:
            if not h:
                gapCountdown -= 1
            else:
                if gapCountdown <= 0:
                    return True
                gapCountdown = self.maxGapLength

        return False

    def checkPrefix(self):
        if len(self.tracks) == 0:
            return False
        curPrefix = self.tracks[0].name[:self.tracks[0].name.index(" - ")]
        match = True
        enoughHits = False
        for t in self.tracks:
            if t.name[:len(curPrefix)] != curPrefix:
                match = False
            if t.hits.count(True) >= self.minHitsForTrack:
                enoughHits = True

        return match and enoughHits

    def getTrack(self):
        if len(self.tracks) == 0:
            curTrack = "Unknown track"
            return curTrack
        elif len(self.tracks) == 1 and self.tracks[0].hits.count(True) >= self.minHitsForTrack and self.tracks[0].identifiedAt < self.totalPoints - 60:
            curTrack = self.tracks[0].name
            if self.tracks[0].reverseCount > self.tracks[0].forwardCount:
                curTrack += " - reversed"
            return curTrack
        elif self.checkPrefix():
            curTrack = self.tracks[0].name[:self.tracks[0].name.index(" - ")]
            return curTrack
        else:
            return "Multiple track candidates"

    def stopDetection(self):
        self.running = False

    def trackIdentified(self):    
        if len(self.tracks) == 0:
            return False
        elif len(self.tracks) == 1 and self.tracks[0].hits.count(True) >= self.minHitsForTrack and self.tracks[0].identifiedAt < self.totalPoints - 60:
            return True
        else:
            return False

    def addPoint(self, p):
        if p.car_speed > 0.0:
            self.curLapQueue.points.append(p)

    def determineTrackProgress(self, p): # TODO: Lap change error
        try:
            lp, pi, d = self.tracks[0].lap.findClosestPointNoLimit(p)
            prog = (lp.package_id - self.tracks[0].lap.points[0].package_id) / (self.tracks[0].lap.points[-1].package_id - self.tracks[0].lap.points[0].package_id)
            if self.tracks[0].forwardCount > self.tracks[0].reverseCount:
                return prog
            else:
                return 1-prog
        except Exception as e:
            logPrint("EXCEPTION")
            logPrint(str(e))
            logPrint(len(self.tracks))
            return 0

    def detectionLoop(self):
        testPath = Path("./tracks")
        if testPath.is_dir():
            self.loadRefsFromDirectory("./tracks")
        elif platform.system() == "Darwin":
            self.loadRefsFromDirectory(sys.argv[0][:sys.argv[0].rfind("/")] + "/../Resources/tracks")
        while self.running:
            if len(self.curLapQueue.points) > 0:
                if self.cooldown > 0:
                    if self.cooldown % 60 == 0:
                        logPrint("Cooldown", self.cooldown)
                    self.cooldown -= 1
                    self.curLapQueue.points.pop(0)
                else:
                    self.curLap.points.append(self.curLapQueue.points.pop(0))
                    if self.totalPoints + len(self.curLap.points) > self.minPointsForDetection:
                        self.detect()
                        self.curLap = Lap()
            else:
                time.sleep(0.005)

    def detect(self):
        for curPoint in self.curLap.points:
            self.totalPoints += 1
            for t in self.tracks:
                # TODO detect finish line position
                lp, pi, d = t.lap.findClosestPointNoLimit(curPoint)
    
                eliminateDistance = self.eliminateDistance
                if "Daytona" in t.name:
                    eliminateDistance = 60 # TODO: Daytona has a distant pit lane, find better solution than a special case
    
                if d > eliminateDistance:
                    self.tracks.remove(t)
                    if self.checkPrefix():
                        logPrint("Track group:", self.tracks[0].name[:self.tracks[0].name.index(" - ")], "after", self.totalPoints)
                    if len(self.tracks) == 1:
                        logPrint("Remaining track:", self.tracks[0].name, "after", self.totalPoints, ", hits:", t.hits.count(True))
                        self.tracks[0].identifiedAt = self.totalPoints
                elif self.hasGaps(t):
                    logPrint("Eliminate", t.name, "due to gaps", pi, t.curPos, d, lp.current_lap, "after", self.totalPoints, "first", t.firstHit)
                    logPrint(t.hits, t.hits.index(True))
                    self.tracks.remove(t)
                    #logPrint("Track candidates left:", len(self.tracks))
                    if self.checkPrefix():
                        logPrint("Track group:", self.tracks[0].name[:self.tracks[0].name.index(" - ")], "after", self.totalPoints)
                    if len(self.tracks) == 1:
                        logPrint("Remaining track:", self.tracks[0].name, "after", self.totalPoints, ", hits:", t.hits.count(True))
                        self.tracks[0].identifiedAt = self.totalPoints
                else:
                    a = lp.angle(curPoint)
                    if a < (3.14159 * self.validAngle / 180):
                        t.forwardCount += 1
                        if t.firstHit is None:
                            #logPrint(t.name, "First hit:", pi)
                            t.firstHit = pi
                        elif t.hits[t.firstHit-1]:
                            t.firstHit = 0
                        t.hits[pi] = True
                    elif a > (3.14159 * (180 - self.validAngle) / 180):
                        t.reverseCount += 1
                        if t.firstHit is None:
                            #logPrint(t.name, "First hit:", pi)
                            t.firstHit = pi
                        elif t.hits[t.firstHit-1]:
                            t.firstHit = 0
                        t.hits[pi] = True
                    t.curPos = pi
        if len(self.tracks) == 0:
            logPrint("Found no track, try again", "after", self.totalPoints)
            self.reset()


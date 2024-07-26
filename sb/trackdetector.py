import sys
from sb.gt7telepoint import Point
from sb.helpers import loadLap
from sb.helpers import Lap
import copy
import glob
import threading
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

class TrackDetector:
    def __init__(self):
        self.curLap = Lap()
        self.curLapQueue = Lap()
        self.loadedTracks = []
        self.tracks = []
        self.eliminateDistance = 30
        self.validAngle = 15
        self.maxGapLength = 10
        self.lastTrack =  "Multiple track candidates"
        self.thread = threading.Thread(target=self.detectionLoop, args=())
        self.running = True
        self.thread.start()


    def reset(self):
        self.curLap = Lap()
        self.curLapQueue = Lap()
        self.tracks = copy.deepcopy(self.loadedTracks)


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
        for t in self.tracks:
            if t.name[:len(curPrefix)] != curPrefix:
                match = False

        return match

    def getTrack(self):
        if len(self.tracks) == 0:
            self.lastTrack = "Unknown track"
            return self.lastTrack
        elif len(self.tracks) == 1:
            self.lastTrack = self.tracks[0].name
            if self.tracks[0].reverseCount > self.tracks[0].forwardCount:
                self.lastTrack += " - reversed"
            return self.lastTrack
        elif self.checkPrefix():
            self.lastTrack = self.tracks[0].name[:self.tracks[0].name.index(" - ")]
            return self.lastTrack
        else:
            return "Multiple track candidates"

    def stopDetection(self):
        self.running = False

    def getLastTrack(self):
        return self.lastTrack

    def trackIdentified(self):    
        if len(self.tracks) == 0:
            return False
        elif len(self.tracks) == 1 and len(self.curLap.points) > 100:
            return True
        else:
            return False

    def addPoint(self, p):
        if p.car_speed > 0.0:
            self.curLapQueue.points.append(p)
            #self.detect()

    def determineTrackProgress(self, p): # TODO: Lap change error
        lp, pi, d = self.tracks[0].lap.findClosestPointNoLimit(p)
        prog = (lp.package_id - self.tracks[0].lap.points[0].package_id) / (self.tracks[0].lap.points[-1].package_id - self.tracks[0].lap.points[0].package_id)
        if self.tracks[0].forwardCount > self.tracks[0].reverseCount:
            return prog
        else:
            return 1-prog

    def detectionLoop(self):
        testPath = Path("./tracks")
        if testPath.is_dir():
            self.loadRefsFromDirectory("./tracks")
        elif platform.system() == "Darwin":
            self.loadRefsFromDirectory(sys.argv[0][:sys.argv[0].rfind("/")] + "/../Resources/tracks")
        while self.running:
            if len(self.curLapQueue.points) > 0:
                self.curLap.points.append(self.curLapQueue.points.pop(0))
                if len(self.curLap.points) > 100:
                    self.detect()

    def detect(self): # TODO use threading or are reference tracks small enough?
        hasEliminated = False
        for t in self.tracks:
            # TODO detect finish line position
            lp, pi, d = t.lap.findClosestPointNoLimit(self.curLap.points[-1])
            eliminateDistance = self.eliminateDistance
            if "Daytona" in t.name:
                eliminateDistance = 60 # TODO: Daytona has a distant pit lane, find better solution than a special case
            if d > eliminateDistance:
                #print("Eliminate", t.name, pi, d, lp.current_lap, "after", len(self.curLap.points))
                self.tracks.remove(t)
                hasEliminated = True
                #print("Track candidates left:", len(self.tracks))
                if self.checkPrefix():
                    print("Track group:", self.tracks[0].name[:self.tracks[0].name.index(" - ")])
                if len(self.tracks) == 1:
                    print("Remaining track:", self.tracks[0].name, "after", len(self.curLap.points))
            elif self.hasGaps(t):
                print("Eliminate", t.name, "due to gaps", pi, t.curPos, d, lp.current_lap, "after", len(self.curLap.points), "first", t.firstHit)
                print(t.hits, t.hits.index(True))
                self.tracks.remove(t)
                hasEliminated = True
                #print("Track candidates left:", len(self.tracks))
                if self.checkPrefix():
                    print("Track group:", self.tracks[0].name[:self.tracks[0].name.index(" - ")])
                if len(self.tracks) == 1:
                    print("Remaining track:", self.tracks[0].name, "after", len(self.curLap.points))
            else:
                a = self.curLap.angle(lp, self.curLap.points[-1])
                if a < (3.14159 * self.validAngle / 180):
                    t.forwardCount += 1
                    if t.firstHit is None:
                        #print(t.name, "First hit:", pi)
                        t.firstHit = pi
                    elif t.hits[t.firstHit-1]:
                        t.firstHit = 0
                    t.hits[pi] = True
                elif a > (3.14159 * (180 - self.validAngle) / 180):
                    t.reverseCount += 1
                    if t.firstHit is None:
                        #print(t.name, "First hit:", pi)
                        t.firstHit = pi
                    elif t.hits[t.firstHit-1]:
                        t.firstHit = 0
                    t.hits[pi] = True
                t.curPos = pi
        #if hasEliminated:
            #print("Tracks were eliminated")
            #for t in self.tracks:
                #print(t.name, round(100 * t.hits.count(True) / len(t.hits)), "%", t.firstHit)
        if len(self.tracks) == 0:
            print("Found no track, try again")
            self.reset()

    def detector (self):
        p = self.loadedLap.points[0]
        print(self.loadedLap.points[0].current_lap, self.loadedLap.points[-1].current_lap)
        count = 0
        for p in self.loadedLap.points:
            count += 1
            self.addPoint(p)
            if len(self.tracks) == 0:
                print ("")
                print ("Search failed")
                print ("")
            if len(self.tracks) == 1 and count > 10:
                print ("")
                if self.tracks[0].forwardCount > self.tracks[0].reverseCount:
                    print ("Identified: " + self.tracks[0].name)
                else:
                    print ("Identified: " + self.tracks[0].name + " - reversed")
                print ("")
                break

        print ("")
        print ("Finished after", count, "points of", len(self.curLap.points))
        print ("")
        best = 0
        count = -1
        for t in self.tracks:
            count += 1
            if t.hits.count(True) / len(t.lap.points) > best:
                best = t.hits.count(True) / len(t.lap.points)
                result = count
            print(t.name + ":", 100 * t.hits.count(True) / len(t.lap.points), "%", "F:", t.forwardCount, "R:", t.reverseCount)

        if count >= 0:
            print ("")
            print ("Chosen: " + self.tracks[result].name)
            print ("")

if __name__ == '__main__':
    detector = TrackDetector()
    detector.loadRefs(sys.argv[1:-1])
    detector.loadTarget(sys.argv[-1])
    detector.detector()

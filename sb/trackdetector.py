import sys
from sb.gt7telepoint import Point
from sb.helpers import loadLap
from sb.helpers import Lap
import copy
import glob

class TrackInfo:
    def __init__(self):
        self.lap = None
        self.name = None
        self.hits = []
        self.curPos = 0
        #self.aggregateDist = 0
        #self.numAggregateDist = 0
        self.forwardCount = 0
        self.reverseCount = 0

class TrackDetector:
    def __init__(self):
        self.lap = Lap()
        self.tracks = []
        self.eliminateDistance = 30
        self.validAngle = 15
        #self.maxPointSkip = 5
        self.maxGapLength = 10
        self.pointsAdded = 0

    def loadRefs(self, refs):
        for r in refs:
            curTrack = TrackInfo()
            curTrack.lap = loadLap(r)
            curTrack.hits = [ False ] * len(curTrack.lap.points)
            curTrack.name = r.replace(".gt7track", "")
            curTrack.name = curTrack.name[curTrack.name.rfind("/")+1:]
            self.tracks.append(curTrack)

    def loadRefsFromDirectory(self, drctry):
        fns = glob.glob('*.gt7track', root_dir=drctry)
        for fn in fns:
            curTrack = TrackInfo()
            curTrack.lap = loadLap(drctry + "/" + fn)
            curTrack.hits = [ False ] * len(curTrack.lap.points)
            curTrack.name = fn.replace(".gt7track", "")
            #curTrack.name = curTrack.name[curTrack.name.rfind("/")+1:]
            self.tracks.append(curTrack)
            

    def loadTarget (self, fni):
        self.loadedLap = loadLap(fni)

    def hasGaps(self, hits):
        gapCountdown = self.maxGapLength
        if not True in hits:
            return False
        rhits = list(reversed(hits))
        for h in rhits[rhits.index(True):]:
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
            print(t.name, curPrefix)
            if t.name[:len(curPrefix)] != curPrefix:
                match = False

        return match

    def addPoint(self, p):
        self.pointsAdded += 1
        self.lap.points.append(p)
        for t in self.tracks:
            # TODO detect finish line position
            lp, pi, d = t.lap.findClosestPointNoLimit(p)
            if d > self.eliminateDistance:
                print("Eliminate", t.name, pi, d, lp.current_lap)
                print(p.position_x, p.position_y, p.position_z)
                print(lp.position_x, lp.position_y, lp.position_z)
                print("")
                self.tracks.remove(t)
                if self.checkPrefix():
                    print("Track group:", self.tracks[0].name[:self.tracks[0].name.index(" - ")])
                if len(self.tracks) == 1:
                    print("Remaining track:", self.tracks[0].name)
            elif self.hasGaps(t.hits):
                print("Eliminate", t.name, "due to gaps", pi, t.curPos, d, lp.current_lap)
                self.tracks.remove(t)
                if self.checkPrefix():
                    print("Track group:", self.tracks[0].name[:self.tracks[0].name.index(" - ")])
                if len(self.tracks) == 1:
                    print("Remaining track:", self.tracks[0].name)
            else:
                #if pi != t.curPos:
                    #diffp = (pi - t.curPos)
                    #if abs(diffp) < self.maxPointSkip:
                        #t.aggregateDist += d
                        #t.numAggregateDist += 1
                a = self.lap.angle(lp, p)
                if a < (3.14159 * self.validAngle / 180):
                    t.forwardCount += 1
                    t.hits[pi] = True
                elif a > (3.14159 * (180 - self.validAngle) / 180):
                    t.reverseCount += 1
                    t.hits[pi] = True
                t.curPos = pi

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
        print ("Finished after", count, "points of", len(self.lap.points))
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

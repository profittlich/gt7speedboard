import math

from sb.crypt import salsa20_dec, salsa20_enc
from sb.gt7telepoint import Point


class PositionPoint:
    def __init__(self):
        self.position_x = 0
        self.position_y = 0
        self.position_z = 0

# TODO own file
class Lap:
    def __init__(self, time = None, pts = None, valid=True):
        self.time = time
        if pts is None:
            self.points = []
        else:
            self.points = pts
        self.valid = valid

    def flatDistance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_z-p2.position_z)**2)

    def distance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_y-p2.position_y)**2 + (p1.position_z-p2.position_z)**2)

    def length(self):
        totalDist = 0
        for i in range(1, len(self.points)):
            totalDist += self.distance(self.points[i-1], self.points[i])
        return totalDist

def loadLap(fn):
    lap = Lap()
    if len(fn)>0:
        print(fn)
        with open(fn, "rb") as f:
            allData = f.read()
            curIndex = 0
            print(len(allData))
            while curIndex < len(allData):
                data = allData[curIndex:curIndex + 296]
                curIndex += 296
                ddata = salsa20_dec(data)
                curPoint = Point(ddata, data)
                lap.points.append(curPoint)
    print(len(lap.points))
    return lap

def loadLaps(fn):
    result = []
    if len(fn)>0:
        print(fn)
        with open(fn, "rb") as f:
            allData = f.read()
            curIndex = 0
            curLap = -10
            print(len(allData))
            while curIndex < len(allData):
                data = allData[curIndex:curIndex + 296]
                curIndex += 296
                ddata = salsa20_dec(data)
                curPoint = Point(ddata, data)
                if curPoint.current_lap != curLap:
                    curLap = curPoint.current_lap
                    result.append(Lap())
                result[-1].points.append(curPoint)
    return result

def indexToTime(i, compensate=1):
    i += 0.5 * compensate
    minu = i // (60*60)
    sec = str(i // 60 - minu*60)
    if len(sec) < 2:
        sec = "0" * (2-len(sec)) + sec
    msec = str((i % 60) * 1/60)[2:5]
    if len(msec) < 3:
        msec += "0" * (3-len(msec))
    result = "{minu:1.0f}:{sec}:{msec}".format(minu = minu, sec = sec, msec = msec)
    return result


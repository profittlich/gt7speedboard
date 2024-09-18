import math
import struct
from sb.helpers import logPrint

from sb.crypt import salsa20_dec, salsa20_enc
from sb.gt7telepoint import Point


class PositionPoint:
    def __init__(self):
        self.position_x = 0
        self.position_y = 0
        self.position_z = 0

# TODO own file
class Lap:
    def __init__(self, time = None, pts = None, valid=True, following=None, preceeding=None):
        self.time = time
        if pts is None:
            self.points = []
        else:
            self.points = pts
        self.valid = valid
        self.following = following
        self.preceeding = preceeding

    def flatDistance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_z-p2.position_z)**2)

    def distance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_y-p2.position_y)**2 + (p1.position_z-p2.position_z)**2)

    def angle(self, p1, p2):
        s = (math.sqrt(p1.velocity_x**2 + p1.velocity_y**2 + p1.velocity_z**2) * math.sqrt(p2.velocity_x**2 + p2.velocity_y**2 + p2.velocity_z**2))
        if s == 0:
            return 0
        a = min(1,(p1.velocity_x * p2.velocity_x + p1.velocity_y * p2.velocity_y + p1.velocity_z * p2.velocity_z) / s)
        r = math.acos(a)
        return r

    def length(self):
        totalDist = 0
        for i in range(1, len(self.points)):
            totalDist += self.distance(self.points[i-1], self.points[i])
        return totalDist

    def updateTime(self):
        if self.following is None:
            self.time = len(self.points) * 1000/59.94
        else:
            self.time = self.following.last_lap

    def findClosestPointNoLimit(self, p):
        shortestDistance = 100000000
        result = None
        for p2 in range(len(self.points)):
            curDist = self.distance(p, self.points[p2])
            if curDist < shortestDistance:
                shortestDistance = curDist
                result = p2

        return self.points[result], result, shortestDistance

    def topSpeed(self):
        topSpeed = 0
        for p2 in self.points:
            if topSpeed < p2.car_speed:
                topSpeed = p2.car_speed

        return topSpeed

def loadLap(fn):
    laps = loadLaps(fn)
    for l in laps:
        if l.valid:
            return l
    if len(laps) > 0:
        return laps[0]
    else:
        emptyLap = Lap()
        emptyLap.updateTime()
        return emptyLap

def loadLaps(fn):
    result = []
    if len(fn)>0:
        logPrint("Load laps:", fn)
        with open(fn, "rb") as f:
            allData = f.read()
            curIndex = 0
            curLap = -10
            while curIndex < len(allData):
                data = allData[curIndex:curIndex + 296]
                curIndex += 296
                magic = struct.unpack('i', data[0x00:0x00 + 4])[0] # 0x47375330
                if magic == 0x47375330:
                    ddata = data
                else:
                    ddata = salsa20_dec(data)
                curPoint = Point(ddata, data)
                if curPoint.current_lap != curLap:
                    curLap = curPoint.current_lap
                    result.append(Lap())
                result[-1].points.append(curPoint)
    for i in range(1, len(result)):
        if result[i].points[0].current_lap == result[i-1].points[-1].current_lap+1:
            result[i].preceeding = result[i-1].points[-1]
            result[i-1].following = result[i].points[0]
        
    kick = []
    for i in range(0, len(result)):
        if (len(result[i].points) == 1):
            kick.append(i)

    for i in reversed(kick):
        result.pop(i)

    for i in range(0, len(result)):
        #print("End point distance:", result[i].distance(result[i].points[0], result[i].points[-1]))
        result[i].updateTime()
        #print("Time:", result[i].time)
        if result[i].distance(result[i].points[0], result[i].points[-1]) > 20: # TODO load from constants
            result[i].valid = False
        
    return result

import math
import sys
import os
import platform
import csv

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
        a = min(1,(p1.velocity_x * p2.velocity_x + p1.velocity_y * p2.velocity_y + p1.velocity_z * p2.velocity_z) / (math.sqrt(p1.velocity_x**2 + p1.velocity_y**2 + p1.velocity_z**2) * math.sqrt(p2.velocity_x**2 + p2.velocity_y**2 + p2.velocity_z**2)))
        r = math.acos(a)
        return r

    def length(self):
        totalDist = 0
        for i in range(1, len(self.points)):
            totalDist += self.distance(self.points[i-1], self.points[i])
        return totalDist

    def updateTime(self):
        if self.following is None:
            self.time = len(self.points) * 1/59.94
            print("Estimate time", len(self.points), self.time)
        else:
            self.time = self.following.last_lap
            print("Use following time", self.time)
        print(msToTime(self.time))

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
    lap = Lap()
    if len(fn)>0:
        print(fn)
        with open(fn, "rb") as f:
            allData = f.read()
            curIndex = 0
            print(len(allData)/296, "frames")
            while curIndex < len(allData):
                data = allData[curIndex:curIndex + 296]
                curIndex += 296
                ddata = salsa20_dec(data)
                curPoint = Point(ddata, data)
                if len(lap.points) == 1 and curPoint.current_lap != lap.points[0].current_lap:
                    print("Found preceeding point")
                    lap.preceeding = lap.points[0]
                    lap.points = []
                lap.points.append(curPoint)
            if len(lap.points) > 1 and lap.points[-1].current_lap != lap.points[-2].current_lap:
                print("Found following point")
                lap.following = lap.points[-1]
                lap.points.pop(-1)
            
    print(len(lap.points))
    lap.updateTime()
    return lap

def loadLaps(fn):
    result = []
    if len(fn)>0:
        print(fn)
        with open(fn, "rb") as f:
            allData = f.read()
            curIndex = 0
            curLap = -10
            print(len(allData)/296, "frames")
            while curIndex < len(allData):
                data = allData[curIndex:curIndex + 296]
                curIndex += 296
                ddata = salsa20_dec(data)
                curPoint = Point(ddata, data)
                if curPoint.current_lap != curLap:
                    curLap = curPoint.current_lap
                    result.append(Lap())
                result[-1].points.append(curPoint)
    for i in range(1, len(result)):
        if result[i].points[0].current_lap == result[i-1].points[-1].current_lap+1:
            print("Found preceeding/following points")
            result[i].preceeding = result[i-1].points[-1]
            result[i-1].following = result[i].points[0]
        
    if (len(result[0].points) == 1):
        result.pop(0)
    if (len(result[-1].points) == 1):
        result.pop(-1)

    return result

def indexToTime(i):
    fsec = i * 1/59.94
    
    minu = fsec // 60
    sec = fsec - minu * 60

    spref = ""
    if sec < 10:
        spref = "0"
    
    return "{minu:1.0f}:{spref}{sec:2.3f}".format(minu = minu, spref=spref, sec = sec)

def msToTime (ms):
    tm = int((ms/1000) // 60)
    ts = int((ms/1000) % 60)
    tms = int(round((ms/1000 % 60 - ts) * 1000))

    ts = str(ts)
    if len(ts) < 2:
        ts = "0" * (2-len(ts)) + ts
    tms = str(tms)
    if len(tms) < 3:
        tms = "0" * (3-len(tms)) + tms

    lt = "{minu:1.0f}:{sec}.{msec}".format(minu = tm, sec = ts, msec = tms)
    return lt

carIds = {}
carMakers = {}

def loadCarIds():
    global carIds
    global carMakers
       
    try:
        with open("makers.csv", 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                carMakers[row[0]] = row[1]
    except:
        if platform.system() == "Darwin":
            altFile = sys.argv[0][:sys.argv[0].rfind("/")] + "/../Resources/makers.csv"
            with open(altFile, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    carMakers[row[0]] = row[1]
        else:
            raise


    try:
        with open("cars.csv", 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                carIds[row[0]] = row
    except:
        if platform.system() == "Darwin":
            altFile = sys.argv[0][:sys.argv[0].rfind("/")] + "/../Resources/cars.csv"
            with open(altFile, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    carIds[row[0]] = row
        else:
            raise

def idToCar(i):
    global carIds
    global carMakers
    try:
        return carMakers[str(carIds[str(i)][2])] + " - " + carIds[str(i)][1]
    except:
        return "Unknown car"


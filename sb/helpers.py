import math
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

    def angle(self, p1, p2):
        a = min(1,(p1.velocity_x * p2.velocity_x + p1.velocity_y * p2.velocity_y + p1.velocity_z * p2.velocity_z) / (math.sqrt(p1.velocity_x**2 + p1.velocity_y**2 + p1.velocity_z**2) * math.sqrt(p2.velocity_x**2 + p2.velocity_y**2 + p2.velocity_z**2)))
        r = math.acos(a)
        return r

    def length(self):
        totalDist = 0
        for i in range(1, len(self.points)):
            totalDist += self.distance(self.points[i-1], self.points[i])
        return totalDist

    def findClosestPointNoLimit(self, p):
        shortestDistance = 100000000
        result = None
        for p2 in range(len(self.points)):
            curDist = self.distance(p, self.points[p2])
            if curDist < shortestDistance:
                shortestDistance = curDist
                result = p2

        return self.points[result], result, shortestDistance

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
    with open("makers.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            carMakers[row[0]] = row[1]


    with open("cars.csv", 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            carIds[row[0]] = row

def idToCar(i):
    global carIds
    global carMakers
    return carMakers[str(carIds[str(i)][2])] + " - " + carIds[str(i)][1]


from salsa20 import Salsa20_xor
import math
from gt7telepoint import Point

def salsa20_dec(dat):
    KEY = b'Simulator Interface Packet GT7 ver 0.0'
    # Seed IV is always located here
    oiv = dat[0x40:0x44]
    iv1 = int.from_bytes(oiv, byteorder='little')
    # Notice DEADBEAF, not DEADBEEF
    iv2 = iv1 ^ 0xDEADBEAF
    IV = bytearray()
    IV.extend(iv2.to_bytes(4, 'little'))
    IV.extend(iv1.to_bytes(4, 'little'))
    ddata = Salsa20_xor(dat, bytes(IV), KEY[0:32])
    magic = int.from_bytes(ddata[0:4], byteorder='little')
    if magic != 0x47375330:
        return bytearray(b'')
    return ddata

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

def indexToTime(i):
    minu = i // (60*60)
    sec = str(i // 60 - minu*60)
    if len(sec) < 2:
        sec = "0" * (2-len(sec)) + sec
    msec = str((i % 60) * 1/60)[2:5]
    if len(msec) < 3:
        msec += "0" * (3-len(msec))
    result = "{minu:1.0f}:{sec}:{msec}".format(minu = minu, sec = sec, msec = msec)
    return result


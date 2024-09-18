import sys
from sb.gt7telepoint import Point
from sb.helpers import loadLap
from sb.helpers import Lap
import copy

def thinOut (fni, fno, step=50):
    sep = ";"
    lap = loadLap(fni)
    lap2 = Lap()
    pOld = lap.points[0]
    lap2.points.append(pOld)
    for p in range(1, len(lap.points)):
        pNew = lap.points[p]

        if pOld.distance(pNew) > step or pOld.angle(pNew) > 3.14159 * 10 / 180:
            lap2.points.append(pNew)
            print("Angle:", 180 * pOld.angle(pNew)/ 3.14159)
            pOld = pNew
    
    with open ( fno, "wb") as f:
        for p in lap2.points:
            f.write(p.raw)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: laptotrack <lapfile> <trackfile> [<stepsize>]")
    else:
        step = 50
        if len(sys.argv) > 3:
            step = int(sys.argv[3])
        thinOut(sys.argv[1], sys.argv[2], step)


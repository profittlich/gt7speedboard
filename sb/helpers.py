import sys
import os
import platform
import csv
import inspect
import time
import statistics

from PyQt6.QtCore import *
from sb.crypt import salsa20_dec, salsa20_enc

class WorkerSignals(QObject):
    finished = pyqtSignal(str, float)

class Worker(QRunnable, QObject):
    def __init__(self, func, msg, t, args=()):
        super(Worker, self).__init__()
        self.func = func
        self.msg = msg
        self.t = t
        self.args = args
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        altMsg = self.func(*self.args)
        if altMsg is None:
            self.signals.finished.emit(self.msg, self.t)
        else:
            self.signals.finished.emit(altMsg, self.t)

class StopWatch():
    def __init__(self):
        self.stopWatchTimes = []
        self.stopWatchCount = 0
        self.stopWatchIndex = 0
        self.stopWatchTime = time.perf_counter()

    def init(self):
        self.stopWatchTime = time.perf_counter()
        self.stopWatchIndex = 0
        self.stopWatchCount += 1

    def lap(self, title=None):
        newTime = time.perf_counter()
        if len(self.stopWatchTimes) <= self.stopWatchIndex:
            self.stopWatchTimes.append([[], title])
        self.stopWatchTimes[self.stopWatchIndex][0].append(newTime - self.stopWatchTime)
        self.stopWatchIndex += 1
        self.stopWatchTime = newTime

    def print(self):
        logPrint(" === STOP WATCH RESULTS ===")
        for i in range(len(self.stopWatchTimes)):
            q = sorted(self.stopWatchTimes[i][0])
            if len(self.stopWatchTimes[i][0]) >= 2:
                logPrint(i, 
                    "\tmean:", "{0:6.0f}".format(round(1000000 * sum(self.stopWatchTimes[i][0]) / len(self.stopWatchTimes[i][0]))), 
                    "\tmedian:", "{0:6.0f}".format(round(1000000 * q[int(len(q)/2)])),
                    "\tmin:", "{0:6.0f}".format(round(1000000*min(self.stopWatchTimes[i][0]))), 
                    "\tQ90:", "{0:6.0f}".format(round(1000000 * q[int(0.9*len(q))])),
                    "\tQ99:", "{0:6.0f}".format(round(1000000 * q[int(0.99*len(q))])),
                    "\tQ99.9:", "{0:6.0f}".format(round(1000000 * q[int(0.999*len(q))])),
                    "\tmax:", "{0:6.0f}".format(round(1000000*max(self.stopWatchTimes[i][0]))), "{0:5.0f}".format(self.stopWatchTimes[i][0].index(max(self.stopWatchTimes[i][0]))),
                    "\tstdev:", "{0:6.0f}".format(round(1000000 * statistics.stdev(self.stopWatchTimes[i][0]))),
                    "\tsamples:", len(self.stopWatchTimes[i][0]),
                    self.stopWatchTimes[i][1], 
                    )
            else:
                logPrint(self.stopWatchTimes[i][1], self.stopWatchTimes[i][0])

def indexToTime(i):
    fsec = i * 1/59.94
    
    minu = fsec // 60
    sec = fsec - minu * 60

    spref = ""
    if sec < 10:
        spref = "0"
    
    return "{minu:1.0f}:{spref}{sec:2.3f}".format(minu = minu, spref=spref, sec = sec)

def msToTime (ms):
    if ms < 0:
        return "no time"
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
        return "Unknown car (" + str(i) + ")"


def logPrint(*args, **kwargs):
    lines = inspect.stack()[1]
    print(lines.filename[lines.filename.rfind('/')+1:] + "::" +  str(lines.lineno) + " [" + lines.function + "()]:", *args, **kwargs)

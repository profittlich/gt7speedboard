import sys
import os
import platform
import csv
import inspect

from sb.crypt import salsa20_dec, salsa20_enc
from sb.gt7telepoint import Point


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
        return "Unknown car (" + str(i) + ")"


def logPrint(*args, **kwargs):
    lines = inspect.stack()[1]
    print(lines.filename[lines.filename.rfind('/')+1:] + "::" +  str(lines.lineno) + " [" + lines.function + "()]:", *args, **kwargs)

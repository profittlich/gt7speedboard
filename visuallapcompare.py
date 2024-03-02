import sys
from statistics import mean
import os
import threading
import traceback
import json
from wakepy import keep
import math
import queue
import datetime
from cProfile import Profile
from pstats import SortKey, Stats

from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QSettings, QEvent
from PyQt6.QtGui import QColor, QRegularExpressionValidator, QPixmap, QPainter, QPalette, QPen, QLinearGradient, QGradient, QPainterPath
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox

from gt7telepoint import Point
from helpers import loadLap
from helpers import Lap, PositionPoint

import gt7telemetryreceiver as tele
from gt7widgets import *

class CrossMarker:
    def __init__(self, group, x1, z1, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class PlusMarker:
    def __init__(self, group, x1, z1, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class SquareMarker:
    def __init__(self, group, x1, z1, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class CircleMarker:
    def __init__(self, group, x1, z1, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class UpMarker:
    def __init__(self, group, x1, z1, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class DownMarker:
    def __init__(self, group, x1, z1, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.color = color
        self.bold = bold

class LeftLineMarker:
    def __init__(self, group, x1, z1, x2, z2, color, bold=1, endText = None):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.x2 = x2
        self.z2 = z2
        self.color = color
        self.bold = bold
        self.endText = endText

class Text:
    def __init__(self, group, x1, z1, text, offsetx, offsetz, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.offsetx = offsetx
        self.offsetz = offsetz
        self.text = text
        self.color = color
        self.bold = bold

class Line:
    def __init__(self, group, x1, z1, x2, z2, color, bold=1):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.x2 = x2
        self.z2 = z2
        self.color = color
        self.bold = bold

class Triangle:
    def __init__(self, group, x1, z1, x2, z2, x3, z3, color):
        self.group = group
        self.x1 = x1
        self.z1 = z1
        self.x2 = x2
        self.z2 = z2
        self.x3 = x3
        self.z3 = z3
        self.color = color

class MapView2(QWidget):

    def __init__(self, lap1 = None, lap2 = None):
        super().__init__()
        self.lap1 = lap1
        self.lap2 = lap2
        self.zoom = 1/1.1
        self.offsetX = 0
        self.offsetZ = 0
        self.showText = True
        self.showLayers = [ True, ] * 5
        self.showGroups = {}
        self.dragging = False

    def setLaps(self, lap1, lap2):
        self.lap1 = lap1
        self.lap2 = lap2
        self.findExtents()
        self.makeGraphic()

    # MAP CONTROL
    def moveLeft(self):
        self.offsetX += 20/self.zoom
        self.update()

    def moveRight(self):
        self.offsetX -= 20/self.zoom
        self.update()

    def moveUp(self):
        self.offsetZ += 20/self.zoom*self.aspectRatio
        self.update()

    def moveDown(self):
        self.offsetZ -= 20/self.zoom*self.aspectRatio
        self.update()

    def zoomIn(self, factor = 1.1):
        self.zoom *= factor
        if self.zoom > 400:
            self.zoom = 400
        self.update()

    def zoomOut(self, factor = 1.1):
        self.zoom /= factor
        if self.zoom < 0.2:
            self.zoom = 0.2
        self.update()
    
    def findExtents(self):
        self.minX = 1000000000.0
        self.maxX = -1000000000.0
        self.minZ = 1000000000.0
        self.maxZ = -1000000000.0
        for p in self.lap1.points + self.lap2.points:
            if p.position_x < self.minX:
                self.minX = p.position_x
            if p.position_z < self.minZ:
                self.minZ = p.position_z
            if p.position_x > self.maxX:
                self.maxX = p.position_x
            if p.position_z > self.maxZ:
                self.maxZ = p.position_z
        self.midX = (self.maxX + self.minX)/2
        self.midZ = (self.maxZ + self.minZ)/2

        print ("Extents:", self.minX, self.minZ, self.maxX, self.maxZ, "->", self.midX, self.midZ)

    def speedDiffQColor(self, d):
        col = QColor()
        hue = d/(180) + 60/360
        if hue < 0:
            hue = 0
        if hue > 120/360:
            hue = 120/360
        col.setHsvF (hue, 1, 1)

        return col

    def indexToTime(self, i):
        minu = i // (60*60)
        sec = str(i // 60 - minu*60)
        if len(sec) < 2:
            sec = "0" * (2-len(sec)) + sec
        msec = str((i % 60) * 1/60)[2:5]
        if len(msec) < 3:
            msec += "0" * (3-len(msec))
        result = "{minu:1.0f}:{sec}:{msec}".format(minu = minu, sec = sec, msec = msec)
        return result

    # DATA ANALYSIS
    def findClosestPointNoLimit(self, lap, p):
        shortestDistance = 100000000
        result = None
        for p2 in lap:
            curDist = self.lap1.flatDistance(p, p2)
            if curDist < shortestDistance:
                shortestDistance = curDist
                result = p2

        return result

    def findNextBrake(self, lap, startI):
        j = startI
        for j in range(startI, len(lap)):
            if lap[j].brake <= 0.1:
                break
        for i in range(j, len(lap)):
            if lap[i].brake > 0.1:
                return i
        return None

    def findNextBrakeOff(self, lap, startI):
        j = startI
        found = False
        for j in range(startI, len(lap)):
            if lap[j].brake > 0.1:
                found = True
                break
        for i in range(j, len(lap)):
            if lap[i].brake <= 0.1 and found:
                return i
        return None

    def recentGearChange(self, lap, index):
        prevGear = lap[index].current_gear
        for i in range(index, max(0, index-10), -1):
            if lap[i].current_gear != prevGear:
                return True
        return False

    def futureGearChange(self, lap, index):
        prevGear = lap[index].current_gear
        for i in range(index, min(len(lap), index+10), 1):
            if lap[i].current_gear != prevGear:
                return True
        return False

    def findNextThrottle(self, lap, startI):
        #print("findNextThrottle", startI)
        j = startI
        for j in range(startI, len(lap)):
            if lap[j].throttle <= 0.9:
                break
        for i in range(j, len(lap)):
            if lap[i].throttle > 0.9:
                future = False #self.recentGearChange(lap, i)
                #if i > 4 and i < 8200:
                    #if future:
                        #print("X", i, "Throttle, ", future, lap[i].position_x, lap[i].position_z, "gear", lap[i-4].current_gear, lap[i-3].current_gear, lap[i-2].current_gear, lap[i-1].current_gear, lap[i].current_gear)
                    #else:
                        #print(i, "Throttle, ", future, lap[i].position_x, lap[i].position_z, "gear", lap[i-4].current_gear, lap[i-3].current_gear, lap[i-2].current_gear, lap[i-1].current_gear, lap[i].current_gear)
                if not future:
                    return i
                else:
                    return self.findNextThrottle(lap, i+1)
        return None

    def findNextThrottleOff(self, lap, startI):
        #print("        ", "findNextThrottleOff", startI)
        j = startI
        found = False
        for j in range(startI, len(lap)):
            if lap[j].throttle > 0.9:
                found = True
                break
        for i in range(j, len(lap)):
            if lap[i].throttle <= 0.9 and found:
                recent = False #self.recentGearChange(lap, i)
                #if i > 4 and i < 8200:
                    #if recent:
                        #print("        ", "X", i, "Throttle off, ", recent, lap[i].position_x, lap[i].position_z, "gear", lap[i-4].current_gear, lap[i-3].current_gear, lap[i-2].current_gear, lap[i-1].current_gear, lap[i].current_gear)
                    #else:
                        #print("        ", i, "Throttle off, ", recent, lap[i].position_x, lap[i].position_z, "gear", lap[i-4].current_gear, lap[i-3].current_gear, lap[i-2].current_gear, lap[i-1].current_gear, lap[i].current_gear)
                if not recent:
                    return i
                else:
                    return self.findNextThrottleOff(lap, i+1)
        return None

    def makeGraphic(self):
        # init
        self.layers = [[], [], [], [], []]
        lap1Layer = 0
        lap2Layer = 1
        lap1Markers = 2
        lap2Markers = 3
        textLayer = 4

        t1 = self.findNextThrottle(lap1.points, 0)
        t2 = self.findNextThrottle(lap2.points, 0)
        to1 = self.findNextThrottleOff(lap1.points, 0)
        to2 = self.findNextThrottleOff(lap2.points, 0)
        b1 = self.findNextBrake(lap1.points, 0)
        b2 = self.findNextBrake(lap2.points, 0)
        bo1 = self.findNextBrakeOff(lap1.points, 0)
        bo2 = self.findNextBrakeOff(lap2.points, 0)

        i1 = 0
        i2 = 0
        p1 = lap1.points[i1]
        p2 = lap2.points[i2]

        l1Color = 0x00ff7f7f
        l2Color = 0x0000ff00

        prevStep = False
        diffHistory = []

        prevDelta = 0
        prevGear1 = 0
        prevGear2 = 0

        # add finish line marker
        self.layers[lap1Markers].append(CircleMarker("finish", lap1.points[-1].position_x, lap1.points[-1].position_z, l1Color, 2))
        self.layers[textLayer].append(Text("finish", lap1.points[-1].position_x, lap1.points[-1].position_z, "FINISH:", 0, 20, 0x00ffffff, 2))
        self.layers[textLayer].append(Text("finish", lap1.points[-1].position_x, lap1.points[-1].position_z, self.indexToTime(len(lap1.points)), 0, 35, l1Color, 2))
        self.layers[textLayer].append(Text("finish", lap1.points[-1].position_x, lap1.points[-1].position_z, self.indexToTime(len(lap2.points)), 0, 50, l2Color, 2))
        if len(lap1.points) < len(lap2.points):
            signPre = "+"
        else:
            signPre = "-"
        self.layers[textLayer].append(Text("finish", lap1.points[-1].position_x, lap1.points[-1].position_z, signPre + self.indexToTime(abs(len(lap1.points)-len(lap2.points))) + " ± 0.017s", 0, 65, 0x00ffffff, 2))
        self.layers[lap2Markers].append(CircleMarker("finish", lap2.points[-1].position_x, lap2.points[-1].position_z, l2Color, 2))

        # handle all data points in the laps
        while i1 < len(lap1.points)-1 and i2 < len(lap2.points)-1:

            p1next = lap1.points[i1+1]
            p2next = lap2.points[i2+1]

            d1 = lap1.distance(p1next, p2)
            d2 = lap1.distance(p2next, p1)
            db = lap1.distance(p1next, p2next)
            dn = lap1.distance(p1, p2)
            if d1 < d2 and d1 < db: # Lap 2 is faster here
                i1+=1

                diffHistory.append(1)
                if len(diffHistory) > 180:
                    diffHistory.pop(0)
                ad = mean(diffHistory)
                
                if not prevStep:
                    self.layers[lap1Markers].append(Triangle("time", p1.position_x, p1.position_z, p2.position_x, p2.position_z, p1next.position_x, p1next.position_z, l2Color))
                    dpre = ""
                    if int(p2.car_speed - p1.car_speed) > 0:
                        dpre = "+"
                    self.layers[lap2Markers].append(LeftLineMarker("time", p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, self.speedDiffQColor(6*30*ad), 4, endText = str(int(p1.car_speed)) + "km/h\n" + str(int(p2.car_speed)) + "km/h\n" + dpre + str(int(p2.car_speed - p1.car_speed)) + " km/h"))
                    prevStep = True
            elif d2 < d1 and d2 < db: # Lap 1 is faster here
                i2+=1

                diffHistory.append(-1)
                if len(diffHistory) > 180:
                    diffHistory.pop(0)

                ad = mean(diffHistory)
                if not prevStep:
                    self.layers[lap1Markers].append(Triangle("time", p1.position_x, p1.position_z, p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, l1Color))
                    dpre = ""
                    if int(p2.car_speed - p1.car_speed) > 0:
                        dpre = "+"
                    self.layers[lap2Markers].append(LeftLineMarker("time", p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, self.speedDiffQColor(6*30*ad), 4, endText = str(int(p1.car_speed)) + "km/h\n" + str(int(p2.car_speed)) + "km/h\n" + dpre + str(int(p2.car_speed-p1.car_speed)) + " km/h"))
                    prevStep = True
            else: # No time difference
                i1+=1
                i2+=1

                diffHistory.append(0)
                if len(diffHistory) > 180:
                    diffHistory.pop(0)
                prevStep = False
            
            # Mark gear changes
            if prevGear1 != p1.current_gear:
                print("Gear change 1:", i1, prevGear1, "->", p1.current_gear)
                if prevGear1 > p1.current_gear:
                    self.layers[lap1Markers].append(DownMarker("gear", p1.position_x, p1.position_z, l1Color, 4))
                else:
                    self.layers[lap1Markers].append(UpMarker("gear", p1.position_x, p1.position_z, l1Color, 4))
                prevGear1 = p1.current_gear

            if prevGear2 != p2.current_gear:
                print("Gear change 2:", i2, prevGear2, "->", p2.current_gear)
                if prevGear2 > p2.current_gear:
                    self.layers[lap2Markers].append(DownMarker("gear", p2.position_x, p2.position_z, l2Color, 4))
                else:
                    self.layers[lap2Markers].append(UpMarker("gear", p2.position_x, p2.position_z, l2Color, 4))
                prevGear2 = p2.current_gear
                
            # Mark brake points
            if b1 == i1:
                self.layers[lap1Markers].append(CrossMarker("brake", p1next.position_x, p1next.position_z, l1Color, 4))
                self.layers[textLayer].append(Text("time", p1next.position_x, p1next.position_z, self.indexToTime(i1) + " ± 0.017s", 0, 20, l1Color, 2))
                self.layers[textLayer].append(Text("time", p1next.position_x, p1next.position_z, self.indexToTime(i2) + " ± 0.017s", 0, 35, l2Color, 2))
                if i1 <= i2:
                    signPre = "+"
                else:
                    signPre = "-"
                change = prevDelta - (i1 - i2)
                if change < 0:
                    cSignPre = "-"
                else:
                    cSignPre = "+"
                self.layers[textLayer].append(Text("time", p1next.position_x, p1next.position_z, signPre + self.indexToTime(abs(i1-i2)) + " (" + cSignPre + self.indexToTime(abs(change)) + ")", 0, 50, 0x00ffffff, 2))
                prevDelta = i1-i2
                b1 = self.findNextBrake(lap1.points, b1+1)
            if bo1 == i1:
                self.layers[lap1Markers].append(SquareMarker("brake", p1next.position_x, p1next.position_z, l1Color, 4))
                bo1 = self.findNextBrakeOff(lap1.points, bo1+1)
            if b2 == i2:
                self.layers[lap2Markers].append(CrossMarker("brake", p2next.position_x, p2next.position_z, l2Color, 4))
                self.layers[textLayer].append(Text("time", p2next.position_x, p2next.position_z, self.indexToTime(i2) + " ± 0.017s", 0, -20, l2Color, 2))
                self.layers[textLayer].append(Text("time", p2next.position_x, p2next.position_z, self.indexToTime(i1) + " ± 0.017s", 0, -35, l1Color, 2))
                if i1 <= i2:
                    signPre = "+"
                else:
                    signPre = "-"
                change = prevDelta - (i1 - i2)
                if change < 0:
                    cSignPre = "-"
                else:
                    cSignPre = "+"
                self.layers[textLayer].append(Text("time", p2next.position_x, p2next.position_z, signPre + self.indexToTime(abs(i1-i2)) + " (" + cSignPre + self.indexToTime(abs(change)) + ")", 0, -50, 0x00ffffff, 2))
                prevDelta = i1-i2
                b2 = self.findNextBrake(lap2.points, b2+1)
            if bo2 == i2:
                self.layers[lap2Markers].append(SquareMarker("brake", p2next.position_x, p2next.position_z, l2Color, 4))
                bo2 = self.findNextBrakeOff(lap2.points, bo2+1)


            # Mark throttle points
            if t1 == i1:
                #self.layers[lap1Markers].append(LeftLineMarker(p1next.position_x, p1next.position_z, p1.position_x, p1.position_z, l1Color, 4))
                self.layers[lap1Markers].append(PlusMarker("throttle", p1next.position_x, p1next.position_z, l1Color, 4))
                t1 = self.findNextThrottle(lap1.points, t1+1)
            if to1 == i1:
                #self.layers[lap1Markers].append(LeftLineMarker(p1.position_x, p1.position_z, p1next.position_x, p1next.position_z, 0x00ffffff, 4))
                self.layers[lap1Markers].append(CircleMarker("throttle", p1next.position_x, p1next.position_z, l1Color, 4))
                to1 = self.findNextThrottleOff(lap1.points, to1+1)
            
            if t2 == i2:
                #self.layers[lap2Markers].append(LeftLineMarker(p2next.position_x, p2next.position_z, p2.position_x, p2.position_z, l2Color, 4))
                self.layers[lap2Markers].append(PlusMarker("throttle", p2next.position_x, p2next.position_z, l2Color, 4))
                t2 = self.findNextThrottle(lap2.points, t2+1)
            if to2 == i2:
                #self.layers[lap2Markers].append(LeftLineMarker(p2next.position_x, p2next.position_z, p2.position_x, p2.position_z, 0x00ffffff, 4))
                self.layers[lap2Markers].append(CircleMarker("throttle", p2next.position_x, p2next.position_z, l2Color, 4))
                to2 = self.findNextThrottleOff(lap2.points, to2+1)

            # Draw laps
            self.layers[lap1Layer].append(Line("line", p1.position_x, p1.position_z, p1next.position_x, p1next.position_z, l1Color, 4))
            self.layers[lap2Layer].append(Line("line", p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, l2Color, 4))
            
            # Go to next points
            p1 = lap1.points[i1]
            p2 = lap2.points[i2]

    # RENDERING
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)

        for ly in range(len(self.layers)):
            if self.showLayers[ly]:
                for l in self.layers[ly]:
                    qp.setBrush(Qt.BrushStyle.NoBrush)
                    if l.group in self.showGroups and not self.showGroups[l.group]:
                        pass
                    elif isinstance(l, CrossMarker):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        qp.drawLine(int(x1+10), int(z1+10), int(x1-10), int(z1-10))
                        qp.drawLine(int(x1-10), int(z1+10), int(x1+10), int(z1-10))
                    elif isinstance(l, PlusMarker):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        qp.drawLine(int(x1), int(z1+10), int(x1), int(z1-10))
                        qp.drawLine(int(x1-10), int(z1), int(x1+10), int(z1))
                    elif isinstance(l, CircleMarker):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        qp.drawEllipse(int(x1-10), int(z1-10), 20, 20)
                    elif isinstance(l, SquareMarker):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        qp.drawLine(int(x1+10), int(z1+10), int(x1+10), int(z1-10))
                        qp.drawLine(int(x1-10), int(z1+10), int(x1-10), int(z1-10))
                        qp.drawLine(int(x1+10), int(z1-10), int(x1-10), int(z1-10))
                        qp.drawLine(int(x1+10), int(z1+10), int(x1-10), int(z1+10))
                    elif isinstance(l, Line):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        x2 = self.width() / 2 - self.zoom * -((l.x2 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z2 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z2 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        qp.drawLine(int(x1), int(z1), int(x2), int(z2))
                    elif isinstance(l, DownMarker):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        qp.setBrush(Qt.BrushStyle.NoBrush)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        path = QPainterPath()
                        path.moveTo(int(x1+10), int(z1-10))
                        path.lineTo(int(x1), int(z1+10))
                        path.lineTo(int(x1-10), int(z1-10))
                        path.lineTo(int(x1+10), int(z1-10))
                        qp.drawPath(path)
                    elif isinstance(l, UpMarker):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        qp.setBrush(Qt.BrushStyle.NoBrush)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        path = QPainterPath()
                        path.moveTo(int(x1+10), int(z1+10))
                        path.lineTo(int(x1), int(z1-10))
                        path.lineTo(int(x1-10), int(z1+10))
                        path.lineTo(int(x1+10), int(z1+10))

                        qp.drawPath(path)
                    elif isinstance(l, Triangle):
                        qp.setPen(l.color)
                        qp.setBrush(l.color)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        x2 = self.width() / 2 - self.zoom * -((l.x2 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z2 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z2 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        x3 = self.width() / 2 - self.zoom * -((l.x3 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z3 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z3 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        path = QPainterPath()
                        path.moveTo(int(x1), int(z1))
                        path.lineTo(int(x2), int(z2))
                        path.lineTo(int(x3), int(z3))
                        path.lineTo(int(x1), int(z1))

                        qp.drawPath(path)

                    elif isinstance(l, LeftLineMarker):
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        x2 = self.width() / 2 - self.zoom * -((l.x2 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z2 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z2 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        dx = x2 - x1
                        dz = z2 - z1
                        le = math.sqrt(dx**2 + dz**2)
                        dx /= le/30
                        dz /= le/30
                        qp.drawLine(int(x1), int(z1), int(x1+dz), int(z1-dx))
                        if not l.endText is None and self.showText:
                            lines = l.endText.split("\n")
                            numLines = len(lines)
                            offsetH = 15
                            for curLine in range(numLines):
                                fm = qp.fontMetrics()
                                br = fm.boundingRect(lines[curLine])
                                px = int(x1 + 1.5*dz - br.width() / 2)
                                py = int(z1 - (1+ 0.5 * numLines)*dx + br.height() / 2 + curLine * offsetH - (numLines-1) * offsetH / 2)
                                qp.drawText(px, py, lines[curLine])

                    elif isinstance(l, Text) and self.showText:
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        qp.drawText(int(x1 + l.offsetx), int(z1 + l.offsetz), l.text)

        qp.end()

    # EVENTS
    def mousePressEvent(self, e):
        if e.button () == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.dragX = e.position().x()
            self.dragY = e.position().y()
        elif e.button () == Qt.MouseButton.RightButton:
            mx = e.position().x()
            mz = e.position().y()
            wx = (mx - self.width () / 2) / self.zoom * ((self.maxX - self.minX)/self.width()) + self.midX - self.offsetX
            wz = (mz - self.height () / 2) / self.zoom/self.aspectRatio * ((self.maxZ - self.minZ)/self.height()) + self.midZ - self.offsetZ
            mp = PositionPoint()
            mp.position_x = wx
            mp.position_z = wz
            
            lp2 = self.findClosestPointNoLimit (self.lap2.points, mp)
            self.layers[3].append(CircleMarker("Mouse", lp2.position_x, lp2.position_z, 0x00ffffff, 2))
            self.layers[3].append(Text("Mouse", lp2.position_x, lp2.position_z, str(int(lp2.car_speed)) + " km/h, gear " + str(lp2.current_gear) + ", " + str (lp2.rpm) + " rpm, throttle " + str(int(lp2.throttle)) + "%", 20, 0, 0x0000ff00, 2))

            lp1 = self.findClosestPointNoLimit (self.lap1.points, lp2)
            self.layers[2].append(CircleMarker("Mouse", lp1.position_x, lp1.position_z, 0x00ffffff, 2))
            self.layers[2].append(Text("Mouse", lp2.position_x, lp2.position_z, str(int(lp1.car_speed)) + " km/h, gear " + str(lp1.current_gear) + ", " + str (lp1.rpm) + " rpm, throttle " + str(int(lp1.throttle)) + "%", 20, 15, 0x00ff7f7f, 2))
            self.update()
            

    def mouseReleaseEvent(self, e):
        if e.button () == Qt.MouseButton.LeftButton:
            self.dragging = False

    def mouseMoveEvent(self, e):
        if self.dragging:
            mx = e.position().x()
            mz = e.position().y()
            wx = (mx - self.width () / 2) / self.zoom * ((self.maxX - self.minX)/self.width()) + self.midX - self.offsetX
            wz = (mz - self.height () / 2) / self.zoom/self.aspectRatio * ((self.maxZ - self.minZ)/self.height()) + self.midZ - self.offsetZ
            wxp = (self.dragX - self.width () / 2) / self.zoom * ((self.maxX - self.minX)/self.width()) + self.midX - self.offsetX
            wzp = (self.dragY - self.height () / 2) / self.zoom/self.aspectRatio * ((self.maxZ - self.minZ)/self.height()) + self.midZ - self.offsetZ
            self.dragX = mx
            self.dragY = mz
            self.offsetX += wx - wxp
            self.offsetZ += wz - wzp
            self.update()

    def resizeEvent(self, e):
        self.aspectRatio = e.size().width() / e.size().height()

    def wheelEvent(self, e):
        dx = e.position().x()
        dz = e.position().y()
        wx = (dx - self.width () / 2) / self.zoom * ((self.maxX - self.minX)/self.width()) + self.midX - self.offsetX
        wz = (dz - self.height () / 2) / self.zoom/self.aspectRatio * ((self.maxZ - self.minZ)/self.height()) + self.midZ - self.offsetZ
        rx = wx - self.midX + self.offsetX
        rz = wz - self.midZ + self.offsetZ
        d = e.angleDelta().y()
        if d > 0:
            for i in range(d):
                self.zoomIn(1.01)
                self.offsetX -= rx * 1.01 - rx
                self.offsetZ -= rz * 1.01 - rz
        else:
            for i in range(-d):
                self.zoomOut(1.01)
                self.offsetX -= rx / 1.01 - rx
                self.offsetZ -= rz / 1.01 - rz

    def delegateKeyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Right.value:
            self.moveRight()
        elif e.key() == Qt.Key.Key_Left.value:
            self.moveLeft()
        elif e.key() == Qt.Key.Key_Up.value:
            self.moveUp()
        elif e.key() == Qt.Key.Key_Down.value:
            self.moveDown()
        elif e.key() == Qt.Key.Key_Q.value:
            self.zoomIn()
        elif e.key() == Qt.Key.Key_A.value:
            self.zoomOut()
        
        elif e.key() == Qt.Key.Key_T.value:
            if not 'time' in self.showGroups:
                self.showGroups['time'] = True
            self.showGroups['time'] = not self.showGroups['time']
            self.update()
        elif e.key() == Qt.Key.Key_B.value:
            if not 'brake' in self.showGroups:
                self.showGroups['brake'] = True
            self.showGroups['brake'] = not self.showGroups['brake']
            self.update()
        elif e.key() == Qt.Key.Key_G.value:
            if not 'throttle' in self.showGroups:
                self.showGroups['throttle'] = True
            self.showGroups['throttle'] = not self.showGroups['throttle']
            self.update()

        elif e.key() == Qt.Key.Key_1.value:
            self.showLayers[0] = not self.showLayers[0]
            self.update()
        elif e.key() == Qt.Key.Key_2.value:
            self.showLayers[1] = not self.showLayers[1]
            self.update()
        elif e.key() == Qt.Key.Key_3.value:
            self.showLayers[2] = not self.showLayers[2]
            self.update()
        elif e.key() == Qt.Key.Key_4.value:
            self.showLayers[3] = not self.showLayers[3]
            self.update()
        elif e.key() == Qt.Key.Key_5.value:
            self.showLayers[4] = not self.showLayers[4]
            self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.masterWidget = MapView2()

        self.setWindowTitle("GT7 Visual Lap Comparison")

        self.setCentralWidget(self.masterWidget)

    def keyPressEvent(self, e):
        self.masterWidget.delegateKeyPressEvent(e)



def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("=== EXCEPTION ===")
    print("error message:\n", tb)
    with open ("gt7visualcomp.log", "a") as f:
        f.write("=== EXCEPTION ===\n")
        f.write(str(datetime.datetime.now ()) + "\n\n")
        f.write(str(tb) + "\n")
    QApplication.quit()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setOrganizationName("pitstop.profittlich.com");
    app.setOrganizationDomain("pitstop.profittlich.com");
    app.setApplicationName("GT7 Visual Lap Comparison");

    window = MainWindow()

    lap1 = loadLap(sys.argv[1])
    lap2 = loadLap(sys.argv[2])

    window.masterWidget.setLaps(lap1, lap2)
    
    window.show()

    sys.excepthook = excepthook
    app.exec()



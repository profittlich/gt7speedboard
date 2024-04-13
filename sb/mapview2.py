import math
from statistics import mean
import json
import datetime
from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QSettings, QEvent
from PyQt6.QtGui import QColor, QRegularExpressionValidator, QPixmap, QPainter, QPalette, QPen, QLinearGradient, QGradient, QPainterPath, QStaticText, QTextOption
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox
from sb.gt7widgets import *
from sb.drawelements import *
from sb.helpers import loadLap, loadLaps, indexToTime
from sb.helpers import Lap, PositionPoint

class MapView2(QWidget):

    def __init__(self, lap1 = None, lap2 = None):
        super().__init__()
        self.lap1 = lap1
        self.lap2 = lap2
        self.zoom = 1/1.1
        self.offsetX = 0
        self.offsetZ = 0
        self.showText = True
        self.showLayers = [ True, ] * 7
        self.layerInfo = ""
        self.typeInfo = ""
        self.showGroups = {}
        self.dragging = False
        self.temporaryMarkers = []
        self.manualSplitPoints = []


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

    # DATA ANALYSIS
    def findClosestPointNoLimit(self, lap, p):
        shortestDistance = 100000000
        result = None
        for p2 in range(len(lap)):
            curDist = self.lap1.flatDistance(p, lap[p2])
            if curDist < shortestDistance:
                shortestDistance = curDist
                result = (lap[p2], p2)

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
            if lap[j].throttle <= 90:
                break
        for i in range(j, len(lap)):
            if lap[i].throttle > 90:
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
            if lap[j].throttle > 90:
                found = True
                break
        for i in range(j, len(lap)):
            if lap[i].throttle <= 90 and found:
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
        self.layers = [[], [], [], [], [], [], []]
        self.lap1Layer = 2
        self.lap2Layer = 3
        self.lap1BottomMarkers = 0
        self.lap2BottomMarkers = 1
        self.lap1Markers = 4
        self.lap2Markers = 5
        self.textLayer = 6

        #t1 = self.findNextThrottle(self.lap1.points, 0)
        #t2 = self.findNextThrottle(self.lap2.points, 0)
        #to1 = self.findNextThrottleOff(self.lap1.points, 0)
        #to2 = self.findNextThrottleOff(self.lap2.points, 0)
        b1 = self.findNextBrake(self.lap1.points, 0)
        b2 = self.findNextBrake(self.lap2.points, 0)
        bo1 = self.findNextBrakeOff(self.lap1.points, 0)
        bo2 = self.findNextBrakeOff(self.lap2.points, 0)

        i1 = 0
        i2 = 0
        p1 = self.lap1.points[i1]
        p2 = self.lap2.points[i2]

        #l1Color = 0x00ff7f7f
        #l2Color = 0x0000ff00
        #l1ColorDark = 0x00af5f4f
        #l2ColorDark = 0x0000af00
        #l1ColorBright = 0x00ffafaf
        #l2ColorBright = 0x00afffaf

        self.l1Color = 0x00ee82ee
        self.l2Color = 0x0000ffff
        self.l1ColorDark = 0x007f427f
        self.l2ColorDark = 0x0000afaf
        self.l1ColorBright = 0x00ffafff
        self.l2ColorBright = 0x00afffff

        prevStep = False
        diffHistory = []

        prevDelta = 0
        prevGear1 = 0
        prevGear2 = 0

        # add finish line marker
        #self.layers[self.lap1Markers].append(CircleMarker("finish", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, self.l1ColorBright, 2))
        self.layers[self.lap1Markers].append(LeftLineMarker("finish", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, self.lap1.points[-2].position_x, self.lap1.points[-2].position_z, 0x00ffffff, 2))
        self.layers[self.textLayer].append(Text("finish", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, "FINISH:", 10, 20, 0x00ffffff, 2))
        self.layers[self.textLayer].append(Text("finish", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, indexToTime(len(self.lap1.points)) + " (est.)", 10, 35, self.l1Color, 2))
        self.layers[self.textLayer].append(Text("finish", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, indexToTime(len(self.lap2.points)) + " (est.)", 10, 50, self.l2Color, 2))
        if len(self.lap1.points) < len(self.lap2.points):
            signPre = "+"
        else:
            signPre = "-"
        self.layers[self.textLayer].append(Text("finish", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, signPre + indexToTime(abs(len(self.lap1.points)-len(self.lap2.points))), 10, 65, 0x00ffffff, 2))
        #self.layers[self.lap2Markers].append(CircleMarker("finish", self.lap2.points[-1].position_x, self.lap2.points[-1].position_z, self.l2ColorBright, 2))
        self.layers[self.lap2Markers].append(LeftLineMarker("finish", self.lap2.points[-1].position_x, self.lap2.points[-1].position_z, self.lap2.points[-2].position_x, self.lap2.points[-2].position_z, 0x00ffffff, 2))

        l1Alt = False
        l2Alt = False
        # handle all data points in the laps
        while i1 < len(self.lap1.points)-1 or i2 < len(self.lap2.points)-1:

            if i1 < len(self.lap1.points)-1:
                p1next = self.lap1.points[i1+1]
            if i2 < len(self.lap2.points)-1:
                p2next = self.lap2.points[i2+1]

            d1 = self.lap1.distance(p1next, p2)
            d2 = self.lap1.distance(p2next, p1)
            db = self.lap1.distance(p1next, p2next)
            dn = self.lap1.distance(p1, p2)
            i1Incremented = False
            i2Incremented = False
            if d1 < d2 and d1 < db and i1 < len(self.lap1.points)-1: # Lap 2 is faster here
                i1+=1
                i1Incremented = True

                diffHistory.append(1)
                if len(diffHistory) > 180:
                    diffHistory.pop(0)
                ad = mean(diffHistory)
                
                if not prevStep:
                    self.layers[self.lap1BottomMarkers].append(Triangle("time", p1.position_x, p1.position_z, p2.position_x, p2.position_z, p1next.position_x, p1next.position_z, self.l2ColorDark))
                    dpre = ""
                    if int(p2.car_speed - p1.car_speed) > 0:
                        dpre = "+"
                    self.layers[self.lap2BottomMarkers].append(LeftLineMarker("time", p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, self.speedDiffQColor(6*30*ad), 4, endText = str(int(p2.car_speed)) + "km/h\n" + dpre + str(int(p2.car_speed - p1.car_speed)) + " km/h"))
                    prevStep = True
            elif d2 < d1 and d2 < db and i2 < len(self.lap2.points)-1: # Lap 1 is faster here
                i2+=1
                i2Incremented = True

                diffHistory.append(-1)
                if len(diffHistory) > 180:
                    diffHistory.pop(0)

                ad = mean(diffHistory)
                if not prevStep:
                    self.layers[self.lap1BottomMarkers].append(Triangle("time", p1.position_x, p1.position_z, p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, self.l1ColorDark))
                    dpre = ""
                    if int(p2.car_speed - p1.car_speed) > 0:
                        dpre = "+"
                    self.layers[self.lap2BottomMarkers].append(LeftLineMarker("time", p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, self.speedDiffQColor(6*30*ad), 4, endText = str(int(p2.car_speed)) + "km/h\n" + dpre + str(int(p2.car_speed-p1.car_speed)) + " km/h"))
                    prevStep = True
            else: # No time difference
                if i1 < len(self.lap1.points)-1:
                    i1+=1
                    i1Incremented = True
                if i2 < len(self.lap2.points)-1:
                    i2+=1
                    i2Incremented = True

                diffHistory.append(0)
                if len(diffHistory) > 180:
                    diffHistory.pop(0)
                prevStep = False
            
            # Mark gear changes
            if prevGear1 != p1.current_gear:
                if prevGear1 > p1.current_gear:
                    self.layers[self.lap1Markers].append(DownMarker("gear", p1.position_x, p1.position_z, self.l1ColorBright, text=str(p1.current_gear)))
                else:
                    self.layers[self.lap1Markers].append(UpMarker("gear", p1.position_x, p1.position_z, self.l1ColorBright, text=str(p1.current_gear)))
                prevGear1 = p1.current_gear

            if prevGear2 != p2.current_gear:
                if prevGear2 > p2.current_gear:
                    self.layers[self.lap2Markers].append(DownMarker("gear", p2.position_x, p2.position_z, self.l2ColorBright, text=str(p2.current_gear)))
                else:
                    self.layers[self.lap2Markers].append(UpMarker("gear", p2.position_x, p2.position_z, self.l2ColorBright, text=str(p2.current_gear)))
                prevGear2 = p2.current_gear
                
            # Mark brake points
            if b1 == i1:
                self.layers[self.lap1Markers].append(CrossMarker("brake", p1next.position_x, p1next.position_z, self.l1ColorBright))
                self.layers[self.textLayer].append(Text("brake", p1next.position_x, p1next.position_z, indexToTime(i1) + " (est.)", 0, 20, self.l1Color, 2))
                self.layers[self.textLayer].append(Text("brake", p1next.position_x, p1next.position_z, indexToTime(i2) + " (est.)", 0, 35, self.l2Color, 2))
                if i1 <= i2:
                    signPre = "+"
                else:
                    signPre = "-"
                change = prevDelta - (i1 - i2)
                if change < 0:
                    cSignPre = "-"
                else:
                    cSignPre = "+"
                self.layers[self.textLayer].append(Text("brake", p1next.position_x, p1next.position_z, signPre + indexToTime(abs(i1-i2)) + " (" + cSignPre + indexToTime(abs(change)) + ")", 0, 50, 0x00ffffff, 2))
                prevDelta = i1-i2
                b1 = self.findNextBrake(self.lap1.points, b1+1)
            if bo1 == i1:
                self.layers[self.lap1Markers].append(SquareMarker("brake", p1next.position_x, p1next.position_z, self.l1ColorBright))
                bo1 = self.findNextBrakeOff(self.lap1.points, bo1+1)
            if b2 == i2:
                self.layers[self.lap2Markers].append(CrossMarker("brake", p2next.position_x, p2next.position_z, self.l2ColorBright))
                self.layers[self.textLayer].append(Text("brake", p2next.position_x, p2next.position_z, indexToTime(i2) + " (est.)", 0, -20, self.l2Color, 2))
                self.layers[self.textLayer].append(Text("brake", p2next.position_x, p2next.position_z, indexToTime(i1) + " (est.)", 0, -35, self.l1Color, 2))
                if i1 <= i2:
                    signPre = "+"
                else:
                    signPre = "-"
                change = prevDelta - (i1 - i2)
                if change < 0:
                    cSignPre = "-"
                else:
                    cSignPre = "+"
                self.layers[self.textLayer].append(Text("brake", p2next.position_x, p2next.position_z, signPre + indexToTime(abs(i1-i2)) + " (" + cSignPre + indexToTime(abs(change)) + ")", 0, -50, 0x00ffffff, 2))
                prevDelta = i1-i2
                b2 = self.findNextBrake(self.lap2.points, b2+1)
            if bo2 == i2:
                self.layers[self.lap2Markers].append(SquareMarker("brake", p2next.position_x, p2next.position_z, self.l2ColorBright))
                bo2 = self.findNextBrakeOff(self.lap2.points, bo2+1)

            #if i1 == len(self.lap1.points)-1:
                #change = prevDelta - (i1 - i2)
                #if change < 0:
                    #cSignPre = "-"
                #else:
                    #cSignPre = "+"
                #prevDelta = i1-i2
                #self.layers[self.textLayer].append(Text("brake", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, "(" + cSignPre + indexToTime(abs(change)) + ")", 10, 80, 0x00ffffff, 2))

            if i2 == len(self.lap2.points)-1:
                change = prevDelta - (i1 - i2)
                if change < 0:
                    cSignPre = "-"
                else:
                    cSignPre = "+"
                prevDelta = i1-i2
                self.layers[self.textLayer].append(Text("brake", self.lap1.points[-1].position_x, self.lap1.points[-1].position_z, "(" + cSignPre + indexToTime(abs(change)) + ")", 10, 80, 0x00ffffff, 2))


            # Mark throttle points
            if not prevStep and i1 % 60 == 0 or abs(p1.throttle-p1next.throttle) > 0.9:
                self.layers[self.lap1BottomMarkers].append(LeftLineMarker("throttle", p1next.position_x, p1next.position_z, p1.position_x, p1.position_z, self.l1ColorDark, 2, length = p1next.throttle))
            if not prevStep and i2 % 60 == 0 or abs(p2.throttle-p2next.throttle) > 0.9:
                self.layers[self.lap2BottomMarkers].append(LeftLineMarker("throttle", p2next.position_x, p2next.position_z, p2.position_x, p2.position_z, self.l2ColorDark, 2, length = p2next.throttle))

            # Draw laps
            if i1Incremented:
                if l1Alt:
                    l1col = self.l1ColorDark
                else:
                    l1col = self.l1Color
                l1Alt = not l1Alt
                self.layers[self.lap1Layer].append(Line("line", p1.position_x, p1.position_z, p1next.position_x, p1next.position_z, l1col))
            if i2Incremented:
                if l2Alt:
                    l2col = self.l2ColorDark
                else:
                    l2col = self.l2Color
                l2Alt = not l2Alt
                self.layers[self.lap2Layer].append(Line("line", p2.position_x, p2.position_z, p2next.position_x, p2next.position_z, l2col))
            
            # Go to next points
            p1 = self.lap1.points[i1]
            p2 = self.lap2.points[i2]

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
                        qp.drawLine(int(x1+ l.length), int(z1+ l.length), int(x1- l.length), int(z1- l.length))
                        qp.drawLine(int(x1- l.length), int(z1+ l.length), int(x1+ l.length), int(z1- l.length))
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
                        if (le > 0):
                            dx *= l.length/le/3
                            dz *= l.length/le/3
                            qp.drawLine(int(x1), int(z1), int(x1+dz), int(z1-dx))

        for ly in range(len(self.layers)):
            if self.showLayers[ly]:
                for l in self.layers[ly]:
                    qp.setBrush(Qt.BrushStyle.NoBrush)
                    if l.group in self.showGroups and not self.showGroups[l.group]:
                        pass
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
                        if (le > 0):
                            dx *= l.length/le/3
                            dz *= l.length/le/3
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
                    elif isinstance(l, UpMarker) and self.showText:
                        if not l.text is None:
                            pen = QPen(l.color)
                            qp.setPen(pen)
                            fm = qp.fontMetrics()
                            br = fm.boundingRect(l.text)
                            x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                            z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                            qp.drawText(int(x1-br.width()/2), int(z1+25), l.text)
                    elif isinstance(l, DownMarker) and self.showText:
                        if not l.text is None:
                            pen = QPen(l.color)
                            qp.setPen(pen)
                            fm = qp.fontMetrics()
                            br = fm.boundingRect(l.text)
                            x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                            z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                            qp.drawText(int(x1-br.width()/2), int(z1-20), l.text)
                    elif isinstance(l, Text) and self.showText:
                        fm = qp.fontMetrics()
                        br = fm.boundingRect(l.text)
                        x1 = self.width() / 2 - self.zoom * -((l.x1 + self.offsetX) - self.midX)/((self.maxX - self.minX)/self.width())
                        z1 = self.height() / 2 - self.zoom*self.aspectRatio * -((l.z1 + self.offsetZ) - self.midZ)/((self.maxZ - self.minZ)/self.height())
                        qp.setBrush(QColor(0, 0, 0, 127))
                        qp.setPen(Qt.PenStyle.NoPen)
                        qp.drawRect(int(x1 + br.left() + l.offsetx), int(z1 + br.top() + l.offsetz), int(br.width()), int(br.height()))
                        pen = QPen(l.color)
                        pen.setWidth(l.bold)
                        qp.setPen(pen)
                        qp.drawText(int(x1 + l.offsetx), int(z1 + l.offsetz), l.text)

        layerInfo = ""
        for b in range(len(self.showLayers)):
            if self.showLayers[b]:
                layerInfo += "<b>[" + str(b+1) + "]</b> "
            else:
                layerInfo += "<span style='color:gray'>[" + str(b+1) + "]</span> "

        qp.setBrush(QColor(0, 0, 0, 127))
        qp.setPen(Qt.PenStyle.NoPen)
        qp.drawRect(0, 0, self.width(), 40)

        qp.setPen(0x00ffffff)
        qp.setBrush(Qt.BrushStyle.NoBrush)

        if not layerInfo == self.layerInfo:
            self.layerInfoTxt = QStaticText(layerInfo)
            #self.layerInfoTxt.setTextWidth(500)
            to = self.layerInfoTxt.textOption()
            to.setWrapMode(QTextOption.WrapMode.NoWrap)
            self.layerInfoTxt.setTextOption(to)
            self.layerInfoTxt.prepare()
            self.layerInfo = layerInfo

        qp.drawStaticText(10, 10, self.layerInfoTxt)

        typeInfo = ""
        if self.showText:
            typeInfo += "<b>[T] text</b> | "
        else:
            typeInfo += "<span style='color:gray'>[T] text</span> | "

        if 'time' in self.showGroups and not self.showGroups['time']:
            typeInfo += "<span style='color:gray'>[S] speed/time</span> | "
        else:
            typeInfo += "<b>[S] speed/time</b> | "

        if 'throttle' in self.showGroups and not self.showGroups['throttle']:
            typeInfo += "<span style='color:gray'>[A] throttle </span> | "
        else:
            typeInfo += "<b>[A] throttle</b> | "

        if 'brake' in self.showGroups and not self.showGroups['brake']:
            typeInfo += "<span style='color:gray'>[B] brakes</span> | "
        else:
            typeInfo += "<b>[B] brakes</b> | "

        if 'gear' in self.showGroups and not self.showGroups['gear']:
            typeInfo += "<span style='color:gray'>[G] gearsr</span> | "
        else:
            typeInfo += "<b>[G] gears</b> | "

        if 'finish' in self.showGroups and not self.showGroups['finish']:
            typeInfo += "<span style='color:gray'>[F] finish line</span>"
        else:
            typeInfo += "<b>[F] finish line</b>"

        if not typeInfo == self.typeInfo:
            self.typeInfoTxt = QStaticText(typeInfo)
            to = self.typeInfoTxt.textOption()
            to.setWrapMode(QTextOption.WrapMode.NoWrap)
            self.typeInfoTxt.setTextOption(to)
            self.typeInfoTxt.prepare()
            self.typeInfo = typeInfo

        qp.drawStaticText(int(self.width() - 10 - self.typeInfoTxt.size().width()), 10, self.typeInfoTxt)
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
            
            lp2, ip2 = self.findClosestPointNoLimit (self.lap2.points, mp)
            mk1 = CircleMarker("Mouse", lp2.position_x, lp2.position_z, 0x00ffffff, 2)
            mk2 = Text("Mouse", lp2.position_x, lp2.position_z, str(ip2) + ": " + str(int(lp2.car_speed)) + " km/h, gear " + str(lp2.current_gear) + ", " + str (lp2.rpm) + " rpm, throttle " + str(int(lp2.throttle)) + "% lap " + str(lp2.current_lap), 20, 0, self.l2Color, 2)
            self.layers[self.lap2Markers].append(mk1)
            self.layers[self.lap2Markers].append(mk2)
            self.temporaryMarkers.append(mk1)
            self.temporaryMarkers.append(mk2)

            lp1, ip1 = self.findClosestPointNoLimit (self.lap1.points, lp2)
            mk3 = CircleMarker("Mouse", lp1.position_x, lp1.position_z, 0x00ffffff, 2)
            mk4 = Text("Mouse", lp2.position_x, lp2.position_z, str(ip1) + ": " + str(int(lp1.car_speed)) + " km/h, gear " + str(lp1.current_gear) + ", " + str (lp1.rpm) + " rpm, throttle " + str(int(lp1.throttle)) + "% lap " + str(lp2.current_lap), 20, 15, self.l1Color, 2)
            mk5 = Text("Mouse", lp1.position_x, lp1.position_z, "Distance: " + str(self.lap2.distance(lp1, lp2)) ,20, 15, self.l1Color, 2)
            self.layers[self.lap1Markers].append(mk3)
            self.layers[self.lap1Markers].append(mk4)
            self.layers[self.lap2Markers].append(mk5)
            self.temporaryMarkers.append(mk3)
            self.temporaryMarkers.append(mk4)

            self.manualSplitPoints.append((self.lap1.points.index(lp1), self.lap2.points.index(lp2)))

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
        trackAspect = (self.maxZ- self.minZ)/(self.maxX-self.minX)
        self.aspectRatio = trackAspect * e.size().width() / e.size().height()
        print("Width:", self.width(), "Height:", self.height())
        print("New aspect ratio:", self.aspectRatio)

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
    
    def writeFlippingLaps(self):
        fromPts = (0, 0)
        optLap = Lap()

        if len(self.manualSplitPoints) > 0:
            flip = self.manualSplitPoints[0][0] > self.manualSplitPoints[0][1]
            if flip:
                optLap.preceeding = self.lap2.preceeding
            else:
                optLap.preceeding = self.lap1.preceeding

        for p in self.manualSplitPoints:
            flip = (p[0]-fromPts[0]) > (p[1]-fromPts[1])
            if flip:
                optLap.points += self.lap2.points[fromPts[1]:p[1]]
            else:
                optLap.points += self.lap1.points[fromPts[0]:p[0]]

            flip = not flip
            fromPts = p

        flip = (len(self.lap1.points)-fromPts[0]) > (len(self.lap2.points)-fromPts[1])
        if flip:
            optLap.points += self.lap2.points[fromPts[1]:]
            optLap.following = self.lap2.following
        else:
            optLap.points += self.lap1.points[fromPts[0]:]
            optLap.following = self.lap1.following

        for p in optLap.points:
            p.current_lap = 1
            p.recreatePackage()
        
        now = datetime.datetime.now()
        with open ( "./optlap-" + now.strftime("%Y-%m-%d_%H-%M-%S") + ".gt7lap", "wb") as f:
            if not optLap.preceeding is None:
                optLap.preceeding.current_lap = 0
                optLap.preceeding.recreatePackage()
                f.write(optLap.preceeding.raw)
            for p in optLap.points:
                f.write(p.raw)
            if not optLap.following is None:
                optLap.following.current_lap = 2
                optLap.following.recreatePackage()
                f.write(optLap.following.raw)
            
    def delegateKeyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Right.value:
            self.moveRight()
        elif e.key() == Qt.Key.Key_Left.value:
            self.moveLeft()
        elif e.key() == Qt.Key.Key_Up.value:
            self.moveUp()
        elif e.key() == Qt.Key.Key_Down.value:
            self.moveDown()
        elif e.key() == Qt.Key.Key_Plus.value:
            self.zoomIn()
        elif e.key() == Qt.Key.Key_Minus.value:
            self.zoomOut()
        
        elif e.key() == Qt.Key.Key_T.value:
            self.showText = not self.showText
            self.update()
        elif e.key() == Qt.Key.Key_F.value:
            if not 'finish' in self.showGroups:
                self.showGroups['finish'] = True
            self.showGroups['finish'] = not self.showGroups['finish']
            self.update()
        elif e.key() == Qt.Key.Key_S.value:
            if not 'time' in self.showGroups:
                self.showGroups['time'] = True
            self.showGroups['time'] = not self.showGroups['time']
            self.update()
        elif e.key() == Qt.Key.Key_B.value:
            if not 'brake' in self.showGroups:
                self.showGroups['brake'] = True
            self.showGroups['brake'] = not self.showGroups['brake']
            self.update()
        elif e.key() == Qt.Key.Key_A.value:
            if not 'throttle' in self.showGroups:
                self.showGroups['throttle'] = True
            self.showGroups['throttle'] = not self.showGroups['throttle']
            self.update()
        elif e.key() == Qt.Key.Key_G.value:
            if not 'gear' in self.showGroups:
                self.showGroups['gear'] = True
            self.showGroups['gear'] = not self.showGroups['gear']
            self.update()
        elif e.key() == Qt.Key.Key_W.value:
            self.writeFlippingLaps()

        elif e.key() == Qt.Key.Key_C.value:
            for m in self.temporaryMarkers:
                for ly in self.layers:
                    if m in ly:
                        ly.remove (m)
            self.temporaryMarkers = []
            self.manualSplitPoints = []
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
        elif e.key() == Qt.Key.Key_6.value:
            self.showLayers[5] = not self.showLayers[5]
            self.update()
        elif e.key() == Qt.Key.Key_7.value:
            self.showLayers[6] = not self.showLayers[6]
            self.update()



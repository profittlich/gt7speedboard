import sys
import os
import threading
from wakepy import keep
import math
import queue
import datetime
from cProfile import Profile
from pstats import SortKey, Stats

from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QSettings
from PyQt6.QtGui import QColor, QRegularExpressionValidator, QPixmap, QPainter, QPalette, QPen, QLinearGradient, QGradient
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox

from gt7telepoint import Point

import gt7telemetryreceiver as tele

class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GT7 TeleDash")
        self.starter = QPushButton("Start")

        ipLabel = QLabel("PlayStation IP address:")
        self.ip = QLineEdit()

        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QRegularExpression ("^" + ipRange
                 + "\\." + ipRange
                 + "\\." + ipRange
                 + "\\." + ipRange + "$");
        ipValidator = QRegularExpressionValidator(ipRegex)
        self.ip.setValidator(ipValidator)

        fmLabel = QLabel("Fuel multiplier:")
        self.fuelMultiplier = QSpinBox()
        self.fuelMultiplier.setMinimum(1)
        self.fuelMultiplier.setMaximum(100)

        fcLabel = QLabel("Max. fuel consumption:")
        self.maxFuelConsumption = QSpinBox()
        self.maxFuelConsumption.setSuffix(" l/100km")
        self.maxFuelConsumption.setMinimum(1)
        self.maxFuelConsumption.setMaximum(500)

        fwLabel = QLabel("Fuel meter turns red at:")
        self.fuelWarning = QSpinBox()
        self.fuelWarning.setSuffix(" l/100km")
        self.fuelWarning.setMinimum(1)
        self.fuelWarning.setMaximum(500)

        layout = QHBoxLayout()
        layout.addWidget(ipLabel)
        layout.addWidget(self.ip)
        layout.addWidget(self.starter)

        addr = QWidget()
        addr.setLayout(layout)

        self.experimental = QCheckBox("Show experimental displays")
        self.allowLoop = QCheckBox("Allow looping telemetry from playback")

        modeLabel = QLabel("Mode:")

        self.mode = QComboBox()
        self.mode.addItem("Laps")
        self.mode.addItem("Circuit Experience (experimental)")
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(modeLabel)
        mainLayout.addWidget(self.mode)
        mainLayout.addWidget(self.experimental)
        mainLayout.addWidget(self.allowLoop)
        mainLayout.addWidget(fmLabel)
        mainLayout.addWidget(self.fuelMultiplier)
        mainLayout.addWidget(fcLabel)
        mainLayout.addWidget(self.maxFuelConsumption)
        mainLayout.addWidget(fwLabel)
        mainLayout.addWidget(self.fuelWarning)
        mainLayout.addWidget(addr)

        mainLayout.insertStretch(-1)

        settings = QSettings("./gt7teledash.ini", QSettings.Format.IniFormat)
        self.ip.setText(settings.value("ip", ""))
        self.experimental.setChecked(settings.value("experimental")=="true")
        self.allowLoop.setChecked(settings.value("allowLoop")=="true")
        self.mode.setCurrentIndex(int(settings.value("mode",0)))
        self.fuelMultiplier.setValue(int(settings.value("fuelMultiplier", 1)))
        self.fuelWarning.setValue(int(settings.value("fuelWarning", 50)))
        self.maxFuelConsumption.setValue(int(settings.value("maxFuelConsumption", 150)))



class FuelGauge(QWidget):

    def __init__(self):
        super().__init__()
        self.level = 0.0
        self.maxLevel = 100
        self.threshold = 50

    def setLevel(self, l):
        self.level = min(l, self.maxLevel)

    def setMaxLevel(self, l):
        self.maxLevel = l

    def setThreshold(self, t):
        self.threshold = t

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        if self.level > self.threshold:
            qp.setPen(Qt.GlobalColor.red)
            qp.setBrush(Qt.GlobalColor.red)
        else:
            qp.setPen(QColor("#08f"))
            qp.setBrush(QColor("#08f"))
        try:
            qp.drawRect(0,int(self.height()*(self.maxLevel-self.level)/self.maxLevel), int(self.width()), int(self.height()))
        except OverflowError as e:
            print(e)
            print(self.maxLevel, self.level)
        qp.end()


class MapView(QWidget):

    def __init__(self):
        super().__init__()
        self.map = QPixmap(2000, 2000)
        self.map.fill(QColor("#222"))#Qt.GlobalColor.black)
        self.liveMap = QPixmap(2000, 2000)
        self.liveMap.fill(QColor("#222"))#Qt.GlobalColor.black)
        self.previousPoints = []
        self.curPoints = []
        self.mapOffset = None
        self.mapWindow = [1000,1000]
        self.mapColor = Qt.GlobalColor.white

    def setPoints(self, p1, p2):
        self.previousPoints.append (p1)
        self.curPoints.append (p2)

    def endLap(self, cleanLap):
        painter = QPainter(self.map)
        pen = QPen(self.mapColor)
        pen.setWidth(5)
        painter.setPen(pen)
        for pi in range(1, len(cleanLap)):
            px1 = 1000 + (0.25 * (cleanLap[pi-1].position_x + self.mapOffset[0])) 
            pz1 = 1000 + (0.25 * (cleanLap[pi-1].position_z + self.mapOffset[1])) 
            px2 = 1000 + (0.25 * (cleanLap[pi].position_x + self.mapOffset[0])) 
            pz2 = 1000 + (0.25 * (cleanLap[pi].position_z + self.mapOffset[1]))
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2))

        if len(cleanLap) > 0:
            px1 = 1010 + (0.25 * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz1 = 1010 + (0.25 * (cleanLap[-1].position_z + self.mapOffset[1])) 
            px2 = 990 + (0.25 * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz2 = 990 + (0.25 * (cleanLap[-1].position_z + self.mapOffset[1]))
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2))
            px1 = 990 + (0.25 * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz1 = 1010 + (0.25 * (cleanLap[-1].position_z + self.mapOffset[1])) 
            px2 = 1010 + (0.25 * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz2 = 990 + (0.25 * (cleanLap[-1].position_z + self.mapOffset[1]))
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2))

        painter.end()
        self.liveMap = self.map.copy()

    def paintEvent(self, event):
        while len (self.previousPoints) > 0  and len(self.curPoints) > 0:
            previousPoint = self.previousPoints.pop()
            curPoint = self.curPoints.pop()
            painter = QPainter(self.liveMap)
            pen = QPen(Qt.GlobalColor.red)
            pen.setWidth(3)
            painter.setPen(pen)
            if self.mapOffset is None:
                self.mapOffset = (-previousPoint.position_x, -previousPoint.position_z)
            px1 = 1000 + (0.25 * (previousPoint.position_x + self.mapOffset[0])) 
            pz1 = 1000 + (0.25 * (previousPoint.position_z + self.mapOffset[1])) 
            px2 = 1000 + (0.25 * (curPoint.position_x + self.mapOffset[0])) 
            pz2 = 1000 + (0.25 * (curPoint.position_z + self.mapOffset[1]))
            if max(px1,px2) > (self.mapWindow[0] + 240) and (self.mapWindow[0] + 250) < 2000 - self.width():
                self.mapWindow[0] += 1
            if min(px1,px2) < (self.mapWindow[0] - 240) and (self.mapWindow[0] - 250) > self.width():
                self.mapWindow[0] -= 1
            if max(pz1,pz2) > (self.mapWindow[1] + 240) and (self.mapWindow[1] + 250) < 2000 - self.height():
                self.mapWindow[1] += 1
            if min(pz1,pz2) < (self.mapWindow[1] - 240) and (self.mapWindow[1] - 250) > self.height():
                self.mapWindow[1] -= 1
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2))
            painter.end()

        qp = QPainter()
        qp.begin(self)

        scaleTarget = 3000#min(self.width(), self.height())
        aspectRatio = self.width()/self.height()

        qp.drawPixmap(self.rect(), self.liveMap.copy(int(self.mapWindow[0] - aspectRatio * 250), int(self.mapWindow[1]-250), int(aspectRatio * 500), 500).scaled(self.width(), self.height()))

        qp.end()


class LineDeviation(QWidget):

    def __init__(self):
        super().__init__()
        self.maxDist = 3
        self.dist = 0
        self.history = []
        self.p1 = None
        self.p2 = None
        self.redGradient = QLinearGradient (10,0,120,0);
        self.redGradient.setColorAt(0.0, QColor("#222"))
        self.redGradient.setColorAt(0.2, QColor("#222"))
        self.redGradient.setColorAt(1.0, Qt.GlobalColor.red);
        self.greenGradient = QLinearGradient (10,0,120,0);
        self.greenGradient.setColorAt(0.0, QColor("#222"))
        self.greenGradient.setColorAt(0.2, QColor("#222"))
        self.greenGradient.setColorAt(1.0, Qt.GlobalColor.green);

    def abs(self, x, y, z):
        return math.sqrt(x**2 + y**2 + z**2)

    def normal(self, x, y, z): # (0, 1, 0)
        a = self.abs(y, 0, -y)
        return (y/a, 0, -y/a)

    def setDistance(self, d):
        self.history.append(d)
        if (len(self.history) > 4):
            self.history = self.history[1:]
        self.dist = 0
        for i in self.history:
            self.dist+=i
        self.dist /= len(self.history)

    def setPoints(self, p2, p1):
        self.p1 = p1
        self.p2 = p2
        a1 = self.abs(p1.velocity_x, p1.velocity_y, p1.velocity_z)
        a2 = self.abs(p2.velocity_x, p2.velocity_y, p2.velocity_z)

        #cosangle = min(1,(p1.velocity_x * p2.velocity_x + p1.velocity_y * p2.velocity_y + p1.velocity_z * p2.velocity_z) / (a1*a2))
        #self.angle = math.acos(cosangle)

        #northcosangle = p1.velocity_z / a1
        #self.northangle = math.acos(northcosangle)
        #if p1.velocity_x < 0:
            #self.northangle = 2*math.pi - self.northangle

        self.angle1 = math.acos(p1.velocity_z / a1)
        if p1.velocity_x < 0:
            self.angle1 = 2*math.pi - self.angle1

        self.angle2 = math.acos(p2.velocity_z / a2)
        if p2.velocity_x < 0:
            self.angle2 = 2*math.pi - self.angle2

        self.angle = self.angle2-self.angle1
        #if self.angle < 0:
            #self.angle += math.pi

        n = self.normal(p1.velocity_x, p1.velocity_y, p1.velocity_z)
        dx = p2.position_x - p1.position_x
        dy = p2.position_y - p1.position_y
        dz = p2.position_z - p1.position_z

        d = dx*n[0] + dy*n[1] + dz*n[2]
        self.setDistance(d)

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        qp.fillRect(0, 0, int(self.width()), int(self.height()), QColor("#222"))
        pen = QPen(Qt.GlobalColor.white)
        pen.setWidth(5)
        qp.setPen(pen)
        font = self.font()
        font.setPointSize(36)
        font.setBold(True)
        self.setFont(font)
        if not self.p1 is None and not self.p2 is None:
            if self.dist < 0:
                self.redGradient.setStart(self.width()/2,0)
                self.redGradient.setFinalStop(self.width()/2 + self.dist/self.maxDist * self.width() / 2, 0)
                qp.fillRect(int(self.width()/2), 0, int(self.dist/self.maxDist * self.width() / 2), int(self.height()), self.redGradient)
                qp.drawLine(int(self.width()/2) + int(self.dist/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(self.dist/self.maxDist * self.width() / 2), int(self.height()))
            else:
                self.greenGradient.setStart(self.width()/2,0)
                self.greenGradient.setFinalStop(self.width()/2 + self.dist/self.maxDist * self.width() / 2, 0)
                qp.fillRect(int(self.width()/2), 0, int(self.dist/self.maxDist * self.width() / 2), int(self.height()), self.greenGradient)
                qp.drawLine(int(self.width()/2) + int(self.dist/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(self.dist/self.maxDist * self.width() / 2), int(self.height()))
            qp.drawText(10, 40, str(round(self.angle*180/math.pi,2)))
        qp.drawLine(int(self.width()/2), 0, int(self.width()/2), int (self.height()))
        qp.end()




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.startWindow = StartWindow()
        self.startWindow.starter.clicked.connect(self.startDash)
        self.startWindow.ip.returnPressed.connect(self.startDash)

        self.setWindowTitle("GT7 TeleDash")
        self.queue = queue.Queue()
        self.receiver = None
        self.isRecording = False

        self.circuitExperience = True
        self.experimental = False
        self.allowLoop = False

        self.newMessage = None
        self.messages = []

        self.setCentralWidget(self.startWindow)

    def makeDashWidget(self):
        # Lvl 4
        self.fuel = QLabel("?%")
        self.fuel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fuel.setAutoFillBackground(True)
        font = self.fuel.font()
        font.setPointSize(96)
        font.setBold(True)
        self.fuel.setFont(font)

        self.fuelBar = FuelGauge()

        if self.circuitExperience:
            self.mapView = MapView()
        else:
            self.laps = QLabel("? LAPS LEFT")
            self.laps.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.laps.setAutoFillBackground(True)
            font = self.laps.font()
            font.setPointSize(96)
            font.setBold(True)
            self.laps.setFont(font)
            pal = self.laps.palette()
            pal.setColor(self.laps.backgroundRole(), QColor("#222"))
            pal.setColor(self.laps.foregroundRole(), QColor("#fff"))
            self.laps.setPalette(pal)

        self.tyreFR = QLabel("?°C")
        self.tyreFR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFR.setAutoFillBackground(True)
        font = self.tyreFR.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreFR.setFont(font)
        pal = self.tyreFR.palette()
        pal.setColor(self.tyreFR.backgroundRole(), QColor('#222'))
        self.tyreFR.setPalette(pal)

        self.tyreFL = QLabel("?°C")
        self.tyreFL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreFL.setAutoFillBackground(True)
        font = self.tyreFL.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreFL.setFont(font)
        pal = self.tyreFL.palette()
        pal.setColor(self.tyreFL.backgroundRole(), QColor('#222'))
        self.tyreFL.setPalette(pal)
        
        self.tyreRR = QLabel("?°C")
        self.tyreRR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRR.setAutoFillBackground(True)
        font = self.tyreRR.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreRR.setFont(font)
        pal = self.tyreRR.palette()
        pal.setColor(self.tyreRR.backgroundRole(), QColor('#222'))
        self.tyreRR.setPalette(pal)

        self.tyreRL = QLabel("?°C")
        self.tyreRL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tyreRL.setAutoFillBackground(True)
        font = self.tyreRL.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreRL.setFont(font)
        pal = self.tyreRL.palette()
        pal.setColor(self.tyreRL.backgroundRole(), QColor('#222'))
        self.tyreRL.setPalette(pal)

        self.pedalBest = QLabel("")
        self.pedalBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalBest.setAutoFillBackground(True)
        font = self.pedalBest.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalBest.setFont(font)
        pal = self.pedalBest.palette()
        pal.setColor(self.pedalBest.backgroundRole(), QColor('#222'))
        self.pedalBest.setPalette(pal)

        self.speedBest = QLabel("BEST")
        self.speedBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedBest.setAutoFillBackground(True)
        font = self.speedBest.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedBest.setFont(font)
        pal = self.speedBest.palette()
        pal.setColor(self.speedBest.backgroundRole(), QColor('#222'))
        self.speedBest.setPalette(pal)

        self.lineBest = LineDeviation()

        self.pedalLast = QLabel("")
        self.pedalLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalLast.setAutoFillBackground(True)
        font = self.pedalLast.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalLast.setFont(font)
        pal = self.pedalLast.palette()
        pal.setColor(self.pedalLast.backgroundRole(), QColor('#222'))
        self.pedalLast.setPalette(pal)

        self.speedLast = QLabel("LAST")
        self.speedLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLast.setAutoFillBackground(True)
        font = self.speedLast.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedLast.setFont(font)
        pal = self.speedLast.palette()
        pal.setColor(self.speedLast.backgroundRole(), QColor('#222'))
        self.speedLast.setPalette(pal)

        self.lineLast = LineDeviation()

        self.pedalMedian = QLabel("")
        self.pedalMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalMedian.setAutoFillBackground(True)
        font = self.pedalMedian.font()
        font.setPointSize(64)
        font.setBold(True)
        self.pedalMedian.setFont(font)
        pal = self.pedalMedian.palette()
        pal.setColor(self.pedalMedian.backgroundRole(), QColor('#222'))
        self.pedalMedian.setPalette(pal)

        self.speedMedian = QLabel("MEDIAN")
        self.speedMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedMedian.setAutoFillBackground(True)
        font = self.speedMedian.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedMedian.setFont(font)
        pal = self.speedMedian.palette()
        pal.setColor(self.speedMedian.backgroundRole(), QColor('#222'))
        self.speedMedian.setPalette(pal)

        self.lineMedian = LineDeviation()

        # Lvl 3
        fuelWidget = QWidget()
        pal = self.fuel.palette()
        pal.setColor(self.fuel.backgroundRole(), QColor("#222"))
        self.fuel.setPalette(pal)
        fuelLayout = QGridLayout()
        fuelLayout.setContentsMargins(11,11,11,11)
        fuelWidget.setLayout(fuelLayout)
        fuelLayout.setColumnStretch(0, 1)
        fuelLayout.setColumnStretch(1, 1)

        fuelLayout.addWidget(self.fuel, 0, 0, 1, 1)
        fuelLayout.addWidget(self.fuelBar, 0, 1, 1, 1)
        if self.circuitExperience:
            fuelLayout.addWidget(self.mapView, 1, 0, 1, 2)
        else:
            fuelLayout.addWidget(self.laps, 1, 0, 1, 2)

        tyreWidget = QWidget()
        tyreLayout = QGridLayout()
        tyreWidget.setLayout(tyreLayout)
        tyreLayout.addWidget(self.tyreFL, 0, 0)
        tyreLayout.addWidget(self.tyreFR, 0, 1)
        tyreLayout.addWidget(self.tyreRL, 1, 0)
        tyreLayout.addWidget(self.tyreRR, 1, 1)

        speedWidget = QWidget()
        speedLayout = QGridLayout()
        speedWidget.setLayout(speedLayout)
        speedLayout.addWidget(self.speedBest, 2, 0)
        speedLayout.addWidget(self.speedMedian, 2, 1)
        speedLayout.addWidget(self.speedLast, 2, 2)
        if self.experimental:
            speedLayout.addWidget(self.pedalBest, 0, 0)
            speedLayout.addWidget(self.lineBest, 1, 0)
            speedLayout.addWidget(self.pedalMedian, 0, 1)
            speedLayout.addWidget(self.lineMedian, 1, 1)
            speedLayout.addWidget(self.pedalLast, 0, 2)
            speedLayout.addWidget(self.lineLast, 1, 2)
            speedLayout.setRowStretch(0, 1)
            speedLayout.setRowStretch(1, 1)
        speedLayout.setRowStretch(2, 4)

        # Lvl 2
        self.header = QLabel("? LAPS LEFT")
        font = self.header.font()
        font.setPointSize(64)
        font.setBold(True)
        self.header.setFont(font)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        headerFuel = QLabel("FUEL")
        font = headerFuel.font()
        font.setPointSize(64)
        font.setBold(True)
        headerFuel.setFont(font)
        headerFuel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        headerTyres = QLabel("TYRES")
        font = headerTyres.font()
        font.setPointSize(64)
        font.setBold(True)
        headerTyres.setFont(font)
        headerTyres.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.headerSpeed = QLabel("SPEED")
        font = self.headerSpeed.font()
        font.setPointSize(64)
        font.setBold(True)
        self.headerSpeed.setFont(font)
        self.headerSpeed.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.headerSpeed.setAutoFillBackground(True)

        # Lvl 1
        masterLayout = QGridLayout()
        self.masterWidget = QWidget()
        self.masterWidget.setLayout(masterLayout)
        masterLayout.setColumnStretch(0, 1)
        masterLayout.setColumnStretch(1, 1)
        masterLayout.setRowStretch(0, 1)
        masterLayout.setRowStretch(1, 1)
        masterLayout.setRowStretch(2, 10)
        masterLayout.setRowStretch(3, 1)
        masterLayout.setRowStretch(4, 4)
        masterLayout.addWidget(self.header, 0, 0, 1, 2)
        masterLayout.addWidget(headerFuel, 1, 1, 1, 1)
        masterLayout.addWidget(headerTyres, 3, 0, 1, 1)
        masterLayout.addWidget(self.headerSpeed, 1, 0, 1, 1)
        masterLayout.addWidget(fuelWidget, 2, 1, 3, 1)
        masterLayout.addWidget(tyreWidget, 4, 0, 1, 1)
        masterLayout.addWidget(speedWidget, 2, 0, 1, 1)

    def startDash(self):
        self.experimental = self.startWindow.experimental.isChecked()
        self.allowLoop = self.startWindow.allowLoop.isChecked()
        self.circuitExperience = self.startWindow.mode.currentIndex() == 1
        self.fuelMultiplier = self.startWindow.fuelMultiplier.value()
        self.maxFuelConsumption = self.startWindow.maxFuelConsumption.value()
        fuelWarning = self.startWindow.fuelWarning.value()
        
        ip = self.startWindow.ip.text()

        settings = QSettings("./gt7teledash.ini", QSettings.Format.IniFormat)
        settings.setValue("ip", ip)
        settings.setValue("experimental", self.experimental)
        settings.setValue("allowLoop", self.allowLoop)
        settings.setValue("mode", self.startWindow.mode.currentIndex())
        settings.setValue("fuelMultiplier", self.startWindow.fuelMultiplier.value())
        settings.setValue("maxFuelConsumption", self.startWindow.maxFuelConsumption.value())
        settings.setValue("fuelWarning", self.startWindow.fuelWarning.value())
        settings.sync()

        self.makeDashWidget()
        self.fuelBar.setThreshold(self.fuelMultiplier * fuelWarning)
        self.fuelBar.setMaxLevel(self.fuelMultiplier * self.maxFuelConsumption)
        self.setCentralWidget(self.masterWidget)

        self.initRace()

        self.receiver = tele.GT7TelemetryReceiver(ip)
        self.receiver.setQueue(self.queue)
        self.receiver.setIgnorePktId(self.allowLoop)
        self.thread = threading.Thread(target=self.receiver.runTelemetryReceiver)
        self.thread.start()

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start()

        self.debugCount = 0
        self.noThrottleCount = 0

    def stopDash(self):
        if not self.receiver is None:
            self.timer.stop()
            self.receiver.running = False
            self.thread.join()
            self.receiver = None

    def initRace(self):
        self.lastLap = -1
        self.lastFuel = -1
        self.lastFuelUsage = []
        self.fuelFactor = 0
        self.refueled = 0

        self.previousPoint = None

        self.newLapPos = []
        self.previousLaps = []
        self.bestLap = -1
        self.medianLap = -1

        self.closestILast = 0
        self.closestIBest = 0
        self.closestIMedian = 0

    def tyreTempColor(self, temp):
        col = QColor()
        hue = 0.333 - (temp - 70)/50
        if hue < 0:
            hue = 0
        if hue > 0.666:
            hue = 0.666
        col.setHsvF (hue, 1, 1)

        return "background-color: " + col.name() + ";"

    def tyreTempQColor(self, temp):
        col = QColor()
        hue = 0.333 - (temp - 70)/50
        if hue < 0:
            hue = 0
        if hue > 0.666:
            hue = 0.666
        col.setHsvF (hue, 1, 1)

        return col

    def speedDiffColor(self, d):
        col = QColor()
        hue = -d/60 + 60/360
        if hue < 0:
            hue = 0
        if hue > 120/360:
            hue = 120/360
        col.setHsvF (hue, 1, 1)

        return "background-color: " + col.name() + ";"

    def speedDiffQColor(self, d):
        col = QColor()
        hue = -d/60 + 60/360
        if hue < 0:
            hue = 0
        if hue > 120/360:
            hue = 120/360
        col.setHsvF (hue, 1, 1)

        return col

    def brakeQColor(self, d):
        col = QColor()
        col.setHsvF (0, 1, (0x22/0xff) + d * (1 - 0x22/0xff)/100)

        return col

    def distance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_y-p2.position_y)**2 + (p1.position_z-p2.position_z)**2)

    def findClosestPoint(self, lap, p, startIdx):
        shortestDistance = 100000000
        result = None
        dbgCount = 0
        for p2 in range(startIdx, len(lap)-10):
            dbgCount+=1
            curDist = self.distance(p, lap[p2])
            if curDist < 10 and curDist < shortestDistance:
                shortestDistance = curDist
                result = p2
            if not result is None and curDist > 20:
                break
            if curDist >= 500:
                break

        if result is None:
            return None, startIdx
        return lap[result], result

    def findClosestPointNoLimit(self, lap, p):
        shortestDistance = 100000000
        result = None
        for p2 in lap:
            curDist = self.distance(p, p2)
            if curDist < shortestDistance:
                shortestDistance = curDist
                result = p2

        return result

    def getLapLength(self, lap):
        totalDist = 0
        for i in range(1, len(lap)):
            totalDist += self.distance(lap[i-1], lap[i])
        return totalDist

    def getAvgSpeed(self, lap):
        if len(lap) == 0:
            return 0
        sm = 0
        for s in lap:
            sm += s.car_speed
        return sm / len(lap)

    def purgeBadLaps(self):
        print("PURGE laps")
        longestLength = 0
        longestLap = None
        for l in self.previousLaps:
            ll = self.getLapLength(l[1])
            if longestLength < ll:
                longestLength = ll
                longestLap = l

        if not longestLap is None:
            print("Longest: ", longestLength, longestLap[0])
        temp = []
        for l in self.previousLaps:
            print ("\nCheck lap", l[0])
            d = self.distance(longestLap[1][-1], l[1][-1])
            c = self.findClosestPointNoLimit(l[1], longestLap[1][-1])
            d2 = -1
            d3 = -1
            if not c is None:
                d2 = self.distance(longestLap[1][-1], c)
            c3 = self.findClosestPointNoLimit(longestLap[1], l[1][-1])
            if not c3 is None:
                d3 = self.distance(l[1][-1], c3)
            print("End distance:", d)
            if d > 15:
                print("PURGE lap", len(l[1])/60, d)
            else:
                temp.append(l)
        self.previousLaps = temp




    def cleanUpLap(self, lap):
        if len(lap) == 0:
            print("Lap is empty")
            return lap
        if len(lap) < 600:
            print("\nLap is short")
            return lap
        if (lap[-1].throttle > 0):# or lap[-1].brake > 0):
            print("Throttle to the end")
            return lap
        afterLap = 0
        for i in range(1, len(lap)):
            if lap[-i].throttle == 0:# and lap[-i].brake == 0:
                afterLap+=1
            else:
                break
        print("Remove", afterLap, "of", len(lap))
        if afterLap > 0:
            result = lap[:-afterLap]
        else:
            result = lap
        print("Got", len(result))
        return result

    def findBestLap(self):
        bestIndex = 0
        bestTime = 100000000.0
        for t in range(len(self.previousLaps)):
            if self.previousLaps[t][0] < bestTime:
                bestTime = self.previousLaps[t][0]
                bestIndex = t
        return bestIndex

    def findMedianLap(self):
        sorter = []
        for e in self.previousLaps:
            sorter.append(e[0])

        sorter = sorted(sorter)
        target = sorter[len(sorter)//2]
        for e in range(len(self.previousLaps)):
            if self.previousLaps[e][0] == target:
                return e
        return 0

    def makeFuelBar(self, val):
        if val > 1:
            color = "darkred"
        else:
            color = "orange"
        val = min (1, max(0.002, val))
        return "background: qlineargradient( x1:0 y1:1, x2:0 y2:0, stop:" + str(val-0.001) + " " + color + ", stop:" + str (val) + " #222);"

    def updateDisplay(self):

        while not self.queue.empty():
            self.debugCount += 1
            d = self.queue.get()

            curPoint = Point(d)

            if not self.newMessage is None:
                print(len(self.newLapPos), -min(60*5,len(self.newLapPos)-1))
                self.messages.append([self.newLapPos[-min(60*5,len(self.newLapPos)-1)], self.newMessage])
                self.newMessage = None
                print(self.messages)

            if curPoint.is_paused or not curPoint.in_race:
                continue

            if curPoint.current_lap <= 0 and not self.circuitExperience:
                self.initRace()
                continue

            #print(len(self.newLapPos))

            if self.circuitExperience and not self.previousPoint is None:
                self.mapView.setPoints(self.previousPoint, curPoint)
                self.mapView.update()


            if curPoint.throttle == 0 and curPoint.brake == 0:
                self.noThrottleCount+=1
            elif self.noThrottleCount > 0:
                self.noThrottleCount=0

            # TYRE TEMPS
            self.tyreFL.setText (str(round(curPoint.tyre_temp_FL)) + "°C")
            pal = self.tyreFL.palette()
            pal.setColor(self.tyreFL.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_FL)))
            self.tyreFL.setPalette(pal)

            self.tyreFR.setText (str(round(curPoint.tyre_temp_FR)) + "°C")
            pal = self.tyreFR.palette()
            pal.setColor(self.tyreFR.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_FR)))
            self.tyreFR.setPalette(pal)

            self.tyreRR.setText (str(round(curPoint.tyre_temp_RR)) + "°C")
            pal = self.tyreRR.palette()
            pal.setColor(self.tyreRR.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_RR)))
            self.tyreRR.setPalette(pal)

            self.tyreRL.setText (str(round(curPoint.tyre_temp_RL)) + "°C")
            pal = self.tyreRL.palette()
            pal.setColor(self.tyreRL.backgroundRole(), QColor(self.tyreTempQColor(curPoint.tyre_temp_RL)))
            self.tyreRL.setPalette(pal)


            #print("LAP ", self.lastLap, curPoint.current_lap, curPoint.total_laps, curPoint.time_on_track)
            # LAP CHANGE
            if self.circuitExperience and self.noThrottleCount == 60 * 10:
                print("Lap ended 10 seconds ago")
            if self.lastLap < curPoint.current_lap or (self.circuitExperience and (self.distance(curPoint, self.previousPoint) > 250 or self.noThrottleCount == 60 * 10)):
                if self.circuitExperience:
                    cleanLap = self.cleanUpLap(self.newLapPos)
                    self.mapView.endLap(cleanLap)
                    self.mapView.update()
                else:
                    cleanLap = self.newLapPos
                #print(len(self.newLapPos), len(cleanLap))
                lapLen = self.getLapLength(cleanLap)
                
                if lapLen < 10:
                    print("LAP CHANGE short")
                else:
                    print("\nLAP CHANGE", self.lastLap, curPoint.current_lap, str(round(lapLen, 3)) + " m", round(len (cleanLap) / 60,3), "s")
                    if (len(self.newLapPos)>0):
                        print("start", self.newLapPos[0].position_x, self.newLapPos[0].position_y, self.newLapPos[0].position_z)
                    if not self.previousPoint is None:
                        print("end", self.previousPoint.position_x, self.previousPoint.position_y, self.previousPoint.position_z)

                if  not (self.lastLap == -1 and curPoint.current_fuel < 99):
                    if self.lastLap > 0:
                        if self.circuitExperience:
                            lastLapTime = len(cleanLap)/60.0
                        else:
                            lastLapTime = curPoint.last_lap
                        self.previousLaps.append([lastLapTime, cleanLap])
                        print("Append lap", lastLapTime, len(cleanLap))
                        if self.circuitExperience:
                            self.purgeBadLaps()
                        #self.previousLaps.append([lastLapTime, self.newLapPos])
                        #for pl in self.previousLaps:
                            #print(pl[0], len(pl[1]), len(pl[1]) / 60)
                    
                        self.bestLap = self.findBestLap()
                        self.medianLap = self.findMedianLap()
                        self.newLapPos = []
                        self.closestILast = 0
                        self.closestIBest = 0
                        self.closestIMedian = 0

                        print("\nBest lap:", self.bestLap, self.previousLaps[self.bestLap][0])
                        print("Median lap:", self.medianLap, self.previousLaps[self.medianLap][0])
                        print("Last lap:", len(self.previousLaps)-1, self.previousLaps[-1][0])

                    if self.lastFuel != -1:
                        fuelDiff = self.lastFuel - curPoint.current_fuel/curPoint.fuel_capacity
                        if fuelDiff > 0:
                            self.lastFuelUsage.append(fuelDiff)
                            self.refueled += 1
                        elif fuelDiff < 0:
                            self.refueled = 0
                        if len(self.lastFuelUsage) > 5:
                            self.lastFuelUsage = self.lastFuelUsage[1:]
                    self.lastFuel = curPoint.current_fuel/curPoint.fuel_capacity

                    if len(self.lastFuelUsage) > 0:
                        self.fuelFactor = self.lastFuelUsage[0]
                        for i in range(1, len(self.lastFuelUsage)):
                            self.fuelFactor = 0.333 * self.fuelFactor + 0.666 * self.lastFuelUsage[i]

                self.lastLap = curPoint.current_lap
            elif (self.lastLap > curPoint.current_lap or curPoint.current_lap == 0) and not self.circuitExperience:
                self.initRace()

            # FUEL
            if self.refueled > 0:
                lapValue = self.refueled
                if self.experimental and self.closestILast > 0:
                    lapValue += (
                            self.closestILast / len(self.previousLaps[-1][1]) +
                            self.closestIBest / len(self.previousLaps[self.bestLap][1]) +
                            self.closestIMedian / len(self.previousLaps[self.medianLap][1])) / 3
                    lapValue = round(lapValue, 2)
                refuelLaps = "\n" + str (lapValue) + " SINCE REFUEL"
            else:
                refuelLaps = ""

            if self.fuelFactor != 0:
                fuelLapPercent = "\n" + str(round(100 * self.fuelFactor,1)) + "% PER LAP"
            else:
                fuelLapPercent = ""

            self.fuel.setText(str(round(100 * curPoint.current_fuel / curPoint.fuel_capacity)) + "%" + fuelLapPercent + refuelLaps)
            if not self.previousPoint is None:
                fuelConsumption = self.previousPoint.current_fuel-curPoint.current_fuel 
                fuelConsumption *= 60 * 60 * 60 # l per hour
                if curPoint.car_speed > 0:
                    fuelConsumption /= curPoint.car_speed # l per km
                    fuelConsumption *= 100 # l per 100 km

                self.fuelBar.setLevel(max(0, fuelConsumption))
                self.fuelBar.update()

            messageShown = False
            for m in self.messages:
                #print( self.distance(curPoint, m[0]))
                if not self.circuitExperience and self.distance(curPoint, m[0]) < 100:
                    pal = self.laps.palette()
                    if datetime.datetime.now().microsecond < 500000:
                        pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.red)
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    else:
                        pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.white)
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.red)
                    self.laps.setPalette(pal)
                    self.laps.setText(m[1])
                    messageShown = True


            if not self.circuitExperience and (not self.experimental or not messageShown):
                if self.fuelFactor > 0:
                    self.laps.setText(str(round(curPoint.current_fuel / curPoint.fuel_capacity / self.fuelFactor, 2)) + " LAPS FUEL")
                    if round(curPoint.current_fuel / curPoint.fuel_capacity / self.fuelFactor, 2) < 1:
                        pal = self.laps.palette()
                        pal.setColor(self.laps.backgroundRole(), Qt.GlobalColor.red)
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                        self.laps.setPalette(pal)
                    elif round(curPoint.current_fuel / curPoint.fuel_capacity / self.fuelFactor, 2) < 2:
                        pal = self.laps.palette()
                        pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                        pal.setColor(self.laps.foregroundRole(), QColor('#f80'))
                        self.laps.setPalette(pal)
                    else:
                        pal = self.laps.palette()
                        pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                        pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                        self.laps.setPalette(pal)
                elif curPoint.current_fuel == curPoint.fuel_capacity:
                    self.laps.setText("FOREVER")
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                    pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    self.laps.setPalette(pal)
                else:
                    self.laps.setText("measuring")
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), QColor('#222'))
                    pal.setColor(self.laps.foregroundRole(), Qt.GlobalColor.white)
                    self.laps.setPalette(pal)

            # SPEED
            #if self.experimental:
                #pal = self.headerSpeed.palette()
                #pal.setColor(self.headerSpeed.backgroundRole(), self.speedDiffQColor((curPoint.throttle - curPoint.brake)/10))
                #self.headerSpeed.setPalette(pal)

            closestPLast = None
            closestPBest = None
            closestPMedian = None
            if len(self.previousLaps) > 0:
                closestPLast, self.closestILast = self.findClosestPoint (self.previousLaps[-1][1], curPoint, self.closestILast)
                closestPBest, self.closestIBest = self.findClosestPoint (self.previousLaps[self.bestLap][1], curPoint, self.closestIBest)
                closestPMedian, self.closestIMedian = self.findClosestPoint (self.previousLaps[self.medianLap][1], curPoint, self.closestIMedian)

            if not closestPLast is None:
                speedDiff = closestPLast.car_speed - curPoint.car_speed
                pal = self.speedLast.palette()
                pal.setColor(self.speedLast.backgroundRole(), self.speedDiffQColor(speedDiff))
                self.speedLast.setPalette(pal)

                if self.experimental:
                    pal = self.pedalLast.palette()
                    if closestPLast.brake > 0:
                        self.pedalLast.setText("BRAKE")
                        pal.setColor(self.pedalLast.backgroundRole(), self.brakeQColor(closestPLast.brake))
                    #elif closestPLast.throttle > 0:
                    else:
                        self.pedalLast.setText("")
                        pal.setColor(self.pedalLast.backgroundRole(), QColor("#222"))
                    #else:
                        #self.pedalLast.setText("COAST")
                        #pal.setColor(self.pedalLast.backgroundRole(), self.speedDiffQColor(0))
                    self.pedalLast.setPalette(pal)
                    self.lineLast.setPoints(curPoint, closestPLast)
                    self.lineLast.update()
            else:
                pal = self.speedLast.palette()
                pal.setColor(self.speedLast.backgroundRole(), QColor('#222'))
                self.speedLast.setPalette(pal)

            #self.lineLast.setPoints(curPoint, curPoint)
            #self.lineLast.update()

            if not closestPBest is None:
                speedDiff = closestPBest.car_speed - curPoint.car_speed
                pal = self.speedBest.palette()
                pal.setColor(self.speedBest.backgroundRole(), self.speedDiffQColor(speedDiff))
                self.speedBest.setPalette(pal)
                if self.experimental:
                    pal = self.pedalBest.palette()
                    if closestPBest.brake > 0:
                        self.pedalBest.setText("BRAKE")
                        pal.setColor(self.pedalBest.backgroundRole(), self.brakeQColor(closestPBest.brake))
                    #elif closestPBest.throttle > 0:
                    else:
                        self.pedalBest.setText("")
                        pal.setColor(self.pedalBest.backgroundRole(), QColor("#222"))
                    #else:
                        #self.pedalBest.setText("COAST")
                        #pal.setColor(self.pedalBest.backgroundRole(), self.speedDiffQColor(0))
                    self.pedalBest.setPalette(pal)

                    self.lineBest.setPoints(curPoint, closestPBest)
                    self.lineBest.update()
            else:
                pal = self.speedBest.palette()
                pal.setColor(self.speedBest.backgroundRole(), QColor('#222'))
                self.speedBest.setPalette(pal)

            if not closestPMedian is None:
                speedDiff = closestPMedian.car_speed - curPoint.car_speed
                pal = self.speedMedian.palette()
                pal.setColor(self.speedMedian.backgroundRole(), self.speedDiffQColor(speedDiff))
                self.speedMedian.setPalette(pal)
                if self.experimental:
                    pal = self.pedalMedian.palette()
                    if closestPMedian.brake > 0:
                        self.pedalMedian.setText("BRAKE")
                        pal.setColor(self.pedalMedian.backgroundRole(), self.brakeQColor(closestPMedian.brake))
                    #elif closestPMedian.throttle > 0:
                    else:
                        self.pedalMedian.setText("")
                        pal.setColor(self.pedalMedian.backgroundRole(), QColor("#222"))
                    #else:
                        #self.pedalMedian.setText("COAST")
                        #pal.setColor(self.pedalMedian.backgroundRole(), self.speedDiffQColor(0))
                    self.pedalMedian.setPalette(pal)
                    self.lineMedian.setPoints(curPoint, closestPMedian)
                    self.lineMedian.update()
            else:
                pal = self.speedMedian.palette()
                pal.setColor(self.speedMedian.backgroundRole(), QColor('#222'))
                self.speedMedian.setPalette(pal)

            # LAP DISPLAY
            lapSuffix = ""
            if self.isRecording:
                lapSuffix = " [RECORDING]"
            if curPoint.total_laps > 0:
                lapValue = curPoint.total_laps - curPoint.current_lap + 1
                if self.experimental and self.closestILast > 0:
                    lapValue -= (
                            self.closestILast / len(self.previousLaps[-1][1]) +
                            self.closestIBest / len(self.previousLaps[self.bestLap][1]) +
                            self.closestIMedian / len(self.previousLaps[self.medianLap][1])) / 3
                    lapValue = round(lapValue, 2)
                self.header.setText(str(lapValue) + " LAPS LEFT" + lapSuffix)
            else:
                lapValue = curPoint.current_lap
                if self.experimental and self.closestILast > 0:
                    lapValue += (
                            self.closestILast / len(self.previousLaps[-1][1]) +
                            self.closestIBest / len(self.previousLaps[self.bestLap][1]) +
                            self.closestIMedian / len(self.previousLaps[self.medianLap][1])) / 3
                    lapValue = round(lapValue, 2)
                self.header.setText("LAP " + str(lapValue) + lapSuffix)

            self.previousPoint = curPoint
            self.newLapPos.append(curPoint)


    def closeEvent(self, event):
        self.stopDash()
        event.accept()


    def toggleRecording(self):
        if self.experimental:
            if self.isRecording:
                self.isRecording = False
                self.receiver.stopRecording()
            else:
                self.receiver.startRecording()
                self.isRecording = True

    def keyPressEvent(self, e):
        if self.centralWidget() == self.masterWidget:
            if e.key() == Qt.Key.Key_R.value:
                self.toggleRecording()
            elif e.key() == Qt.Key.Key_Escape.value:
                if self.isRecording:
                    self.isRecording = False
                    self.receiver.stopRecording()
                self.stopDash()
                self.startWindow = StartWindow()
                self.startWindow.starter.clicked.connect(self.startDash)
                self.startWindow.ip.returnPressed.connect(self.startDash)
                self.setCentralWidget(self.startWindow)
            elif e.key() == Qt.Key.Key_Space.value:
                self.newMessage = "CAUTION"



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    window.startWindow.ip.setFocus()


    with keep.presenting():
        app.exec()


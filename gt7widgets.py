from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QSettings
from PyQt6.QtGui import QColor, QRegularExpressionValidator, QPixmap, QPainter, QPalette, QPen, QLinearGradient, QGradient
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox, QGroupBox, QLineEdit, QFileDialog
import math

class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GT7 SpeedBoard 1.0")
        modeLabel = QLabel("Mode:")

        self.mode = QComboBox()
        self.mode.addItem("Laps")
        self.mode.addItem("Circuit Experience (experimental)")
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(modeLabel)
        mainLayout.addWidget(self.mode)

        cols = QWidget()
        mainLayoutCols = QHBoxLayout()
        cols.setLayout(mainLayoutCols)
        mainLayout.addWidget(cols)

        ll = QWidget()
        mainLayoutL = QVBoxLayout()
        ll.setLayout(mainLayoutL)
        mainLayoutCols.addWidget(ll)

        lr = QWidget()
        mainLayoutR = QVBoxLayout()
        lr.setLayout(mainLayoutR)
        mainLayoutCols.addWidget(lr)

        # GENERAL
        gnGroup = QGroupBox("General")
        mainLayoutL.addWidget(gnGroup)
        gnLayout = QVBoxLayout()
        gnGroup.setLayout(gnLayout)

        self.keepLaps = QCheckBox("Keep laps through setup changes and sessions (experimental)")
        gnLayout.addWidget(self.keepLaps)

        # VIEW
        vwGroup = QGroupBox("View")
        mainLayoutL.addWidget(vwGroup)
        vwLayout = QVBoxLayout()
        vwGroup.setLayout(vwLayout)

        self.lapDecimals = QCheckBox("Show decimals in lap displays (experimental)")
        self.cbOptimal = QCheckBox("Optimal lap")
        self.cbOptimal.setEnabled(False)
        self.cbBest = QCheckBox("Best lap")
        self.cbMedian = QCheckBox("Median lap")
        self.cbRefA = QCheckBox("Reference lap A")
        self.cbRefA.stateChanged.connect(self.chooseReferenceLapA)
        self.refAFile = ""
        self.cbRefB = QCheckBox("Reference lap B")
        self.cbRefB.stateChanged.connect(self.chooseReferenceLapB)
        self.refBFile = ""
        self.cbRefC = QCheckBox("Reference lap C")
        self.cbRefC.stateChanged.connect(self.chooseReferenceLapC)
        self.refCFile = ""
        self.cbLast = QCheckBox("Last lap")
        
        vwLayout.addWidget(self.lapDecimals)
        #vwLayout.addWidget(self.cbOptimal)
        vwLayout.addWidget(self.cbBest)
        vwLayout.addWidget(self.cbMedian)
        vwLayout.addWidget(self.cbRefA)
        vwLayout.addWidget(self.cbRefB)
        vwLayout.addWidget(self.cbRefC)
        vwLayout.addWidget(self.cbLast)

        # RECORDING
        recGroup = QGroupBox("Recording")
        mainLayoutL.addWidget(recGroup)
        recLayout = QVBoxLayout()
        recGroup.setLayout(recLayout)

        self.recordingEnabled = QCheckBox("Allow recording data by pressing [R]")
        self.sessionName = QLineEdit()
        self.saveSessionName = QCheckBox("Remember session name")
        pbChooseStorage = QPushButton("Choose storage location")
        self.lStorageLocation = QLabel()
        self.storageLocation = ""
        self.lStorageLocation.setText ("Storage location: " + self.storageLocation)
        pbChooseStorage.clicked.connect(self.chooseStorage)
        
        recLayout.addWidget(self.recordingEnabled)
        recLayout.addWidget(QLabel("Session name:"))
        recLayout.addWidget(self.sessionName)
        recLayout.addWidget(self.saveSessionName)
        recLayout.addWidget(self.lStorageLocation)
        recLayout.addWidget(pbChooseStorage)
        
        # RACING LINE
        rlGroup = QGroupBox("Racing line")
        mainLayoutL.addWidget(rlGroup)
        rlLayout = QVBoxLayout()
        rlGroup.setLayout(rlLayout)

        self.linecomp = QCheckBox("Show racing line comparisons (experimental)")
        self.messagesEnabled = QCheckBox("Allow adding warning locations by pressing [space] (experimental)")
        
        rlLayout.addWidget(self.linecomp)
        rlLayout.addWidget(self.messagesEnabled)

        # BRAKE POINTS
        bpGroup = QGroupBox("Brake points")
        bpLayout = QVBoxLayout()
        bpGroup.setLayout(bpLayout)
        mainLayoutR.addWidget(bpGroup)

        self.brakepoints = QCheckBox("Show brake points")
        self.countdownBrakepoint = QCheckBox("Count down to best brake points (experimental)")
        self.bigCountdownBrakepoint = QLabel("Whole screen brake point colors for:")
        self.bigCountdownTarget = QComboBox()
        self.bigCountdownTarget.addItem("Nothing")
        self.bigCountdownTarget.addItem("Best lap")
        self.bigCountdownTarget.addItem("Reference lap A")
        self.bigCountdownTarget.addItem("Reference lap B")
        self.bigCountdownTarget.addItem("Reference lap C")
        
        bpLayout.addWidget(self.brakepoints)
        bpLayout.addWidget(self.countdownBrakepoint)
        bpLayout.addWidget(self.bigCountdownBrakepoint)
        bpLayout.addWidget(self.bigCountdownTarget)
        
        # NETWORK
        netGroup = QGroupBox("Network")
        netLayout = QVBoxLayout()
        netGroup.setLayout(netLayout)
        mainLayoutR.addWidget(netGroup)

        self.allowLoop = QCheckBox("Allow looping telemetry from playback (experimental)")
        
        netLayout.addWidget(self.allowLoop)

        # FUEL
        fuGroup = QGroupBox("Fuel")
        fuLayout = QVBoxLayout()
        fuGroup.setLayout(fuLayout)
        mainLayoutR.addWidget(fuGroup)

        self.fuelMultiplier = QSpinBox()
        self.fuelMultiplier.setMinimum(1)
        self.fuelMultiplier.setMaximum(100)

        self.maxFuelConsumption = QSpinBox()
        self.maxFuelConsumption.setSuffix(" l/100km")
        self.maxFuelConsumption.setMinimum(1)
        self.maxFuelConsumption.setMaximum(500)

        self.fuelWarning = QSpinBox()
        self.fuelWarning.setSuffix(" l/100km")
        self.fuelWarning.setMinimum(1)
        self.fuelWarning.setMaximum(500)
        fuLayout.addWidget(QLabel("Fuel multiplier:"))
        fuLayout.addWidget(self.fuelMultiplier)
        fuLayout.addWidget(QLabel("Max. fuel consumption:"))
        fuLayout.addWidget(self.maxFuelConsumption)
        fuLayout.addWidget(QLabel("Fuel meter turns red at:"))
        fuLayout.addWidget(self.fuelWarning)

        # SHORTCUTS
        ksGroup = QGroupBox("Keyboard shortcuts")
        ksLayout = QVBoxLayout()
        ksGroup.setLayout(ksLayout)
        mainLayoutR.addWidget(ksGroup)

        ksLayout.addWidget(QLabel("ESC - return to configuration\n"+
                                  "R - start/stop recording\n"+
                                  "SPACE - set CAUTION marker to current location\n"+
                                  "B - save best lap\n"+
                                  "L - save last lap\n"+
                                  "M - save median lap\n"+
                                  "A - save all laps\n"+
                                  "W - save warning messages\n"
                                  ))

        # CONNECT
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


        layout = QHBoxLayout()
        layout.addWidget(ipLabel)
        layout.addWidget(self.ip)
        layout.addWidget(self.starter)

        addr = QWidget()
        addr.setLayout(layout)


        mainLayout.insertStretch(-1)
        mainLayout.addWidget(addr)

        print("Load preferences")
        settings = QSettings()#"./gt7speedboard.ini", QSettings.Format.IniFormat)
        self.mode.setCurrentIndex(int(settings.value("mode",0)))

        self.keepLaps.setChecked(settings.value("keepLaps") in [ True, "true"])

        self.ip.setText(settings.value("ip", ""))
        self.storageLocation = settings.value("storageLocation", "")
        self.lStorageLocation.setText ("Storage location: " + self.storageLocation)

        self.lapDecimals.setChecked(settings.value("lapDecimals") in [ True, "true"])
        self.cbOptimal.setChecked(settings.value("showOtimalLap") in [ True, "true"])
        self.cbBest.setChecked(settings.value("showBestLap") in [ True, "true"])
        self.cbMedian.setChecked(settings.value("showMedianLap") in [ True, "true"])
        self.cbLast.setChecked(settings.value("showLastLap") in [ True, "true"])
        

        self.recordingEnabled.setChecked(settings.value("recordingEnabled") in [ True, "true"])
        self.messagesEnabled.setChecked(settings.value("messagesEnabled") in [ True, "true"])
        self.sessionName.setText(settings.value("sessionName", ""))
        self.saveSessionName.setChecked(settings.value("saveSessionName") in [ True, "true"])

        self.linecomp.setChecked(settings.value("linecomp") in [ True, "true"])
        
        self.brakepoints.setChecked(settings.value("brakepoints") in [ True, "true"])
        self.countdownBrakepoint.setChecked(settings.value("countdownBrakepoint") in [True, "true"])
        self.bigCountdownTarget.setCurrentIndex(int(settings.value("bigCountdownTarget",0)))

        self.allowLoop.setChecked(settings.value("allowLoop") in [True, "true"])
        
        self.fuelMultiplier.setValue(int(settings.value("fuelMultiplier", 1)))
        self.fuelWarning.setValue(int(settings.value("fuelWarning", 50)))
        self.maxFuelConsumption.setValue(int(settings.value("maxFuelConsumption", 150)))

    def chooseStorage(self):
        chosen = QFileDialog.getExistingDirectory()
        if chosen == "":
            print("None")
        else:
            self.storageLocation = chosen
            self.lStorageLocation.setText ("Storage location: " + self.storageLocation)
            print(chosen)

    def chooseReferenceLapA(self, on):
        if on:
            chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7)")
            if chosen[0] == "":
                print("None")
                self.cbRefA.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.refAFile = chosen[0]
                self.cbRefA.setText("Reference lap A: " + chosen[0][chosen[0].rfind("/")+1:])
        else:
            self.cbRefA.setText("Reference lap A")

    def chooseReferenceLapB(self, on):
        if on:
            chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7)")
            if chosen[0] == "":
                print("None")
                self.cbRefB.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.refBFile = chosen[0]
                self.cbRefB.setText("Reference lap B: " + chosen[0][chosen[0].rfind("/")+1:])
        else:
            self.cbRefB.setText("Reference lap B")

    def chooseReferenceLapC(self, on):
        if on:
            chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7)")
            if chosen[0] == "":
                print("None")
                self.cbRefC.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.refCFile = chosen[0]
                self.cbRefC.setText("Reference lap C: " + chosen[0][chosen[0].rfind("/")+1:])
        else:
            self.cbRefC.setText("Reference lap C")



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
        self.size = [2000, 2000]
        self.map = QPixmap(self.size[0], self.size[1])
        self.map.fill(QColor("#222"))#Qt.GlobalColor.black)
        self.liveMap = QPixmap(self.size[0], self.size[1])
        self.liveMap.fill(QColor("#222"))#Qt.GlobalColor.black)
        self.previousPoints = []
        self.curPoints = []
        self.mapOffset = None
        self.mapWindow = [self.size[0]/2,self.size[1]/2]
        self.mapColor = QColor("#77f")
        self.zoom = 0.7

    def setPoints(self, p1, p2, color = Qt.GlobalColor.red):
        self.previousPoints.append (p1)
        self.curPoints.append (p2)
        self.liveColor = color

    def endLap(self, cleanLap):
        if self.mapOffset is None:
            return
        painter = QPainter(self.map)
        pen = QPen(self.mapColor)
        pen.setWidth(5)
        painter.setPen(pen)
        for pi in range(1, len(cleanLap)):
            px1 = self.size[0]/2 + (self.zoom * (cleanLap[pi-1].position_x + self.mapOffset[0])) 
            pz1 = self.size[1]/2 + (self.zoom * (cleanLap[pi-1].position_z + self.mapOffset[1])) 
            px2 = self.size[0]/2 + (self.zoom * (cleanLap[pi].position_x + self.mapOffset[0])) 
            pz2 = self.size[1]/2 + (self.zoom * (cleanLap[pi].position_z + self.mapOffset[1]))
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2))

        if len(cleanLap) > 0:
            px1 = self.size[0]/2 + 10 + (self.zoom * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz1 = self.size[0]/2 + 10 + (self.zoom * (cleanLap[-1].position_z + self.mapOffset[1])) 
            px2 = self.size[1]/2 - 10 + (self.zoom * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz2 = self.size[1]/2 - 10 + (self.zoom * (cleanLap[-1].position_z + self.mapOffset[1]))
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2))
            px1 = self.size[1]/2 - 10 + (self.zoom * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz1 = self.size[0]/2 + 10 + (self.zoom * (cleanLap[-1].position_z + self.mapOffset[1])) 
            px2 = self.size[0]/2 + 10 + (self.zoom * (cleanLap[-1].position_x + self.mapOffset[0])) 
            pz2 = self.size[1]/2 - 10 + (self.zoom * (cleanLap[-1].position_z + self.mapOffset[1]))
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2))

        painter.end()
        self.liveMap = self.map.copy()

    def paintEvent(self, event):
        aspectRatio = self.width()/self.height()
        baseAspectRatio = self.size[0] / self.size[1]

        while len (self.previousPoints) > 0  and len(self.curPoints) > 0:
            previousPoint = self.previousPoints.pop()
            curPoint = self.curPoints.pop()
            if previousPoint.position_x - curPoint.position_x > 5 or previousPoint.position_z - curPoint.position_z > 5:
                continue

            painter = QPainter(self.liveMap)
            pen = QPen(self.liveColor)
            pen.setWidth(5)
            painter.setPen(pen)
            
            if self.mapOffset is None:
                self.mapOffset = (-previousPoint.position_x, -previousPoint.position_z)
            
            px1 = self.size[0]/2 + (self.zoom * (previousPoint.position_x + self.mapOffset[0])) 
            pz1 = self.size[1]/2 + (self.zoom * (previousPoint.position_z + self.mapOffset[1])) 
            px2 = self.size[0]/2 + (self.zoom * (curPoint.position_x + self.mapOffset[0])) 
            pz2 = self.size[1]/2 + (self.zoom * (curPoint.position_z + self.mapOffset[1]))
            
            temp = self.zoom
            self.zoom=0.25
            #TODO: Handle leaving the pixmap area
            if max(px1,px2) > (self.mapWindow[0] + (self.size[0]-100)*self.zoom*aspectRatio):                                           # and (self.mapWindow[0] + 1000*self.zoom*aspectRatio) < 2000 - self.width():
                self.mapWindow[0] += math.ceil(abs(max(px1,px2) - (self.mapWindow[0] + (self.size[0]-100)*self.zoom*aspectRatio))/10)
            if min(px1,px2) < (self.mapWindow[0] - (self.size[0]-100)*self.zoom*aspectRatio):                                           # and (self.mapWindow[0] - 1000*self.zoom*aspectRatio) > self.width():
                self.mapWindow[0] -= math.ceil (abs(min(px1,px2) - (self.mapWindow[0] - (self.size[0]-100)*self.zoom*aspectRatio))/10)
            if max(pz1,pz2) > (self.mapWindow[1] + (self.size[1]-100)*self.zoom):                                                       # and (self.mapWindow[1] + self.size[1]/2*self.zoom) < self.size[1] - self.height():
                self.mapWindow[1] += math.ceil(abs(max(pz1,pz2) - (self.mapWindow[1] + (self.size[1]-100)*self.zoom))/10)
            if min(pz1,pz2) < (self.mapWindow[1] - (self.size[1]-100)*self.zoom):                                                       # and (self.mapWindow[1] - self.size[1]/2*self.zoom) > self.height():
                self.mapWindow[1] -= math.ceil (abs(min(pz1,pz2) - (self.mapWindow[1] - (self.size[1]-100)*self.zoom))/10)
            self.zoom = temp
            painter.drawLine(int(px1), int(pz1),int( px2), int(pz2),)
            painter.end()

            if px1 < 0 or px2 < 0 or pz1 < 0 or pz2 < 0 or px1 > self.size[0] or px2 > self.size[0] or pz1 > self.size[1] or pz2 > self.size[1] :
                print("Outside:", px1, pz1, px2, pz2)
                if max(px1, px2) > self.size[0]:
                    self.size[0] *= 2
                    newLive = QPixmap(self.size[0], self.size[1])
                    cp = QPainter(newLive)
                    cp.drawPixmap(0,0, self.liveMap)
                    cp.end()
                    self.liveMap = newLive
                    newBase = QPixmap(self.size[0], self.size[1])
                    cp2 = QPainter(newBase)
                    cp2.drawPixmap(0,0, self.map)
                    cp2.end()
                    self.map = newBase
                if max(pz1, pz2) > self.size[1]:
                    self.size[1] *= 2
                    newLive = QPixmap(self.size[0], self.size[1])
                    cp = QPainter(newLive)
                    cp.drawPixmap(0,0, self.liveMap)
                    cp.end()
                    self.liveMap = newLive
                    newBase = QPixmap(self.size[0], self.size[1])
                    cp2 = QPainter(newBase)
                    cp2.drawPixmap(0,0, self.map)
                    cp2.end()
                    self.map = newBase
                    

        qp = QPainter()
        qp.begin(self)


        temp = self.zoom
        self.zoom=0.25
        #qp.drawPixmap(self.rect(), self.liveMap.copy(int(self.mapWindow[0] - aspectRatio * 1000*self.zoom), int(self.mapWindow[1]-1000*self.zoom), int(aspectRatio * self.zoom * 2000), int(self.zoom * 2000)).scaled(self.width(), self.height()))
        #qp.drawPixmap(self.rect(), self.liveMap.copy(0, 0, self.size[0], self.size[1]).scaled(self.width(), self.height()))
        #print(self.size, aspectRatio,self.size[1] - self.size[1]/aspectRatio)
        qp.drawPixmap(self.rect(), self.liveMap.copy(0, int((self.size[1] - self.size[1]/aspectRatio)/2), self.size[0], int(self.size[1]/aspectRatio)).scaled(self.width(), self.height()))
        self.zoom = temp

        qp.end()


class LineDeviation(QWidget):

    def __init__(self):
        super().__init__()
        self.maxDist = 3
        self.dist = 0
        self.invert = True
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
        a = self.abs(-z, 0, x)
        if a == 0:
            a = 1
        return (-z/a, 0, x/a)

    def setDistance(self, d):
        if self.invert:
            self.dist = -d
        else:
            self.dist = d

    def setPoints(self, p2, p1):
        self.p1 = p1
        self.p2 = p2
        if p1 is None or p2 is None:
            return
        a1 = self.abs(p1.velocity_x, p1.velocity_y, p1.velocity_z)
        a2 = self.abs(p2.velocity_x, p2.velocity_y, p2.velocity_z)

        # is the car standing still? TODO: maybe use orientation?
        if a1 == 0:
            a1 = 1
        if a2 == 0:
            a2 = 1

        self.angle1 = math.acos(p1.velocity_z / a1)
        if p1.velocity_x < 0:
            self.angle1 = 2*math.pi - self.angle1

        self.angle2 = math.acos(p2.velocity_z / a2)
        if p2.velocity_x < 0:
            self.angle2 = 2*math.pi - self.angle2

        self.angle = self.angle2-self.angle1

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
        clippedDist = min(self.maxDist, max(-self.maxDist, self.dist))
        if not self.p1 is None and not self.p2 is None:
            if self.dist < 0:
                self.redGradient.setStart(self.width()/2,0)
                self.redGradient.setFinalStop(self.width()/2 + clippedDist/self.maxDist * self.width() / 2, 0)
                qp.fillRect(int(self.width()/2), 0, int(clippedDist/self.maxDist * self.width() / 2), int(self.height()), self.redGradient)
                qp.drawLine(int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), int(self.height()))
            else:
                self.greenGradient.setStart(self.width()/2,0)
                self.greenGradient.setFinalStop(self.width()/2 + clippedDist/self.maxDist * self.width() / 2, 0)
                qp.fillRect(int(self.width()/2), 0, int(clippedDist/self.maxDist * self.width() / 2), int(self.height()), self.greenGradient)
                qp.drawLine(int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), int(self.height()))
        qp.drawLine(int(self.width()/2), 0, int(self.width()/2), int (self.height()))
        qp.end()



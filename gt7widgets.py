from PyQt6.QtCore import QSize, Qt, QTimer, QRegularExpression, QSettings
from PyQt6.QtGui import QColor, QRegularExpressionValidator, QPixmap, QPainter, QPalette, QPen, QLinearGradient, QGradient
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox, QGroupBox

class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GT7 SpeedBoard 1.0")
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

        self.lapDecimals = QCheckBox("Show decimals in lap displays (experimental)")
        self.recordingEnabled = QCheckBox("Allow recording data by pressing [R]")
        self.messagesEnabled = QCheckBox("Allow adding warning locations by pressing [space] (experimental)")
        self.linecomp = QCheckBox("Show racing line comparisons (experimental)")
        self.brakepoints = QCheckBox("Show brake points")
        self.countdownBrakepoint = QCheckBox("Count down to best brake points (experimental)")
        self.bigCountdownBrakepoint = QCheckBox("Hijack fuel box for countdown colors")
        self.allowLoop = QCheckBox("Allow looping telemetry from playback (experimental)")

        modeLabel = QLabel("Mode:")

        self.mode = QComboBox()
        self.mode.addItem("Laps")
        self.mode.addItem("Circuit Experience (experimental)")
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(modeLabel)
        mainLayout.addWidget(self.mode)

        vwGroup = QGroupBox("View")
        mainLayout.addWidget(vwGroup)
        vwLayout = QVBoxLayout()
        vwGroup.setLayout(vwLayout)
        vwLayout.addWidget(self.lapDecimals)

        recGroup = QGroupBox("Recording")
        mainLayout.addWidget(recGroup)
        recLayout = QVBoxLayout()
        recGroup.setLayout(recLayout)
        recLayout.addWidget(self.recordingEnabled)
        
        rlGroup = QGroupBox("Racing line")
        mainLayout.addWidget(rlGroup)
        rlLayout = QVBoxLayout()
        rlGroup.setLayout(rlLayout)
        rlLayout.addWidget(self.linecomp)
        rlLayout.addWidget(self.messagesEnabled)

        bpGroup = QGroupBox("Brake points")
        bpLayout = QVBoxLayout()
        bpGroup.setLayout(bpLayout)
        mainLayout.addWidget(bpGroup)
        bpLayout.addWidget(self.brakepoints)
        bpLayout.addWidget(self.countdownBrakepoint)
        bpLayout.addWidget(self.bigCountdownBrakepoint)
        
        netGroup = QGroupBox("Network")
        netLayout = QVBoxLayout()
        netGroup.setLayout(netLayout)
        mainLayout.addWidget(netGroup)
        netLayout.addWidget(self.allowLoop)

        fuGroup = QGroupBox("Fuel")
        fuLayout = QVBoxLayout()
        fuGroup.setLayout(fuLayout)
        mainLayout.addWidget(fuGroup)
        fuLayout.addWidget(fmLabel)
        fuLayout.addWidget(self.fuelMultiplier)
        fuLayout.addWidget(fcLabel)
        fuLayout.addWidget(self.maxFuelConsumption)
        fuLayout.addWidget(fwLabel)
        fuLayout.addWidget(self.fuelWarning)
        mainLayout.addWidget(addr)

        mainLayout.insertStretch(-1)

        print("Load preferences")
        settings = QSettings()#"./gt7speedboard.ini", QSettings.Format.IniFormat)
        self.ip.setText(settings.value("ip", ""))
        self.lapDecimals.setChecked(settings.value("lapDecimals") in [ True, "true"])
        self.recordingEnabled.setChecked(settings.value("recordingEnabled") in [ True, "true"])
        self.messagesEnabled.setChecked(settings.value("messagesEnabled") in [ True, "true"])
        self.linecomp.setChecked(settings.value("linecomp") in [ True, "true"])
        self.brakepoints.setChecked(settings.value("brakepoints") in [ True, "true"])
        self.allowLoop.setChecked(settings.value("allowLoop") in [True, "true"])
        self.countdownBrakepoint.setChecked(settings.value("countdownBrakepoint") in [True, "true"])
        self.bigCountdownBrakepoint.setChecked(settings.value("bigCountdownBrakepoint") in [True, "true"])
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
        if self.mapOffset is None:
            return
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
            if previousPoint.position_x - curPoint.position_x > 5 or previousPoint.position_z - curPoint.position_z > 5:
                continue
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




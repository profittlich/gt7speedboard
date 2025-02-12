from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import math
import copy
from sb.helpers import logPrint
import requests
import json
import glob
from pathlib import Path
import platform
import sys

shortcutText = "ESC \t return to configuration\n" \
             + "C \t clear lap data\n" \
             + "P\t Reset laps since pit stop counter\n"  \
             + "- \t Reduce number of laps by 1 (e.g. when being lapped)\n"  \
             + "+ \t Increase number of laps by 1\n"  \

class StartWindow(QWidget):
    def __init__(self, allowAutoUpdate):
        super().__init__()
        self.setWindowTitle("GT7 SpeedBoard 1.0")
        modeLabel = QLabel("Mode:")

        self.cbCheckUpdatesStart = QCheckBox("Automatically check for updates")

        pbCheckUpdates = QPushButton("Check for updates")
        pbCheckUpdates.setFlat(True)
        pal = pbCheckUpdates.palette()
        pal.setColor(pbCheckUpdates.foregroundRole(), QColor("#8af"))
        pbCheckUpdates.setPalette(pal)
        pbCheckUpdates.setCursor(Qt.CursorShape.PointingHandCursor)
        pbCheckUpdates.clicked.connect(self.checkUpdates)

        updateLayout = QHBoxLayout()
        updateLayout.setContentsMargins(0,0,0,0)
        firstRow = QWidget()
        firstRow.setLayout(updateLayout)

        self.mode = QComboBox()
        testPath = Path("./layouts")
        if testPath.is_dir():
            self.layoutPath = "./layouts"
        elif platform.system() == "Darwin":
            self.layoutPath = sys.argv[0][:sys.argv[0].rfind("/")] + "/../Resources/layouts"
        layoutFiles = glob.glob(self.layoutPath + '/*.sblayout')
        for f in layoutFiles:
            self.mode.addItem(f[f.rfind("/")+1:-9])
        updateLayout.addWidget(self.mode,10)
        updateLayout.addWidget(self.cbCheckUpdatesStart)
        updateLayout.addWidget(pbCheckUpdates,1,Qt.AlignmentFlag.AlignRight)
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(modeLabel)
        #mainLayout.addWidget(self.mode)
        mainLayout.addWidget(firstRow)

        tabWidget = QTabWidget()
        mainLayout.addWidget(tabWidget)

        # SPEED ASSISTS
        saGroup = QWidget()
        saLayout = QVBoxLayout()
        saGroup.setLayout(saLayout)
        tabWidget.addTab(saGroup, "Speed assists")
        self.cbOptimal = QCheckBox("Optimized lap (experimental)")

        self.optimizedSeedLabel = QLabel("Initialize optimized lap with:")
        self.optimizedSeed = QComboBox()
        self.optimizedSeed.addItem("Nothing")
        self.optimizedSeed.addItem("Reference lap A")
        self.optimizedSeed.addItem("Reference lap B")
        self.optimizedSeed.addItem("Reference lap C")

        self.comparisonLapLabel = QLabel("Show comparison laps:")
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
        self.speedcomp = QCheckBox("Show speed comparisons")
        self.timecomp = QCheckBox("Show graphical lap time comparisons")
        self.linecomp = QCheckBox("Show racing line comparisons")
        
        saLayout.addWidget(self.comparisonLapLabel)
        saLayout.addWidget(self.cbBest)
        saLayout.addWidget(self.cbMedian)
        saLayout.addWidget(self.cbRefA)
        saLayout.addWidget(self.cbRefB)
        saLayout.addWidget(self.cbRefC)
        saLayout.addWidget(self.cbLast)
        saLayout.addWidget(self.cbOptimal)
        saLayout.addWidget(self.optimizedSeedLabel)
        saLayout.addWidget(self.optimizedSeed)
        saLayout.addWidget(self.speedcomp)
        saLayout.addWidget(self.timecomp)
        saLayout.addWidget(self.linecomp)
        saLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


        # BRAKE POINTS
        bpGroup = QWidget()
        bpLayout = QVBoxLayout()
        bpGroup.setLayout(bpLayout)
        tabWidget.addTab(bpGroup, "Location assists")

        self.brakepoints = QCheckBox("Show brake points")
        self.throttlepoints = QCheckBox("Show throttle points")
        self.countdownBrakepoint = QCheckBox("Count down to brake points")
        self.bigCountdownBrakepoint = QLabel("Whole screen brake/throttle point colors for:")
        self.bigCountdownTarget = QComboBox()
        self.bigCountdownTarget.addItem("Nothing")
        self.bigCountdownTarget.addItem("Best lap")
        self.bigCountdownTarget.addItem("Reference lap A")
        self.bigCountdownTarget.addItem("Reference lap B")
        self.bigCountdownTarget.addItem("Reference lap C")
        self.bigCountdownTarget.addItem("Optimized lap")
        self.switchToBestLap = QCheckBox("Switch to best lap once it's faster")
        
        self.messagesEnabled = QCheckBox("Allow adding warning markers by pressing SPACE")
        
        self.cbCaution = QCheckBox("Use pre-loaded warning markers")
        self.cautionFile = ""

        bpLayout.addWidget(self.brakepoints)
        bpLayout.addWidget(self.throttlepoints)
        bpLayout.addWidget(self.countdownBrakepoint)
        bpLayout.addWidget(self.bigCountdownBrakepoint)
        bpLayout.addWidget(self.bigCountdownTarget)
        bpLayout.addWidget(self.switchToBestLap)
        bpLayout.addWidget(self.messagesEnabled)
        bpLayout.addWidget(self.cbCaution)
        bpLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # FUEL
        fuGroup = QWidget()
        fuLayout = QVBoxLayout()
        fuGroup.setLayout(fuLayout)
        tabWidget.addTab(fuGroup, "Fuel")

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
        fuLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # VIEW
        vwGroup = QWidget()
        vwLayout = QVBoxLayout()
        vwGroup.setLayout(vwLayout)
        vwGroup.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        tabWidget.addTab(vwGroup, "View")

        self.fontScale = QDoubleSpinBox()
        self.fontScale.setMinimum(0.1)
        self.fontScale.setMaximum(2)
        self.fontScale.setSingleStep(0.1)
        self.fontScale.setValue(1)

        self.lapDecimals = QCheckBox("Show decimals in lap displays")

        vwLayout.addWidget(QLabel("Font scale:"))
        vwLayout.addWidget(self.fontScale)
        vwLayout.addWidget(self.lapDecimals)
        vwLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # RECORDING
        recGroup = QWidget()
        recLayout = QVBoxLayout()
        recGroup.setLayout(recLayout)
        tabWidget.addTab(recGroup, "Recording")

        self.recordingEnabled = QCheckBox("Allow recording raw data by pressing R (not recommended)")
        self.sessionName = QLineEdit()
        self.saveSessionName = QCheckBox("Remember session name")
        pbChooseStorage = QPushButton("Choose storage location")
        self.lStorageLocation = QLabel()
        self.storageLocation = ""
        self.lStorageLocation.setText ("Storage location: " + self.storageLocation)
        pbChooseStorage.clicked.connect(self.chooseStorage)
        
        recLayout.addWidget(QLabel("Session name (optional):"))
        recLayout.addWidget(self.sessionName)
        recLayout.addWidget(self.saveSessionName)
        recLayout.addWidget(self.lStorageLocation)
        recLayout.addWidget(pbChooseStorage)
        recLayout.addWidget(self.recordingEnabled)
        recLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # SHORTCUTS
        ksGroup = QWidget()
        ksLayout = QVBoxLayout()
        ksGroup.setLayout(ksLayout)
        tabWidget.addTab(ksGroup, "Keyboard shortcuts")

        ksLayout.addWidget(QLabel(shortcutText))
        ksLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

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


        mainLayout.addWidget(addr)

        self.cbCheckUpdatesStart.stateChanged.connect(self.checkUpdatesAtStart)

        logPrint("Load preferences")
        settings = QSettings()#"./gt7speedboard.ini", QSettings.Format.IniFormat)
        self.mode.setCurrentIndex(int(settings.value("mode",0)))

        checkUpdVal = settings.value("checkUpdatesAtStart")
        logPrint(checkUpdVal)
        if checkUpdVal is None:
            result = QMessageBox.question(self, "Check updates", "Do you want automatically check for updates?")
            self.checkUpdatesAtStart(result == QMessageBox.StandardButton.Yes)

        storLoc = settings.value("storageLocation")
        if storLoc is None:
            QMessageBox.information(self, "Storage location", "You must choose a storage location for your data.")
            self.chooseStorage()

        self.cbCheckUpdatesStart.setChecked(settings.value("checkUpdatesAtStart", True) in [ True, "true"])
        self.optimizedSeed.setCurrentIndex(int(settings.value("optimizedSeed",0)))

        self.ip.setText(settings.value("ip", ""))
        self.storageLocation = settings.value("storageLocation", "")
        self.lStorageLocation.setText ("Storage location: " + self.storageLocation)

        self.fontScale.setValue(float(settings.value("fontScale",1)))
        self.lapDecimals.setChecked(settings.value("lapDecimals", True) in [ True, "true"])
        self.cbOptimal.setChecked(settings.value("showOptimalLap") in [ True, "true"])
        self.cbBest.setChecked(settings.value("showBestLap", True) in [ True, "true"])
        self.cbMedian.setChecked(settings.value("showMedianLap", True) in [ True, "true"])
        self.cbLast.setChecked(settings.value("showLastLap", True) in [ True, "true"])

        self.cbRefA.blockSignals(True)
        self.cbRefA.setChecked(settings.value("showRefALap") in [ True, "true"])
        self.cbRefA.blockSignals(False)
        self.cbRefB.blockSignals(True)
        self.cbRefB.setChecked(settings.value("showRefBLap") in [ True, "true"])
        self.cbRefB.blockSignals(False)
        self.cbRefC.blockSignals(True)
        self.cbRefC.setChecked(settings.value("showRefCLap") in [ True, "true"])
        self.cbRefC.blockSignals(False)
        if self.cbRefA.isChecked():
            self.refAFile = settings.value("refAFile", "")
            self.cbRefA.setText("Reference lap A: " + self.refAFile[self.refAFile.rfind("/")+1:])
        if self.cbRefB.isChecked():
            self.refBFile = settings.value("refBFile", "")
            self.cbRefB.setText("Reference lap B: " + self.refBFile[self.refBFile.rfind("/")+1:])
        if self.cbRefC.isChecked():
            self.refCFile = settings.value("refCFile", "")
            self.cbRefC.setText("Reference lap C: " + self.refCFile[self.refCFile.rfind("/")+1:])

        self.recordingEnabled.setChecked(settings.value("recordingEnabled") in [ True, "true"])
        self.messagesEnabled.setChecked(settings.value("messagesEnabled") in [ True, "true"])
        self.sessionName.setText(settings.value("sessionName", ""))
        self.saveSessionName.setChecked(settings.value("saveSessionName") in [ True, "true"])

        self.speedcomp.setChecked(settings.value("speedcomp", True) in [ True, "true"])
        self.linecomp.setChecked(settings.value("linecomp") in [ True, "true"])
        self.timecomp.setChecked(settings.value("timecomp", True) in [ True, "true"])
        self.cautionFile = settings.value("messageFile")
        self.cbCaution.setChecked(settings.value("loadMessagesFromFile") in [ True, "true"])
        if self.cbCaution.isChecked() and self.cautionFile != "":
            self.cbCaution.setText("Warning locations: " + self.cautionFile[self.cautionFile.rfind("/")+1:])
        elif self.cautionFile == "":
            self.cbCaution.setChecked(False)
        
        self.brakepoints.setChecked(settings.value("brakepoints") in [ True, "true"])
        self.throttlepoints.setChecked(settings.value("throttlepoints") in [ True, "true"])
        self.countdownBrakepoint.setChecked(settings.value("countdownBrakepoint", True) in [True, "true"])
        self.bigCountdownTarget.setCurrentIndex(int(settings.value("bigCountdownTarget",1)))
        self.switchToBestLap.setChecked(settings.value("switchToBestLap") in [ True, "true" ])

        self.fuelMultiplier.setValue(int(settings.value("fuelMultiplier", 1)))
        self.fuelWarning.setValue(int(settings.value("fuelWarning", 50)))
        self.maxFuelConsumption.setValue(int(settings.value("maxFuelConsumption", 150)))

        self.brakepoints.stateChanged.connect(self.brakePointWarning)
        self.throttlepoints.stateChanged.connect(self.brakePointWarning)
        self.linecomp.stateChanged.connect(self.racingLineWarning)
        self.cbCaution.stateChanged.connect(self.chooseCautionFile)
        self.mode.currentIndexChanged.connect(self.updateForMode)

        if allowAutoUpdate and self.cbCheckUpdatesStart.isChecked():
            self.checkUpdates(True)

        self.updateForMode()

    def updateForMode(self):
        logPrint("updateForMode")
        if "Circuit Experience" in self.mode.currentText():
            self.cbOptimal.setEnabled(False)
            self.optimizedSeed.setEnabled(False)
        else:
            self.cbOptimal.setEnabled(True)
            self.optimizedSeed.setEnabled(True)

    def checkUpdates(self, quiet = False):
        try:
            x = requests.get('https://api.github.com/repos/profittlich/gt7speedboard/releases/latest')
            j = json.loads(x.text)
            if j['tag_name'] == "v8":
                if not quiet:
                    QMessageBox.information(self, "Check updates", "You have the latest version.")
            else:
                result = QMessageBox.question(self, "Check updates", "There is a newer version:\n\n" + j['name'] + "\n\nDo you want to visit the download page?")
                if result == QMessageBox.StandardButton.Yes:
                    QDesktopServices.openUrl(QUrl(j['html_url']))
        except:
            QMessageBox.critical(self, "Check updates", "Unable to check for updates.\nTry again later.")

    def checkUpdatesAtStart(self, on):
        settings = QSettings()
        if on:
            settings.setValue("checkUpdatesAtStart", True)
        else:
            settings.setValue("checkUpdatesAtStart", False)
        settings.sync()


    def racingLineWarning(self, on):
        if on:
            QMessageBox.warning(self, "Please note", "Please be respectful about the rules of online races. Sometimes, racing line helpers are not allowed.")

    def brakePointWarning(self, on):
        if on:
            QMessageBox.warning(self, "Please note", "Please be respectful about the rules of online races. Sometimes, brake/throttle point helpers are not allowed.")

    def chooseStorage(self):
        chosen = QFileDialog.getExistingDirectory()
        if chosen == "":
            logPrint("None")
        else:
            self.storageLocation = chosen
            self.lStorageLocation.setText ("Storage location: " + self.storageLocation)
            settings = QSettings()
            settings.setValue("storageLocation", self.storageLocation)
            settings.sync()
            logPrint(chosen)

    def chooseReferenceLapA(self, on):
        if on:
            chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7; *.gt7lap; *.gt7laps)")
            if chosen[0] == "":
                logPrint("None")
                self.refAFile = ""
                self.cbRefA.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.refAFile = chosen[0]
                self.cbRefA.setText("Reference lap A: " + chosen[0][chosen[0].rfind("/")+1:])
        else:
            self.refAFile = ""
            self.cbRefA.setText("Reference lap A")

    def chooseReferenceLapB(self, on):
        if on:
            chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7; *.gt7lap; *.gt7laps)")
            if chosen[0] == "":
                logPrint("None")
                self.refBFile = ""
                self.cbRefB.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.refBFile = chosen[0]
                self.cbRefB.setText("Reference lap B: " + chosen[0][chosen[0].rfind("/")+1:])
        else:
            self.refBFile = ""
            self.cbRefB.setText("Reference lap B")

    def chooseReferenceLapC(self, on):
        if on:
            chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7; *.gt7lap; *.gt7laps)")
            if chosen[0] == "":
                logPrint("None")
                self.refCFile = ""
                self.cbRefC.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.refCFile = chosen[0]
                self.cbRefC.setText("Reference lap C: " + chosen[0][chosen[0].rfind("/")+1:])
        else:
            self.refCFile = ""
            self.cbRefC.setText("Reference lap C")

    def chooseCautionFile(self, on):
        if on:
            chosen = QFileDialog.getOpenFileName(filter="Location messages (*.sblm)")
            if chosen[0] == "":
                logPrint("None")
                self.cbCaution.setCheckState(Qt.CheckState.Unchecked)
            else:
                self.cautionFile = chosen[0]
                self.cbCaution.setText("Warning locations: " + chosen[0][chosen[0].rfind("/")+1:])
        else:
            self.cbCaution.setText("Use pre-loaded warning locations")


class ColorMainWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.color = QColor("#00000000")

    def setColor(self, c):
        if c != self.color:
            self.color = c
            self.update()

    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        qp.setPen(self.color)
        qp.setBrush(self.color)
        try:
            qp.drawRect(0,0, int(self.width()), int(self.height()))
        except OverflowError as e:
            logPrint(e)
        qp.end()
        super().paintEvent(event)

class ColorLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.color = QColor("#00000000")
        self.qp = QPainter()
        pal = self.palette()
        pal.setColor(self.foregroundRole(), QColor("#fff"))
        self.setPalette(pal)

    def __init__(self, t):
        super().__init__(t)
        self.color = QColor("#00000000")
        self.qp = QPainter()
        pal = self.palette()
        pal.setColor(self.foregroundRole(), QColor("#fff"))
        self.setPalette(pal)

    def setColor(self, c):
        if c != self.color:
            self.color = c
            self.update()

    def paintEvent(self, event):

        self.qp.begin(self)
        self.qp.setPen(self.color)
        self.qp.setBrush(self.color)
        try:
            self.qp.drawRect(0,0, int(self.width()), int(self.height()))
        except OverflowError as e:
            logPrint(e)
        self.qp.end()
        super().paintEvent(event)

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
            logPrint(e)
            logPrint(self.maxLevel, self.level)
        qp.end()


class MapView(QWidget):

    def __init__(self):
        super().__init__()
        self.clear()
        self.bulkRendering = False

    def setPoints(self, p1, p2, color = Qt.GlobalColor.red):
        self.previousPoints.append (p1)
        self.curPoints.append (p2)
        self.liveColor = color
        self.preparePaintEvent()

    def clear(self):
        self.size = [500, 500]
        self.liveMap = QPixmap(self.size[0], self.size[1])
        self.liveMap.fill(QColor("#000"))#Qt.GlobalColor.black)
        self.previousPoints = []
        self.curPoints = []
        self.mapOffset = None
        self.pixmapOffset = [ 250, 250 ]
        self.zoom = 1
        self.px2 = -20
        self.pz2 = -20
        self.debug = True

    def endLap(self):
        painter = QPainter(self.liveMap)
        brush = QBrush(QColor(0,0,0,96))
        painter.setBrush(brush)
        painter.drawRect(0,0,self.liveMap.width(), self.liveMap.height())

    def preparePaintEvent(self):
        while len (self.previousPoints) > 0  and len(self.curPoints) > 0:
            previousPoint = self.previousPoints.pop()
            curPoint = self.curPoints.pop()
            if abs(previousPoint.position_x - curPoint.position_x) > 5 or abs(previousPoint.position_z - curPoint.position_z) > 5:
                logPrint("Skip jump")
                continue

            if self.mapOffset is None:
                self.mapOffset = [ -curPoint.position_x, -curPoint.position_z ]
    
            px1 = (self.zoom * (previousPoint.position_x + self.mapOffset[0])) + self.pixmapOffset[0] 
            pz1 = (self.zoom * (previousPoint.position_z + self.mapOffset[1])) + self.pixmapOffset[1] 
            self.px2 = (self.zoom * (curPoint.position_x + self.mapOffset[0])) + self.pixmapOffset[0] 
            self.pz2 = (self.zoom * (curPoint.position_z + self.mapOffset[1]) + self.pixmapOffset[1])


            if self.px2 < 20:
                step = 10
                if self.px2 < 0:
                    step = -self.px2
                temp = self.liveMap.copy()
                step = int(math.ceil(step))
                self.liveMap = QPixmap(temp.width()+step, temp.height())
                self.liveMap.fill(QColor("#000"))
                painter = QPainter(self.liveMap)
                painter.drawPixmap(step, 0, temp.width(), temp.height(), temp)
                painter.end()
                self.pixmapOffset[0] += step

            if self.pz2 < 20:
                step = 10
                if self.pz2 < 0:
                    step = -self.pz2
                temp = self.liveMap.copy()
                step = int(math.ceil(step))
                self.liveMap = QPixmap(temp.width(), temp.height()+step)
                self.liveMap.fill(QColor("#000"))
                painter = QPainter(self.liveMap)
                painter.drawPixmap(0, step, temp.width(), temp.height(), temp)
                painter.end()
                self.pixmapOffset[1] += step

            if self.px2 >= self.liveMap.width()-20:
                step = 10
                if self.px2 >= self.liveMap.width():
                    step = math.ceil(self.px2) - self.liveMap.width()
                temp = self.liveMap.copy()
                self.liveMap = QPixmap(temp.width()+step, temp.height())
                self.liveMap.fill(QColor("#000"))
                painter = QPainter(self.liveMap)
                brush = QBrush(QColor(0,0,0))
                painter.drawPixmap(0, 0, temp.width(), temp.height(), temp)
                painter.end()

            if self.pz2 >= self.liveMap.height()-20:
                step = 10
                if self.pz2 >= self.liveMap.height():
                    step = math.ceil(self.pz2) - self.liveMap.height()
                temp = self.liveMap.copy()
                self.liveMap = QPixmap(temp.width(), temp.height()+step)
                self.liveMap.fill(QColor("#000"))
                painter = QPainter(self.liveMap)
                painter.drawPixmap(0, 0, temp.width(), temp.height(), temp)
                painter.end()

            px1 = (self.zoom * (previousPoint.position_x + self.mapOffset[0])) + self.pixmapOffset[0] 
            pz1 = (self.zoom * (previousPoint.position_z + self.mapOffset[1])) + self.pixmapOffset[1] 
            self.px2 = (self.zoom * (curPoint.position_x + self.mapOffset[0])) + self.pixmapOffset[0] 
            self.pz2 = (self.zoom * (curPoint.position_z + self.mapOffset[1]) + self.pixmapOffset[1])

            if self.debug:
                self.debug = False

            painter = QPainter(self.liveMap)
            brush = QBrush(QColor(0,0,0))
            painter.setBrush(brush)
            pen = QPen(QColor(0,0,0))
            painter.setPen(pen)

            pen = QPen(self.liveColor)
            pen.setWidth(5)
            painter.setPen(pen)
            
            painter.drawLine(int(px1), int(pz1), int(self.px2), int(self.pz2))
            painter.end()


    def paintEvent(self, event):
        if self.bulkRendering:
            return
        aspectRatio = self.width()/self.height()
        baseAspectRatio = self.liveMap.width() / self.liveMap.height()
        qp = QPainter()
        qp.begin(self)
        qp.fillRect(self.rect(), QColor("#222"))
        qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_Lighten)


        stretch = aspectRatio / baseAspectRatio
        if aspectRatio < baseAspectRatio:
            qp.drawPixmap(0, int((self.height() - stretch * self.height())/2), self.width(), int(stretch * self.height()), self.liveMap)
            qp.drawEllipse(int(self.px2 * self.width() / self.liveMap.width()) - 8, int(self.pz2 * self.height() / self.liveMap.height() * stretch + (self.height() - stretch * self.height())/2) - 8, 16, 16)
        else:
            qp.drawPixmap(int((self.width() - (1/stretch) * self.width())/2), 0, int((1/stretch) * self.width()), self.height(), self.liveMap)
            qp.drawEllipse(int(self.px2 * self.width() / self.liveMap.width() / stretch - 8 + (self.width() - (1/stretch) * self.width())/2), int(self.pz2 * self.height() / self.liveMap.height()) - 8, 16, 16)

        qp.end()


class PedalWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.maxDist = 100
        self.distr = 0
        self.distl = 0
        self.vr = None
        self.vl = None
        self.redGradient = QLinearGradient (10,0,120,0);
        self.redGradient.setColorAt(0.0, QColor("#222"))
        self.redGradient.setColorAt(0.2, QColor("#222"))
        self.redGradient.setColorAt(1.0, Qt.GlobalColor.red);
        self.greenGradient = QLinearGradient (10,0,120,0);
        self.greenGradient.setColorAt(0.0, QColor("#222"))
        self.greenGradient.setColorAt(0.2, QColor("#222"))
        self.greenGradient.setColorAt(1.0, Qt.GlobalColor.green);

    def setDistance(self, dl, dr):
        self.distr = dr
        self.distl = dl

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
        clippedDistL = -min(self.maxDist, max(-self.maxDist, self.distl))
        clippedDistR = min(self.maxDist, max(-self.maxDist, self.distr))

        self.redGradient.setStart(self.width()/2,0)
        self.redGradient.setFinalStop(self.width()/2 + clippedDistL/self.maxDist * self.width() / 2, 0)
        if clippedDistL == -100:
            qp.fillRect(int(self.width()/2), 0, int(clippedDistL/self.maxDist * self.width() / 2), int(self.height()), Qt.GlobalColor.red)
        else:
            qp.fillRect(int(self.width()/2), 0, int(clippedDistL/self.maxDist * self.width() / 2), int(self.height()), self.redGradient)
        qp.drawLine(int(self.width()/2) + int(clippedDistL/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(clippedDistL/self.maxDist * self.width() / 2), int(self.height()))

        self.greenGradient.setStart(self.width()/2,0)
        self.greenGradient.setFinalStop(self.width()/2 + clippedDistR/self.maxDist * self.width() / 2, 0)
        if clippedDistR == 100:
            qp.fillRect(int(self.width()/2), 0, int(clippedDistR/self.maxDist * self.width() / 2), int(self.height()), Qt.GlobalColor.green)
        else:
            qp.fillRect(int(self.width()/2), 0, int(clippedDistR/self.maxDist * self.width() / 2), int(self.height()), self.greenGradient)
        qp.drawLine(int(self.width()/2) + int(clippedDistR/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(clippedDistR/self.maxDist * self.width() / 2), int(self.height()))

        qp.drawLine(int(self.width()/2), 0, int(self.width()/2), int (self.height()))
        qp.end()

class LineDeviation(QWidget):

    def __init__(self, maxDist = 3, colorScaleMode = 0, greenRange = 0.1, yellowRange = 0.3):
        super().__init__()
        self.maxDist = maxDist
        self.dist = 0
        self.invert = True
        self.p1 = None
        self.p2 = None
        self.colorScaleMode = colorScaleMode
        self.greenRange = greenRange
        self.yellowRange = yellowRange
        self.redGradient = QLinearGradient (10,0,120,0);
        self.redGradient.setColorAt(0.0, QColor("#222"))
        self.redGradient.setColorAt(0.2, QColor("#222"))
        self.redGradient.setColorAt(1.0, Qt.GlobalColor.red);
        self.yellowGradient = QLinearGradient (10,0,120,0);
        self.yellowGradient.setColorAt(0.0, QColor("#222"))
        self.yellowGradient.setColorAt(0.2, QColor("#222"))
        self.yellowGradient.setColorAt(1.0, Qt.GlobalColor.yellow);
        self.greenGradient = QLinearGradient (10,0,120,0);
        self.greenGradient.setColorAt(0.0, QColor("#222"))
        self.greenGradient.setColorAt(0.2, QColor("#222"))
        self.greenGradient.setColorAt(1.0, Qt.GlobalColor.green);

    def setColorScaleMode (self, m, greenRange = None, yellowRange = None):
        self.colorScaleMode = m
        if not greenRange is None:
            self.greenRange = greenRange
        if not yellowRange is None:
            self.yellowRange = yellowRange

    def setMaxDeviation(self, d):
        self.maxDist = d

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
        if self.colorScaleMode == 0:
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
        elif self.colorScaleMode == 1:
            if abs(self.dist) <= self.greenRange:
                curGradient = self.greenGradient
            elif abs(self.dist) <= self.yellowRange:
                curGradient = self.yellowGradient
            else:
                curGradient = self.redGradient

            if self.dist < 0:
                curGradient.setStart(self.width()/2,0)
                curGradient.setFinalStop(self.width()/2 + clippedDist/self.maxDist * self.width() / 2, 0)
                qp.fillRect(int(self.width()/2), 0, int(clippedDist/self.maxDist * self.width() / 2), int(self.height()), curGradient)
                qp.drawLine(int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), int(self.height()))
            else:
                curGradient.setStart(self.width()/2,0)
                curGradient.setFinalStop(self.width()/2 + clippedDist/self.maxDist * self.width() / 2, 0)
                qp.fillRect(int(self.width()/2), 0, int(clippedDist/self.maxDist * self.width() / 2), int(self.height()), curGradient)
                qp.drawLine(int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), 0, int(self.width()/2) + int(clippedDist/self.maxDist * self.width() / 2), int(self.height()))
        qp.drawLine(int(self.width()/2), 0, int(self.width()/2), int (self.height()))
        qp.end()



class TimeDeviation(QWidget):

    def __init__(self):
        super().__init__()
        self.maxDiff = 1.0 * 59.94
        self.additionalDiffFactor = 4
        self.difference = 0
        self.redGradient = QLinearGradient (0, 10,0,120);
        self.redGradient.setColorAt(0.0, QColor("#222"))
        self.redGradient.setColorAt(0.2, QColor("#222"))
        self.redGradient.setColorAt(1.0, Qt.GlobalColor.red);
        self.greenGradient = QLinearGradient (0, 10,0,120);
        self.greenGradient.setColorAt(0.0, QColor("#222"))
        self.greenGradient.setColorAt(0.2, QColor("#222"))
        self.greenGradient.setColorAt(1.0, Qt.GlobalColor.green);

    def setDiff(self, d):
        self.difference = -d

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
        clippedDifference = min(self.maxDiff, max(-self.maxDiff, self.difference))
        lineLen = self.width()
        if self.difference > 0:
            self.redGradient.setStart(0, self.height()/2)
            self.redGradient.setFinalStop(0, self.height()/2 + clippedDifference/self.maxDiff * self.height() / 2)
            qp.fillRect(0, int(self.height()/2), int(self.width()), int(clippedDifference/self.maxDiff * self.height() / 2), self.redGradient)
            lineLen = max(0, min(lineLen, lineLen * (1-(self.difference - self.maxDiff) / (self.additionalDiffFactor * self.maxDiff))))
        else:
            self.greenGradient.setStart(0, self.height()/2)
            self.greenGradient.setFinalStop(0, self.height()/2 + clippedDifference/self.maxDiff * self.height() / 2)
            qp.fillRect(0, int(self.height()/2), int(self.width()), int(clippedDifference/self.maxDiff * self.height() / 2), self.greenGradient)
            lineLen = max(0, min(lineLen, lineLen * (1-(-self.difference - self.maxDiff) / (self.additionalDiffFactor * self.maxDiff))))
        lineLen = int(lineLen)
        if lineLen < self.width():
            pen = QPen(QColor(0, 0, 0, 92))
            pen.setWidth(5)
            qp.setPen(pen)
            qp.drawLine(0, int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2), int(self.width()), int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2))
            qp.drawLine(0, int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2), int(self.width()/4), int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2))
            qp.drawLine(int(self.width()/2), int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2), int(3*self.width()/4), int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2))
            pen = QPen(Qt.GlobalColor.white)
            pen.setWidth(5)
            qp.setPen(pen)
        qp.drawLine(0, int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2), lineLen, int(self.height()/2) + int(clippedDifference/self.maxDiff * self.height() / 2))
        qp.drawLine(0, int(self.height()/2), int (self.width()), int(self.height()/2))
        qp.end()




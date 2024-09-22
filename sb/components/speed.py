from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint
from sb.helpers import indexToTime, msToTime

class Speed(sb.component.Component):
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

        self.pedalBest = QLabel("")
        self.pedalBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalBest.setAutoFillBackground(True)
        font = self.pedalBest.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalBest.setFont(font)
        pal = self.pedalBest.palette()
        pal.setColor(self.pedalBest.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.pedalBest.foregroundRole(), self.cfg.foregroundColor)
        self.pedalBest.setPalette(pal)

        self.speedBest = QLabel("BEST")
        self.speedBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedBest.setAutoFillBackground(True)
        font = self.speedBest.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedBest.setFont(font)
        pal = self.speedBest.palette()
        pal.setColor(self.speedBest.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.speedBest.foregroundRole(), self.cfg.foregroundColor)
        self.speedBest.setPalette(pal)

        self.lineBest = LineDeviation()
        self.timeDiffBest = TimeDeviation()

        self.pedalLast = QLabel("")
        self.pedalLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalLast.setAutoFillBackground(True)
        font = self.pedalLast.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalLast.setFont(font)
        pal = self.pedalLast.palette()
        pal.setColor(self.pedalLast.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.pedalLast.foregroundRole(), self.cfg.foregroundColor)
        self.pedalLast.setPalette(pal)

        self.speedLast = QLabel("LAST")
        self.speedLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLast.setAutoFillBackground(True)
        font = self.speedLast.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedLast.setFont(font)
        pal = self.speedLast.palette()
        pal.setColor(self.speedLast.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.speedLast.foregroundRole(), self.cfg.foregroundColor)
        self.speedLast.setPalette(pal)

        self.lineLast = LineDeviation()
        self.timeDiffLast = TimeDeviation()

        self.pedalRefA = QLabel("")
        self.pedalRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefA.setAutoFillBackground(True)
        font = self.pedalRefA.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalRefA.setFont(font)
        pal = self.pedalRefA.palette()
        pal.setColor(self.pedalRefA.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.pedalRefA.foregroundRole(), self.cfg.foregroundColor)
        self.pedalRefA.setPalette(pal)

        self.speedRefA = QLabel("REF A")
        self.speedRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefA.setAutoFillBackground(True)
        font = self.speedRefA.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedRefA.setFont(font)
        pal = self.speedRefA.palette()
        pal.setColor(self.speedRefA.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.speedRefA.foregroundRole(), self.cfg.foregroundColor)
        self.speedRefA.setPalette(pal)

        self.lineRefA = LineDeviation()
        self.timeDiffRefA = TimeDeviation()

        self.pedalRefB = QLabel("")
        self.pedalRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefB.setAutoFillBackground(True)
        font = self.pedalRefB.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalRefB.setFont(font)
        pal = self.pedalRefB.palette()
        pal.setColor(self.pedalRefB.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.pedalRefB.foregroundRole(), self.cfg.foregroundColor)
        self.pedalRefB.setPalette(pal)

        self.speedRefB = QLabel("REF B")
        self.speedRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefB.setAutoFillBackground(True)
        font = self.speedRefB.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedRefB.setFont(font)
        pal = self.speedRefB.palette()
        pal.setColor(self.speedRefB.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.speedRefB.foregroundRole(), self.cfg.foregroundColor)
        self.speedRefB.setPalette(pal)

        self.lineRefB = LineDeviation()
        self.timeDiffRefB = TimeDeviation()

        self.pedalRefC = QLabel("")
        self.pedalRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefC.setAutoFillBackground(True)
        font = self.pedalRefC.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalRefC.setFont(font)
        pal = self.pedalRefC.palette()
        pal.setColor(self.pedalRefC.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.pedalRefC.foregroundRole(), self.cfg.foregroundColor)
        self.pedalRefC.setPalette(pal)

        self.speedRefC = QLabel("REF C")
        self.speedRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefC.setAutoFillBackground(True)
        font = self.speedRefC.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedRefC.setFont(font)
        pal = self.speedRefC.palette()
        pal.setColor(self.speedRefC.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.speedRefC.foregroundRole(), self.cfg.foregroundColor)
        self.speedRefC.setPalette(pal)

        self.lineRefC = LineDeviation()
        self.timeDiffRefC = TimeDeviation()

        self.pedalMedian = QLabel("")
        self.pedalMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalMedian.setAutoFillBackground(True)
        font = self.pedalMedian.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalMedian.setFont(font)
        pal = self.pedalMedian.palette()
        pal.setColor(self.pedalMedian.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.pedalMedian.foregroundRole(), self.cfg.foregroundColor)
        self.pedalMedian.setPalette(pal)

        self.speedMedian = QLabel("MEDIAN")
        self.speedMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedMedian.setAutoFillBackground(True)
        font = self.speedMedian.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedMedian.setFont(font)
        pal = self.speedMedian.palette()
        pal.setColor(self.speedMedian.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.speedMedian.foregroundRole(), self.cfg.foregroundColor)
        self.speedMedian.setPalette(pal)

        self.lineMedian = LineDeviation()
        self.timeDiffMedian = TimeDeviation()

        self.pedalOptimized = QLabel("")
        self.pedalOptimized.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalOptimized.setAutoFillBackground(True)
        font = self.pedalOptimized.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalOptimized.setFont(font)
        pal = self.pedalOptimized.palette()
        pal.setColor(self.pedalOptimized.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.pedalOptimized.foregroundRole(), self.cfg.foregroundColor)
        self.pedalOptimized.setPalette(pal)

        self.speedOptimized = QLabel("OPT")
        self.speedOptimized.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedOptimized.setAutoFillBackground(True)
        font = self.speedOptimized.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedOptimized.setFont(font)
        pal = self.speedOptimized.palette()
        pal.setColor(self.speedOptimized.backgroundRole(), self.cfg.backgroundColor)
        pal.setColor(self.speedOptimized.foregroundRole(), self.cfg.foregroundColor)
        self.speedOptimized.setPalette(pal)

        self.lineOptimized = LineDeviation()
        self.timeDiffOptimized = TimeDeviation()


        self.speedWidget = QWidget()
        speedLayout = QGridLayout()
        self.speedWidget.setLayout(speedLayout)
        if self.cfg.showBestLap:
            speedLayout.addWidget(self.speedBest, 2, 0)
        if self.cfg.showMedianLap:
            speedLayout.addWidget(self.speedMedian, 2, 1)
        if self.cfg.showRefALap:
            speedLayout.addWidget(self.speedRefA, 2, 2)
        if self.cfg.showRefBLap:
            speedLayout.addWidget(self.speedRefB, 2, 3)
        if self.cfg.showRefCLap:
            speedLayout.addWidget(self.speedRefC , 2, 4)
        if self.cfg.showLastLap:
            speedLayout.addWidget(self.speedLast, 2, 5)
        if self.cfg.showOptimalLap:
            speedLayout.addWidget(self.speedOptimized, 2, 6)

        if self.cfg.linecomp:
            if self.cfg.showBestLap:
                speedLayout.addWidget(self.lineBest, 1, 0)
            if self.cfg.showMedianLap:
                speedLayout.addWidget(self.lineMedian, 1, 1)
            if self.cfg.showRefALap:
                speedLayout.addWidget(self.lineRefA, 1, 2)
            if self.cfg.showRefBLap:
                speedLayout.addWidget(self.lineRefB, 1, 3)
            if self.cfg.showRefCLap:
                speedLayout.addWidget(self.lineRefC, 1, 4)
            if self.cfg.showLastLap:
                speedLayout.addWidget(self.lineLast, 1, 5)
            if self.cfg.showOptimalLap:
                speedLayout.addWidget(self.lineOptimized, 1, 6)
            speedLayout.setRowStretch(1, 1)
        if self.cfg.timecomp:
            speedLayout.setRowStretch(3, 6)
            if self.cfg.showBestLap:
                speedLayout.addWidget(self.timeDiffBest, 3, 0)
            if self.cfg.showMedianLap:
                speedLayout.addWidget(self.timeDiffMedian, 3, 1)
            if self.cfg.showRefALap:
                speedLayout.addWidget(self.timeDiffRefA, 3, 2)
            if self.cfg.showRefBLap:
                speedLayout.addWidget(self.timeDiffRefB, 3, 3)
            if self.cfg.showRefCLap:
                speedLayout.addWidget(self.timeDiffRefC, 3, 4)
            if self.cfg.showLastLap:
                speedLayout.addWidget(self.timeDiffLast, 3, 5)
            if self.cfg.showOptimalLap:
                speedLayout.addWidget(self.timeDiffOptimized, 3, 6)

        if self.cfg.brakepoints or self.cfg.throttlepoints:
            if self.cfg.showBestLap:
                speedLayout.addWidget(self.pedalBest, 0, 0)
            if self.cfg.showMedianLap:
                speedLayout.addWidget(self.pedalMedian, 0, 1)
            if self.cfg.showRefALap:
                speedLayout.addWidget(self.pedalRefA, 0, 2)
            if self.cfg.showRefBLap:
                speedLayout.addWidget(self.pedalRefB, 0, 3)
            if self.cfg.showRefCLap:
                speedLayout.addWidget(self.pedalRefC, 0, 4)
            if self.cfg.showLastLap:
                speedLayout.addWidget(self.pedalLast, 0, 5)
            if self.cfg.showOptimalLap:
                speedLayout.addWidget(self.pedalOptimized, 0, 6)
            speedLayout.setRowStretch(0, 1)
        speedLayout.setRowStretch(2, 4)

        self.markBigCountdownField()

    def updateSpeed(self, curPoint):
        class SpeedData:
            def __init__(self):
                self.closestPoint = None
                self.closestOffsetPoint = None
                self.nextBrake = None
                self.closestIndex = None
                self.speedWidget = None
                self.pedalWidget = None
                self.lineWidget = None
                self.timeDiffWidget = None
                self.id = None

        best = SpeedData()
        best.closestIndex = self.data.closestIBest
        best.closestPoint = self.data.closestPointBest
        best.closestOffsetPoint = self.data.closestOffsetPointBest
        best.speedWidget = self.speedBest
        best.pedalWidget = self.pedalBest
        best.lineWidget = self.lineBest
        best.timeDiffWidget = self.timeDiffBest
        best.id = 1
             
        median = SpeedData()
        median.closestIndex = self.data.closestIMedian
        median.closestPoint = self.data.closestPointMedian
        median.closestOffsetPoint = self.data.closestOffsetPointMedian
        median.speedWidget = self.speedMedian
        median.pedalWidget = self.pedalMedian
        median.lineWidget = self.lineMedian
        median.timeDiffWidget = self.timeDiffMedian
        median.id = 101
             
        last = SpeedData()
        last.closestIndex = self.data.closestILast
        last.closestPoint = self.data.closestPointLast
        last.closestOffsetPoint = self.data.closestOffsetPointLast
        last.speedWidget = self.speedLast
        last.pedalWidget = self.pedalLast
        last.lineWidget = self.lineLast
        last.timeDiffWidget = self.timeDiffLast
        last.id = 102

        refA = SpeedData()
        refA.closestIndex = self.data.closestIRefA
        refA.closestPoint = self.data.closestPointRefA
        refA.closestOffsetPoint = self.data.closestOffsetPointRefA
        refA.speedWidget = self.speedRefA
        refA.pedalWidget = self.pedalRefA
        refA.lineWidget = self.lineRefA
        refA.timeDiffWidget = self.timeDiffRefA
        refA.id = 2

        refB = SpeedData()
        refB.closestIndex = self.data.closestIRefB
        refB.closestPoint = self.data.closestPointRefB
        refB.closestOffsetPoint = self.data.closestOffsetPointRefB
        refB.speedWidget = self.speedRefB
        refB.pedalWidget = self.pedalRefB
        refB.lineWidget = self.lineRefB
        refB.timeDiffWidget = self.timeDiffRefB
        refB.id = 3
             
        refC = SpeedData()
        refC.closestIndex = self.data.closestIRefC
        refC.closestPoint = self.data.closestPointRefC
        refC.closestOffsetPoint = self.data.closestOffsetPointRefC
        refC.speedWidget = self.speedRefC
        refC.pedalWidget = self.pedalRefC
        refC.lineWidget = self.lineRefC
        refC.timeDiffWidget = self.timeDiffRefC
        refC.id = 4
             
        opti = SpeedData()
        opti.closestIndex = self.data.closestIOptimized
        opti.closestPoint = self.data.closestPointOptimized
        opti.closestOffsetPoint = self.data.closestOffsetPointOptimized
        opti.speedWidget = self.speedOptimized
        opti.pedalWidget = self.pedalOptimized
        opti.lineWidget = self.lineOptimized
        opti.timeDiffWidget = self.timeDiffOptimized
        opti.id = 5
             
        refA.nextBrake = self.data.findNextBrake(self.data.refLaps[0].points, refA.closestIndex) # TODO refactor
        refB.nextBrake = self.data.findNextBrake(self.data.refLaps[1].points, refB.closestIndex)
        refC.nextBrake = self.data.findNextBrake(self.data.refLaps[2].points, refC.closestIndex)
        opti.nextBrake = self.data.findNextBrake(self.data.optimizedLap.points, opti.closestIndex)

        if len(self.data.previousLaps) > 0 and self.data.previousLaps[self.data.bestLap].valid:
            best.nextBrake = self.data.findNextBrake(self.data.previousLaps[self.data.bestLap].points, best.closestIndex)

        pal = self.data.palette()
        pal.setColor(self.pedalBest.backgroundRole(), self.cfg.brightBackgroundColor)
        self.data.setPalette(pal)

        self.updateOneSpeedEntry(last, curPoint)
        self.updateOneSpeedEntry(refA, curPoint)
        self.updateOneSpeedEntry(refB, curPoint)
        self.updateOneSpeedEntry(refC, curPoint)
        self.updateOneSpeedEntry(best, curPoint)
        self.updateOneSpeedEntry(median, curPoint)
        self.updateOneSpeedEntry(opti, curPoint)

    def updateOneSpeedEntry(self, refLap, curPoint):
        bgPal = self.speedWidget.palette()
        bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.brightBackgroundColor)

        if not refLap.closestPoint is None:
            # SPEED
            speedDiff = refLap.closestPoint.car_speed - curPoint.car_speed
            pal = refLap.speedWidget.palette()
            pal.setColor(refLap.speedWidget.backgroundRole(), self.speedDiffQColor(speedDiff))
            refLap.speedWidget.setPalette(pal)

            # BRAKE POINTS
            if self.cfg.throttlepoints or self.cfg.brakepoints:
                refLap.pedalWidget.setText("")
                pal = refLap.pedalWidget.palette()
                pal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.backgroundColor)

            if self.cfg.throttlepoints:
                if refLap.closestOffsetPoint.throttle > 98:
                    refLap.pedalWidget.setText("GAS")
                    pal.setColor(refLap.pedalWidget.backgroundRole(), QColor("#f2f"))
                    if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                        bgPal.setColor(refLap.pedalWidget.backgroundRole(), QColor("#626"))

            if self.cfg.brakepoints:
                if refLap.closestOffsetPoint.brake > 0:
                    refLap.pedalWidget.setText("BRAKE")
                    pal.setColor(refLap.pedalWidget.backgroundRole(), self.brakeQColor(refLap.closestOffsetPoint.brake))
                    if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                        bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.brakeQColor(refLap.closestOffsetPoint.brake))

                elif self.cfg.countdownBrakepoint and not refLap.nextBrake is None:
                    refLap.pedalWidget.setText(str(math.ceil (refLap.nextBrake/60)))
                    if refLap.nextBrake >= 120:
                        if refLap.nextBrake%60 >= 30:
                            pal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.countdownColor3)
                            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                                bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.countdownColor3)
                    elif refLap.nextBrake >= 60:
                        if refLap.nextBrake%60 >= 30:
                            pal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.countdownColor2)
                            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                                bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.countdownColor2)
                    else:
                        if refLap.nextBrake%30 >= 15:
                            pal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.countdownColor1)
                            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                                bgPal.setColor(refLap.pedalWidget.backgroundRole(), self.cfg.countdownColor1)

            refLap.pedalWidget.setPalette(pal)
            refLap.lineWidget.setPoints(curPoint, refLap.closestPoint)
            refLap.lineWidget.update()

            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                self.data.setPalette(bgPal)

            # TIME DIFF
            refLap.timeDiffWidget.setDiff(refLap.closestIndex - len(self.data.curLap.points))
            refLap.timeDiffWidget.update()
        else:
            pal = refLap.speedWidget.palette()
            pal.setColor(refLap.speedWidget.backgroundRole(), self.cfg.backgroundColor)
            refLap.speedWidget.setPalette(pal)
            refLap.pedalWidget.setPalette(pal)
            refLap.pedalWidget.setText("")
            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                self.data.setPalette(bgPal)
            refLap.timeDiffWidget.setDiff(0)
            refLap.timeDiffWidget.update()

    def getWidget(self):
        return self.speedWidget

    def speedDiffQColor(self, d):
        col = QColor()
        hue = self.cfg.speedDiffCenterHue - d/(self.cfg.speedDiffSpread/self.cfg.speedDiffCenterHue) 
        if hue < self.cfg.speedDiffMinHue:
            hue = self.cfg.speedDiffMinHue
        if hue > self.cfg.speedDiffMaxHue:
            hue = self.cfg.speedDiffMaxHue
        col.setHsvF (hue, self.cfg.speedDiffColorSaturation, self.cfg.speedDiffColorValue)

        return col

    def brakeQColor(self, d):
        col = QColor()
        col.setHsvF (self.cfg.brakeColorHue, self.cfg.brakeColorSaturation, self.cfg.brakeColorMinValue + d * (1 - self.cfg.brakeColorMinValue)/100)

        return col


    def addPoint(self, curPoint, curLap):
        self.updateSpeed(curPoint)

    def initRace(self):
        pal = self.pedalLast.palette()
        self.pedalLast.setText("")
        pal.setColor(self.pedalLast.backgroundRole(), self.cfg.backgroundColor)
        self.pedalLast.setPalette(pal)

        pal = self.pedalBest.palette()
        self.pedalBest.setText("")
        pal.setColor(self.pedalBest.backgroundRole(), self.cfg.backgroundColor)
        self.pedalBest.setPalette(pal)

        pal = self.pedalMedian.palette()
        self.pedalMedian.setText("")
        pal.setColor(self.pedalMedian.backgroundRole(), self.cfg.backgroundColor)
        self.pedalMedian.setPalette(pal)

        pal = self.pedalRefA.palette()
        self.pedalRefA.setText("")
        pal.setColor(self.pedalRefA.backgroundRole(), self.cfg.backgroundColor)
        self.pedalRefA.setPalette(pal)

        pal = self.pedalRefB.palette()
        self.pedalRefB.setText("")
        pal.setColor(self.pedalRefB.backgroundRole(), self.cfg.backgroundColor)
        self.pedalRefB.setPalette(pal)

        pal = self.pedalRefC.palette()
        self.pedalRefC.setText("")
        pal.setColor(self.pedalRefC.backgroundRole(), self.cfg.backgroundColor)
        self.pedalRefC.setPalette(pal)

        pal = self.pedalOptimized.palette()
        self.pedalOptimized.setText("")
        pal.setColor(self.pedalOptimized.backgroundRole(), self.cfg.backgroundColor)
        self.pedalOptimized.setPalette(pal)

        self.lineBest.setPoints(None,None)
        self.lineBest.update()

        self.timeDiffBest.setDiff(0)
        self.timeDiffBest.update()

        self.lineLast.setPoints(None,None)
        self.lineLast.update()

        self.timeDiffLast.setDiff(0)
        self.timeDiffLast.update()

        self.lineMedian.setPoints(None,None)
        self.lineMedian.update()

        self.timeDiffMedian.setDiff(0)
        self.timeDiffMedian.update()

        self.lineRefA.setPoints(None,None)
        self.lineRefA.update()

        self.timeDiffRefA.setDiff(0)
        self.timeDiffRefA.update()

        self.lineRefB.setPoints(None,None)
        self.lineRefB.update()

        self.timeDiffRefB.setDiff(0)
        self.timeDiffRefB.update()

        self.lineRefC.setPoints(None,None)
        self.lineRefC.update()

        self.timeDiffRefC.setDiff(0)
        self.timeDiffRefC.update()

        self.lineOptimized.setPoints(None,None)
        self.lineOptimized.update()

        self.timeDiffOptimized.setDiff(0)
        self.timeDiffOptimized.update()

    def markBigCountdownField(self):
        itBest = self.data.bigCountdownBrakepoint == 1
        itRefA = self.data.bigCountdownBrakepoint == 2
        itRefB = self.data.bigCountdownBrakepoint == 3
        itRefC = self.data.bigCountdownBrakepoint == 4
        itOptimized = self.data.bigCountdownBrakepoint == 5

        font = self.speedBest.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setUnderline(itBest)
        self.speedBest.setFont(font)

        font = self.speedRefA.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setUnderline(itRefA)
        self.speedRefA.setFont(font)

        font = self.speedRefB.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setUnderline(itRefB)
        self.speedRefB.setFont(font)

        font = self.speedRefC.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setUnderline(itRefC)
        self.speedRefC.setFont(font)

        font = self.speedOptimized.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setUnderline(itOptimized)
        self.speedOptimized.setFont(font)

    def newLap(self, curPoint, lastLap):
        # Check if the full screen color flashing should be for the best lap from now on
        if self.cfg.switchToBestLap:
            logPrint("Compare ref/best lap", msToTime(curPoint.last_lap), msToTime(self.data.refLaps[0].time))
            if self.cfg.bigCountdownBrakepoint == 2 and (self.data.refLaps[0] is None or self.data.refLaps[0].time > curPoint.last_lap):
                if not self.data.refLaps[0] is None:
                    logPrint("Switch to best lap", msToTime(curPoint.last_lap), msToTime(self.data.refLaps[0].time))
                    self.data.showUiMsg("BEAT REFERENCE LAP", 1)
                showBestLapMessage = False
                self.cfg.bigCountdownBrakepoint = 1
                self.markBigCountdownField()
            elif self.cfg.bigCountdownBrakepoint == 3 and (self.data.refLaps[1] is None or self.data.refLaps[1].time > curPoint.last_lap):
                if not self.data.refLaps[1] is None:
                    logPrint("Switch to best lap", msToTime(curPoint.last_lap), msToTime(self.data.refLaps[1].time))
                    self.data.showUiMsg("BEAT REFERENCE LAP", 1)
                showBestLapMessage = False
                self.cfg.bigCountdownBrakepoint = 1
                self.markBigCountdownField()
            elif self.cfg.bigCountdownBrakepoint == 4 and (self.data.refLaps[2] is None or self.data.refLaps[2].time > curPoint.last_lap):
                if not self.data.refLaps[2] is None:
                    logPrint("Switch to best lap", msToTime(curPoint.last_lap), msToTime(self.data.refLaps[2].time))
                    self.data.showUiMsg("BEAT REFERENCE LAP", 1)
                showBestLapMessage = False
                self.cfg.bigCountdownBrakepoint = 1
                self.markBigCountdownField()

    def title(self):
        return "Speed"

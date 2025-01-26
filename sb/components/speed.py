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
    def description():
        return "Speed and time comparisons to previous laps"
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

        self.pedalBest = ColorLabel("")
        self.pedalBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalBest.setAutoFillBackground(True)
        font = self.pedalBest.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalBest.setFont(font)
        self.pedalBest.setColor(self.cfg.backgroundColor)

        self.speedBest = ColorLabel("BEST")
        self.speedBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedBest.setAutoFillBackground(True)
        font = self.speedBest.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedBest.setFont(font)
        if self.cfg.speedcomp:
            self.speedBest.setColor(self.cfg.backgroundColor)

        self.lineBest = LineDeviation()
        self.timeDiffBest = TimeDeviation()

        self.pedalLast = ColorLabel("")
        self.pedalLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalLast.setAutoFillBackground(True)
        font = self.pedalLast.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalLast.setFont(font)
        self.pedalLast.setColor(self.cfg.backgroundColor)

        self.speedLast = ColorLabel("LAST")
        self.speedLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLast.setAutoFillBackground(True)
        font = self.speedLast.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedLast.setFont(font)
        if self.cfg.speedcomp:
            self.speedLast.setColor(self.cfg.backgroundColor)

        self.lineLast = LineDeviation()
        self.timeDiffLast = TimeDeviation()

        self.pedalRefA = ColorLabel("")
        self.pedalRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefA.setAutoFillBackground(True)
        font = self.pedalRefA.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalRefA.setFont(font)
        self.pedalRefA.setColor(self.cfg.backgroundColor)

        self.speedRefA = ColorLabel("REF A")
        self.speedRefA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefA.setAutoFillBackground(True)
        font = self.speedRefA.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedRefA.setFont(font)
        if self.cfg.speedcomp:
            self.speedRefA.setColor(self.cfg.backgroundColor)

        self.lineRefA = LineDeviation()
        self.timeDiffRefA = TimeDeviation()

        self.pedalRefB = ColorLabel("")
        self.pedalRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefB.setAutoFillBackground(True)
        font = self.pedalRefB.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalRefB.setFont(font)
        self.pedalRefB.setColor(self.cfg.backgroundColor)

        self.speedRefB = ColorLabel("REF B")
        self.speedRefB.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefB.setAutoFillBackground(True)
        font = self.speedRefB.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedRefB.setFont(font)
        if self.cfg.speedcomp:
            self.speedRefB.setColor(self.cfg.backgroundColor)

        self.lineRefB = LineDeviation()
        self.timeDiffRefB = TimeDeviation()

        self.pedalRefC = ColorLabel("")
        self.pedalRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalRefC.setAutoFillBackground(True)
        font = self.pedalRefC.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalRefC.setFont(font)
        self.pedalRefC.setColor(self.cfg.backgroundColor)

        self.speedRefC = ColorLabel("REF C")
        self.speedRefC.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedRefC.setAutoFillBackground(True)
        font = self.speedRefC.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedRefC.setFont(font)
        if self.cfg.speedcomp:
            self.speedRefC.setColor(self.cfg.backgroundColor)

        self.lineRefC = LineDeviation()
        self.timeDiffRefC = TimeDeviation()

        self.pedalMedian = ColorLabel("")
        self.pedalMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalMedian.setAutoFillBackground(True)
        font = self.pedalMedian.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalMedian.setFont(font)
        self.pedalMedian.setColor(self.cfg.backgroundColor)

        self.speedMedian = ColorLabel("MEDIAN")
        self.speedMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedMedian.setAutoFillBackground(True)
        font = self.speedMedian.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedMedian.setFont(font)
        if self.cfg.speedcomp:
            self.speedMedian.setColor(self.cfg.backgroundColor)

        self.lineMedian = LineDeviation()
        self.timeDiffMedian = TimeDeviation()

        self.pedalOptimized = ColorLabel("")
        self.pedalOptimized.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pedalOptimized.setAutoFillBackground(True)
        font = self.pedalOptimized.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.pedalOptimized.setFont(font)
        self.pedalOptimized.setColor(self.cfg.backgroundColor)

        self.speedOptimized = ColorLabel("OPT")
        self.speedOptimized.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedOptimized.setAutoFillBackground(True)
        font = self.speedOptimized.font()
        font.setPointSize(self.cfg.fontSizeNormal)
        font.setBold(True)
        self.speedOptimized.setFont(font)
        if self.cfg.speedcomp:
            self.speedOptimized.setColor(self.cfg.backgroundColor)

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
        if self.cfg.showOptimalLap and not self.cfg.circuitExperience:
            speedLayout.addWidget(self.speedOptimized, 2, 6)
        speedLayout.setRowStretch(2, 4)
        if not self.cfg.speedcomp:
            if self.cfg.showBestLap:
                self.speedBest = ColorLabel("")
            if self.cfg.showMedianLap:
                self.speedMedian = ColorLabel("")
            if self.cfg.showRefALap:
                self.speedRefA = ColorLabel("")
            if self.cfg.showRefBLap:
                self.speedRefB = ColorLabel("")
            if self.cfg.showRefCLap:
                self.speedRefC = ColorLabel("")
            if self.cfg.showLastLap:
                self.speedLast = ColorLabel("")
            if self.cfg.showOptimalLap and not self.cfg.circuitExperience:
                self.speedOptimized = ColorLabel("")
            speedLayout.setRowStretch(2, 1)

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
            if self.cfg.showOptimalLap and not self.cfg.circuitExperience:
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
            if self.cfg.showOptimalLap and not self.cfg.circuitExperience:
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
            if self.cfg.showOptimalLap and not self.cfg.circuitExperience:
                speedLayout.addWidget(self.pedalOptimized, 0, 6)
            speedLayout.setRowStretch(0, 1)

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

        self.data.setColor(self.cfg.brightBackgroundColor)

        self.updateOneSpeedEntry(last, curPoint)
        self.updateOneSpeedEntry(refA, curPoint)
        self.updateOneSpeedEntry(refB, curPoint)
        self.updateOneSpeedEntry(refC, curPoint)
        self.updateOneSpeedEntry(best, curPoint)
        self.updateOneSpeedEntry(median, curPoint)
        self.updateOneSpeedEntry(opti, curPoint)

    def cycleBigCountdownBreakponts(self):
        self.cfg.bigCountdownBrakepoint += 1
        hit = False
        while not hit:
            if self.cfg.bigCountdownBrakepoint > 5:
                self.cfg.bigCountdownBrakepoint = 0
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 1 and self.cfg.showBestLap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 2 and self.cfg.showRefALap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 3 and self.cfg.showRefBLap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 4 and self.cfg.showRefCLap:
                hit = True
            elif self.cfg.bigCountdownBrakepoint == 5 and self.cfg.showOptimalLap:
                hit = True
            else:
                self.cfg.bigCountdownBrakepoint += 1

    def updateOneSpeedEntry(self, refLap, curPoint):
        bgCol = self.cfg.brightBackgroundColor
        col = self.cfg.backgroundColor

        if not refLap.closestPoint is None:
            # SPEED
            speedDiff = refLap.closestPoint.car_speed - curPoint.car_speed
            refLap.speedWidget.setColor(self.speedDiffQColor(speedDiff))

            # BRAKE POINTS
            if self.cfg.throttlepoints or self.cfg.brakepoints:
                refLap.pedalWidget.setText("")

            if self.cfg.throttlepoints:
                if refLap.closestOffsetPoint.throttle > 98:
                    refLap.pedalWidget.setText("GAS")
                    col = QColor("#f2f")
                    if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                        bgCol = QColor("#626")

            if self.cfg.brakepoints:
                if refLap.closestOffsetPoint.brake > 0:
                    refLap.pedalWidget.setText("BRAKE")
                    col = self.brakeQColor(refLap.closestOffsetPoint.brake)
                    if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                        bgCol = self.brakeQColor(refLap.closestOffsetPoint.brake)

                elif self.cfg.countdownBrakepoint and not refLap.nextBrake is None:
                    refLap.pedalWidget.setText(str(math.ceil (refLap.nextBrake/60)))
                    if refLap.nextBrake >= 120:
                        if refLap.nextBrake%60 >= 30:
                            col = self.cfg.countdownColor3
                            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                                bgCol = self.cfg.countdownColor3
                    elif refLap.nextBrake >= 60:
                        if refLap.nextBrake%60 >= 30:
                            col = self.cfg.countdownColor2
                            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                                bgCol = self.cfg.countdownColor2
                    else:
                        if refLap.nextBrake%30 >= 15:
                            col = self.cfg.countdownColor1
                            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                                bgCol = self.cfg.countdownColor1

            refLap.pedalWidget.setColor(col)
            refLap.lineWidget.setPoints(curPoint, refLap.closestPoint)
            refLap.lineWidget.update()

            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                self.data.setColor(bgCol)

            # TIME DIFF
            refLap.timeDiffWidget.setDiff(refLap.closestIndex - len(self.data.curLap.points))
            refLap.timeDiffWidget.update()
        else:
            refLap.speedWidget.setColor(self.cfg.backgroundColor)
            refLap.pedalWidget.setColor(self.cfg.backgroundColor)
            refLap.pedalWidget.setText("")
            if self.cfg.bigCountdownBrakepoint == refLap.id and self.data.masterWidget.currentIndex() == 0:
                self.data.setColor(bgCol)
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
        if self.data.brakeOffset != 0:
            self.header.setText("[" + str(round(self.data.brakeOffset/-60, 2)) + "] SPEED")
        else:
            self.header.setText("SPEED")
        self.header.update()
        self.markBigCountdownField()

    def newSession(self):
        pal = self.pedalLast.palette()
        self.pedalLast.setText("")
        pal.setColor(self.pedalLast.backgroundRole(), self.cfg.backgroundColor)
        self.pedalLast.setColor(self.cfg.backgroundColor)

        pal = self.pedalBest.palette()
        self.pedalBest.setText("")
        pal.setColor(self.pedalBest.backgroundRole(), self.cfg.backgroundColor)
        self.pedalBest.setColor(self.cfg.backgroundColor)

        pal = self.pedalMedian.palette()
        self.pedalMedian.setText("")
        pal.setColor(self.pedalMedian.backgroundRole(), self.cfg.backgroundColor)
        self.pedalMedian.setColor(self.cfg.backgroundColor)

        pal = self.pedalRefA.palette()
        self.pedalRefA.setText("")
        pal.setColor(self.pedalRefA.backgroundRole(), self.cfg.backgroundColor)
        self.pedalRefA.setColor(self.cfg.backgroundColor)

        pal = self.pedalRefB.palette()
        self.pedalRefB.setText("")
        pal.setColor(self.pedalRefB.backgroundRole(), self.cfg.backgroundColor)
        self.pedalRefB.setColor(self.cfg.backgroundColor)

        pal = self.pedalRefC.palette()
        self.pedalRefC.setText("")
        pal.setColor(self.pedalRefC.backgroundRole(), self.cfg.backgroundColor)
        self.pedalRefC.setColor(self.cfg.backgroundColor)

        pal = self.pedalOptimized.palette()
        self.pedalOptimized.setText("")
        pal.setColor(self.pedalOptimized.backgroundRole(), self.cfg.backgroundColor)
        self.pedalOptimized.setColor(self.cfg.backgroundColor)

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
        itBest = self.cfg.bigCountdownBrakepoint == 1
        itRefA = self.cfg.bigCountdownBrakepoint == 2
        itRefB = self.cfg.bigCountdownBrakepoint == 3
        itRefC = self.cfg.bigCountdownBrakepoint == 4
        itOptimized = self.cfg.bigCountdownBrakepoint == 5

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

    def completedLap(self, curPoint, lastLap, isFullLap):
        if lastLap.valid:
            self.speedLast.setText("LAST")
        else:
            self.speedLast.setText("(LAST)")

        if not isFullLap:
            return
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

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Tab:
            self.cycleBigCountdownBreakponts()

sb.component.componentLibrary['Speed'] = Speed

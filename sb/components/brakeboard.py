from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import random
import time
import sb.component
from sb.gt7telepoint import Point
from sb.gt7widgets import ColorLabel, LineDeviation
from sb.helpers import logPrint

class BrakeBoard(sb.component.Component):
    def description():
        return "Pedal coach"

    def actions():
        return {
                "cycleModes":"Cycle BrakeBoard modes",
                "cycleDifficulty":"Cycle BrakeBoard difficulty"
               }
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)

        self.brakeTargetLevel = 50
        self.brakeDownTime = None
        self.brakeFromFull = False
        self.prevBrakes = []

        self.startTime = None
        self.delayTime = 5

        self.mode = 0 # brake target
        self.state = "begin"
        self.difficulty = 0

        self.difficultyNames = { 0:"EASY", 1:"MEDIUM", 2:"HARD", 3:"SENNA" }

        random.seed()
    
    def getWidget(self):
        self.mainLabel = ColorLabel("\u2197 50%")
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLabel.setAutoFillBackground(True)
        font = self.mainLabel.font()
        font.setPointSize(self.fontSizeLarge() * 4)
        font.setBold(True)
        self.mainLabel.setFont(font)
        self.mainLabel.setColor(self.cfg.backgroundColor)

        self.topLabel = ColorLabel("MODE: BRAKE LEVEL")
        self.topLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topLabel.setAutoFillBackground(True)
        font = self.topLabel.font()
        font.setPointSize(self.fontSizeLarge())
        font.setBold(True)
        self.topLabel.setFont(font)
        self.topLabel.setColor(self.cfg.backgroundColor)

        self.bottomLabel = ColorLabel ("PRESS THE BRAKE PEDAL TO 50% AND HOLD")
        self.bottomLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottomLabel.setAutoFillBackground(True)
        font = self.bottomLabel.font()
        font.setPointSize(self.fontSizeSmall())
        font.setBold(True)
        self.bottomLabel.setFont(font)
        self.bottomLabel.setColor(self.cfg.backgroundColor)

        self.deviation = LineDeviation()
        self.deviation.setMaxDeviation(20)
        self.deviation.setColorScaleMode(1, 5, 10)
        self.deviation.setDistance(0)

        layout = QGridLayout()

        self.mainWidget = QWidget()
        self.mainWidget.setLayout(layout)
        layout.addWidget(self.topLabel, 0, 0)
        layout.addWidget(self.mainLabel, 1, 0, 3, 1)
        layout.addWidget(self.bottomLabel, 5, 0)
        layout.addWidget(self.deviation, 6, 0)

        self.updateDifficulty()
        self.updateMode()
        return self.mainWidget

    def cycleDifficulty(self):
        self.difficulty += 1
        if not self.difficulty in self.difficultyNames:
            self.difficulty = 0
        self.updateDifficulty()
        self.updateMode()

    def updateDifficulty(self):
        if self.difficulty == 0:
            self.brakeHoldTime = 60
            self.brakeHoldCorridor = 5
            self.brakeLevelTolerance = 12

            self.brakeTimingTolerance = 0.08
        elif self.difficulty == 1:
            self.brakeHoldTime = 30
            self.brakeHoldCorridor = 5
            self.brakeLevelTolerance = 8

            self.brakeTimingTolerance = 0.04
        elif self.difficulty == 2:
            self.brakeHoldTime = 30
            self.brakeHoldCorridor = 5
            self.brakeLevelTolerance = 4

            self.brakeTimingTolerance = 0.02
        elif self.difficulty == 3:
            self.brakeHoldTime = 15
            self.brakeHoldCorridor = 5
            self.brakeLevelTolerance = 1

            self.brakeTimingTolerance = 0.01

    def cycleModes(self):
        self.state = "begin"
        self.mode += 1
        if self.mode > 1:
            self.mode = 0
        self.updateMode()

    def updateMode(self):
        logPrint("Next brakeboard mode:", self.mode)
        self.state = "begin"

        if self.mode == 0:
            self.brakeTargetLevel = 50
            self.topLabel.setText("MODE: BRAKE LEVEL, " + self.difficultyNames[self.difficulty])
            self.bottomLabel.setText("PRESS THE BRAKE PEDAL TO " + str(self.brakeTargetLevel) + "%" + " AND HOLD")
            self.mainLabel.setText("\u2197 50%")
            self.prevBrakes = []
            self.deviation.setMaxDeviation(5 * self.brakeLevelTolerance)
            self.deviation.setColorScaleMode(1, self.brakeLevelTolerance, 3 * self.brakeLevelTolerance)
        elif self.mode == 1:
            self.topLabel.setText("MODE: BRAKE TIMING, " + self.difficultyNames[self.difficulty])
            self.bottomLabel.setText("PRESS THE BRAKE PEDAL AT THE RIGHT TIME")
            self.mainLabel.setText("WAIT")
            self.startTime = time.perf_counter()
            self.delayTime = random.randrange(1000,5000)
            self.deviation.setMaxDeviation(10 * self.brakeTimingTolerance)
            self.deviation.setColorScaleMode(1, self.brakeTimingTolerance, 3 * self.brakeTimingTolerance)
            logPrint(self.delayTime)


    def callAction(self, a):
        if a == "cycleModes":
            self.cycleModes()
        elif a == "cycleDifficulty":
            self.cycleDifficulty()

    def brakeTiming(self, curPoint):
        now = time.perf_counter()
        if self.state != "begin" and curPoint.brake > self.cfg.brakeMinimumLevel and self.brakeDownTime is None:
            self.brakeDownTime = now
            logPrint("Braking!", self.brakeDownTime)
        if self.state == "begin":
            if now - self.startTime >= self.delayTime/1000.0:
                self.state = "countdown3"
                self.startTime = now
                self.mainLabel.setText("3")
                self.mainLabel.setColor(self.cfg.countdownColor3)
        elif self.state == "countdown3":
            if now - self.startTime >= 0.5:
                self.mainLabel.setColor(self.cfg.backgroundColor)
            if now - self.startTime >= 1.0:
                self.state = "countdown2"
                self.startTime = now
                self.mainLabel.setText("2")
                self.mainLabel.setColor(self.cfg.countdownColor2)
        elif self.state == "countdown2":
            if now - self.startTime >= 0.5:
                self.mainLabel.setColor(self.cfg.backgroundColor)
            if now - self.startTime >= 1.0:
                self.state = "countdown1"
                self.startTime = now
                self.mainLabel.setText("1")
                self.mainLabel.setStyleSheet("color:black")
                self.mainLabel.setColor(self.cfg.countdownColor1)
        elif self.state == "countdown1":
            if now - self.startTime >= 0.25:
                self.mainLabel.setStyleSheet("")
                self.mainLabel.setColor(self.cfg.backgroundColor)
            if now - self.startTime >= 0.5:
                self.mainLabel.setStyleSheet("color:black")
                self.mainLabel.setColor(self.cfg.countdownColor1)
            if now - self.startTime >= 0.75:
                self.mainLabel.setStyleSheet("")
                self.mainLabel.setColor(self.cfg.backgroundColor)
            if now - self.startTime >= 1.0:
                self.state = "brakepoint"
                self.startTime = now
                self.targetTime = now
                self.mainLabel.setText("BRAKE!")
        elif self.state == "brakepoint":
            if now - self.startTime >= 3.0 or not self.brakeDownTime is None:
                logPrint(now, self.brakeDownTime, self.startTime, curPoint.brake)
                self.state = "result"
                self.startTime = now
                if self.brakeDownTime is None:
                    self.mainLabel.setText("MISS!")
                    self.deviation.setDistance(-1000)
                    self.deviation.update()
                elif self.targetTime - self.brakeDownTime < -self.brakeTimingTolerance:
                    self.mainLabel.setText("LATE")
                    self.bottomLabel.setText(str(round(self.brakeDownTime - self.targetTime, 3)) + "s")
                    self.deviation.setDistance(self.targetTime - self.brakeDownTime)
                    self.deviation.update()
                elif self.targetTime - self.brakeDownTime > self.brakeTimingTolerance:
                    self.mainLabel.setText("EARLY")
                    self.bottomLabel.setText(str(round(self.brakeDownTime - self.targetTime, 3)) + "s")
                    self.deviation.setDistance(self.targetTime - self.brakeDownTime)
                    self.deviation.update()
                elif self.targetTime - self.brakeDownTime < 0.0:
                    self.mainLabel.setText("GOOD")
                    self.bottomLabel.setText(str(round(self.brakeDownTime - self.targetTime, 3)) + "s")
                    self.deviation.setDistance(self.targetTime - self.brakeDownTime)
                    self.deviation.update()
                elif self.targetTime - self.brakeDownTime > 0.0:
                    self.mainLabel.setText("GOOD")
                    self.bottomLabel.setText(str(round(self.brakeDownTime - self.targetTime, 3)) + "s")
                    self.deviation.setDistance(self.targetTime - self.brakeDownTime)
                    self.deviation.update()
                else:
                    self.mainLabel.setText("PERFECT!")
                    self.deviation.setDistance(0)
                    self.deviation.update()
                    logPrint("PERFECT")
        elif self.state == "result":
            if now - self.startTime >= 3.0:
                self.state = "begin"
                self.startTime = now
                self.brakeDownTime = None
                self.mainLabel.setText("WAIT")
                self.bottomLabel.setText("PRESS THE BRAKE PEDAL AT THE RIGHT TIME")
                self.delayTime = random.randrange(1000,5000)
                self.deviation.setDistance(0)
                self.deviation.update()
                logPrint(self.delayTime)


    def brakeTarget(self, curPoint):
        if self.state == "begin":
            if not self.brakeFromFull and curPoint.brake > 2:
                self.state = "braking"
                logPrint(self.state)
                self.prevBrakes.append(curPoint.brake)
            elif self.brakeFromFull and curPoint.brake == 100:
                self.state = "brakingfull"
                logPrint(self.state)
                self.bottomLabel.setText("GO BACK TO " + str(self.brakeTargetLevel) + "%" + " AND HOLD")
        elif self.state == "brakingfull":
            if curPoint.brake < 98:
                self.state = "braking"
                logPrint(self.state)
                self.prevBrakes.append(curPoint.brake)
        elif self.state == "braking":
            self.prevBrakes.append(curPoint.brake)
            if len(self.prevBrakes) > self.brakeHoldTime:
                self.prevBrakes = self.prevBrakes[-self.brakeHoldTime:]
            if sum(self.prevBrakes) / len(self.prevBrakes) < 2:
                self.state = "begin"
                logPrint(self.state)
                if self.brakeFromFull:
                    self.bottomLabel.setText("PRESS THE BRAKE PEDAL FULLY, THEN GO BACK TO " + str(self.brakeTargetLevel) + "%" + " AND HOLD")
            elif len(self.prevBrakes) == self.brakeHoldTime and abs(max(self.prevBrakes) - min(self.prevBrakes)) < self.brakeHoldCorridor:
                self.state = "brakelevelreached"
                logPrint(self.state)
                self.deviation.setDistance(self.brakeTargetLevel - round(sum(self.prevBrakes[-3:]) / len(self.prevBrakes[-3:])))
                self.deviation.update()
        elif self.state == "brakelevelreached":
            if curPoint.brake < 2:
                self.state = "begin"
                logPrint(self.state)
                self.prevBrakes = []
                self.brakeTargetLevel = random.randrange(25,100,25)
                self.brakeFromFull = bool(random.getrandbits(1))
                if self.brakeFromFull:
                    self.mainLabel.setText("\u2198 " + str(self.brakeTargetLevel) + "%")
                    self.bottomLabel.setText("PRESS THE BRAKE PEDAL FULLY, THEN GO BACK TO " + str(self.brakeTargetLevel) + "%" + " AND HOLD")
                else:
                    self.mainLabel.setText("\u2197 " + str(self.brakeTargetLevel) + "%")
                    self.bottomLabel.setText("PRESS THE BRAKE PEDAL TO " + str(self.brakeTargetLevel) + "%" + " AND HOLD")
                self.deviation.setDistance(0)
                self.deviation.update()
            else:
                if (self.brakeTargetLevel - sum(self.prevBrakes[-3:]) / len(self.prevBrakes[-3:])) >= self.brakeLevelTolerance: # TODO constants
                    self.mainLabel.setText("TOO SOFT")
                elif (self.brakeTargetLevel - sum(self.prevBrakes[-3:]) / len(self.prevBrakes[-3:])) <= -self.brakeLevelTolerance:
                    self.mainLabel.setText("TOO HARD")
                elif round(self.brakeTargetLevel - sum(self.prevBrakes[-3:]) / len(self.prevBrakes[-3:])) > 0:
                    self.mainLabel.setText("GOOD")
                elif round(self.brakeTargetLevel - sum(self.prevBrakes[-3:]) / len(self.prevBrakes[-3:])) < 0:
                    self.mainLabel.setText("GOOD")
                else:
                    self.mainLabel.setText("PERFECT")
                self.bottomLabel.setText(str (round(sum(self.prevBrakes[-3:]) / len(self.prevBrakes[-3:]))) + "% vs " + str(self.brakeTargetLevel) + "%")


    def addPoint(self, curPoint, curLap):
        if self.mainWidget.isVisible():
            if self.mode == 0:
                self.brakeTarget(curPoint)
            elif self.mode == 1:
                self.brakeTiming(curPoint)

    def defaultTitle(self):
        return "BrakeBoard"

sb.component.componentLibrary['BrakeBoard'] = BrakeBoard

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
    
    def __init__(self, cfg, data):
        super().__init__(cfg, data)

        self.mainLabel = ColorLabel("\u2197 50%")
        self.mainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainLabel.setAutoFillBackground(True)
        font = self.mainLabel.font()
        font.setPointSize(self.cfg.fontSizeLarge * 4)
        font.setBold(True)
        self.mainLabel.setFont(font)
        self.mainLabel.setColor(self.cfg.backgroundColor)

        self.topLabel = ColorLabel("MODE: BRAKE LEVEL")
        self.topLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topLabel.setAutoFillBackground(True)
        font = self.topLabel.font()
        font.setPointSize(self.cfg.fontSizeLarge)
        font.setBold(True)
        self.topLabel.setFont(font)
        self.topLabel.setColor(self.cfg.backgroundColor)

        self.bottomLabel = ColorLabel ("PRESS THE BRAKE PEDAL TO 50% AND HOLD")
        self.bottomLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bottomLabel.setAutoFillBackground(True)
        font = self.bottomLabel.font()
        font.setPointSize(self.cfg.fontSizeSmall)
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

        self.brakeTargetLevel = 50
        self.brakeDownTime = None
        self.prevBrakes = []

        self.startTime = None
        self.delayTime = 5

        self.mode = 0 # brake target
        self.state = "begin"

        random.seed()
    
    def getWidget(self):
        return self.mainWidget

    def cycleModes(self):
        self.state = "begin"
        self.mode += 1
        if self.mode > 1:
            self.mode = 0

        logPrint("Next brakeboard mode:", self.mode)

        if self.mode == 0:
            self.brakeTargetLevel = 50
            self.topLabel.setText("MODE: BRAKE LEVEL")
            self.bottomLabel.setText("PRESS THE BRAKE PEDAL TO " + str(self.brakeTargetLevel) + "%" + " AND HOLD")
            self.mainLabel.setText("\u2197 50%")
            self.prevBrakes = []
            self.deviation.setMaxDeviation(100)
            self.deviation.setColorScaleMode(1, 30, 60)
        elif self.mode == 1:
            self.topLabel.setText("MODE: BRAKE TIMING")
            self.bottomLabel.setText("PRESS THE BRAKE PEDAL AT THE RIGHT TIME")
            self.mainLabel.setText("WAIT")
            self.startTime = time.perf_counter()
            self.delayTime = random.randrange(1000,5000)
            self.deviation.setMaxDeviation(0.1)
            self.deviation.setColorScaleMode(1, 0.01, 0.05)
            logPrint(self.delayTime)


    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Tab:
            self.cycleModes()


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
                self.mainLabel.setColor(self.cfg.countdownColor1)
        elif self.state == "countdown1":
            if now - self.startTime >= 0.25:
                self.mainLabel.setColor(self.cfg.backgroundColor)
            if now - self.startTime >= 0.5:
                self.mainLabel.setColor(self.cfg.countdownColor1)
            if now - self.startTime >= 0.75:
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
                elif self.targetTime - self.brakeDownTime < -0.01: # TODO constants
                    self.mainLabel.setText("LATE")
                    self.bottomLabel.setText(str(round(self.brakeDownTime - self.targetTime, 3)) + "s")
                    self.deviation.setDistance(self.targetTime - self.brakeDownTime)
                    self.deviation.update()
                elif self.targetTime - self.brakeDownTime > 0.01:
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
            if curPoint.brake > 2:
                self.state = "braking"
                logPrint(self.state)
                self.prevBrakes.append(curPoint.brake)
        elif self.state == "braking":
            self.prevBrakes.append(curPoint.brake)
            logPrint(curPoint.brake)
            if len(self.prevBrakes) > 30:
                self.prevBrakes = self.prevBrakes[-30:]
            if sum(self.prevBrakes) / len(self.prevBrakes) < 2:
                self.state = "begin"
                logPrint(self.state)
            elif len(self.prevBrakes) == 30 and abs(max(self.prevBrakes) - min(self.prevBrakes)) < 5:
                self.state = "brakelevelreached"
                logPrint(self.state)
                self.deviation.setDistance(self.brakeTargetLevel - sum(self.prevBrakes) / len(self.prevBrakes))
                self.deviation.update()
        elif self.state == "brakelevelreached":
            if curPoint.brake < 2:
                self.state = "begin"
                logPrint(self.state)
                self.prevBrakes = []
                self.brakeTargetLevel = random.randrange(25,100,25)
                self.mainLabel.setText("\u2197 " + str(self.brakeTargetLevel) + "%")
                #self.mainLabel.setText("\u2198 " + str(self.brakeTargetLevel) + "%")
                self.bottomLabel.setText("PRESS THE BRAKE PEDAL TO " + str(self.brakeTargetLevel) + "%" + " AND HOLD")
                self.deviation.setDistance(0)
                self.deviation.update()
            else:
                logPrint (self.brakeTargetLevel - sum(self.prevBrakes) / len(self.prevBrakes))
                logPrint (self.brakeTargetLevel , sum(self.prevBrakes) / len(self.prevBrakes))
                if (self.brakeTargetLevel - sum(self.prevBrakes) / len(self.prevBrakes)) > 5: # TODO constants
                    self.mainLabel.setText("TOO SOFT")
                elif (self.brakeTargetLevel - sum(self.prevBrakes) / len(self.prevBrakes)) < -5:
                    self.mainLabel.setText("TOO HARD")
                elif round(self.brakeTargetLevel - sum(self.prevBrakes) / len(self.prevBrakes)) > 0:
                    self.mainLabel.setText("GOOD")
                elif round(self.brakeTargetLevel - sum(self.prevBrakes) / len(self.prevBrakes)) < 0:
                    self.mainLabel.setText("GOOD")
                else:
                    self.mainLabel.setText("PERFECT")
                self.bottomLabel.setText(str (round(sum(self.prevBrakes) / len(self.prevBrakes))) + "% vs " + str(self.brakeTargetLevel) + "%")


    def addPoint(self, curPoint, curLap):
        if self.mode == 0:
            self.brakeTarget(curPoint)
        elif self.mode == 1:
            self.brakeTiming(curPoint)

    def title(self):
        return "BrakeBoard"

sb.component.componentLibrary['BrakeBoard'] = BrakeBoard

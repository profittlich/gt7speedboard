from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

import datetime
import sb.component
from sb.gt7widgets import *
from sb.gt7telepoint import Point
from sb.helpers import logPrint

class FuelAndMessages(sb.component.Component):
    def __init__(self, cfg):
        super().__init__(cfg)

        self.fuelWidget = QWidget()

        self.fuel = QLabel("?%")
        self.fuel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fuel.setAutoFillBackground(True)
        font = self.fuel.font()
        font.setPointSize(cfg.fontSizeNormal)
        font.setBold(True)
        self.fuel.setFont(font)

        self.fuelBar = FuelGauge()

        self.fuelBar.setThreshold(cfg.fuelMultiplier * cfg.fuelWarning)
        self.fuelBar.setMaxLevel(cfg.fuelMultiplier * cfg.maxFuelConsumption)

        self.laps = QLabel("? LAPS LEFT")
        self.laps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.laps.setAutoFillBackground(True)
        font = self.laps.font()
        font.setPointSize(cfg.fontSizeNormal)
        font.setBold(True)
        self.laps.setFont(font)
        pal = self.laps.palette()
        pal.setColor(self.laps.backgroundRole(), cfg.backgroundColor)
        pal.setColor(self.laps.foregroundRole(), cfg.foregroundColor)
        self.laps.setPalette(pal)


        pal = self.fuel.palette()
        pal.setColor(self.fuel.backgroundRole(), cfg.backgroundColor)
        pal.setColor(self.fuel.foregroundRole(), cfg.foregroundColor)
        self.fuel.setPalette(pal)
        fuelLayout = QGridLayout()
        fuelLayout.setContentsMargins(11,11,11,11)
        self.fuelWidget.setLayout(fuelLayout)
        fuelLayout.setColumnStretch(0, 1)
        fuelLayout.setColumnStretch(1, 1)
        fuelLayout.setColumnStretch(2, 1)

        fuelLayout.addWidget(self.fuel, 0, 0, 1, 2)
        fuelLayout.addWidget(self.fuelBar, 0, 2, 1, 1)
        fuelLayout.addWidget(self.laps, 1, 0, 1, 3)


    def getWidget(self):
        return self.fuelWidget

    def updateFuelAndWarnings(self, curPoint, curLap):
        fuel_capacity = curPoint.fuel_capacity
        postfix = "%"
        if fuel_capacity == 0: # EV
            fuel_capacity = 100
            postfix = " kWh"

        if len(curLap.points) > 0 and curPoint.current_fuel > curLap.points[-1].current_fuel:
            logPrint("Refueled!")
            self.data.refueled = 0
            if self.data.lapProgress > 0.5:
                self.data.refueled -= 1
            self.data.manualPitStop = False

        if (curPoint.current_fuel / fuel_capacity) < 1 or self.data.manualPitStop:
            lapValue = self.data.refueled
            if self.cfg.lapDecimals:
                lapValue += self.data.lapProgress
                lapValue = round(lapValue, 2)
            if self.data.manualPitStop:
                refuelLaps = "<br>" + str (lapValue) + " SINCE PIT STOP"
            else:
                refuelLaps = "<br>" + str (lapValue) + " SINCE REFUEL"
        else:
            refuelLaps = ""

        if self.data.fuelFactor != 0:
            fuelLapPercent = "<br>" + str(round(100 * self.data.fuelFactor,1)) + postfix + " PER LAP<br>" + str(round(1 / self.data.fuelFactor,1)) + " FULL RANGE"
        else:
            fuelLapPercent = ""

        self.fuel.setTextFormat(Qt.TextFormat.RichText)
        self.fuel.setText("<font size=6>" + str(round(100 * curPoint.current_fuel / fuel_capacity)) + postfix + "</font><font size=1>" + fuelLapPercent + refuelLaps + "</font>")
        if len (curLap.points) > 0:
            fuelConsumption = curLap.points[-1].current_fuel-curPoint.current_fuel 
            fuelConsumption *= self.cfg.psFPS * 60 * 60 # l per hour
            if curPoint.car_speed > 0:
                fuelConsumption /= curPoint.car_speed # l per km
                fuelConsumption *= 100 # l per 100 km

            self.fuelBar.setLevel(max(0, fuelConsumption))
            self.fuelBar.update()

        self.laps.setTextFormat(Qt.TextFormat.RichText)
        messageShown = False
        if self.cfg.messagesEnabled: # TODO: put at end and remove messageShown?
            for m in self.data.messages:
                if curPoint.distance(m[0]) < self.cfg.messageDisplayDistance:
                    pal = self.laps.palette()
                    if (datetime.datetime.now().microsecond + self.cfg.messageBlinkingPhase) % 500000 < 250000:
                        pal.setColor(self.laps.backgroundRole(), self.cfg.warningColor1)
                        pal.setColor(self.laps.foregroundRole(), self.cfg.foregroundColor)
                    else:
                        pal.setColor(self.laps.backgroundRole(), self.cfg.foregroundColor)
                        pal.setColor(self.laps.foregroundRole(), self.cfg.warningColor1)
                    self.laps.setPalette(pal)
                    self.laps.setText(m[1])
                    messageShown = True


        if not messageShown:
            if self.data.fuelFactor > 0:
                lapsFuel = curPoint.current_fuel / fuel_capacity / self.data.fuelFactor
                remainingRefuels = ""
                if curPoint.total_laps > 0:
                    fuelStints = (curPoint.total_laps + self.data.lapOffset - curPoint.current_lap + 1 - self.data.lapProgress - lapsFuel) * self.data.fuelFactor
                    plural = ""
                    if fuelStints > 1:
                        plural = "S"
                    remainingRefuels = '<br><font size="1">' + str(int(math.ceil(fuelStints))) + " REFUEL" + plural + " NEEDED (" + str(round(100 * (fuelStints - math.floor(fuelStints)))) + "%)</font>"
                self.laps.setText("<font size=4>" + str(round(lapsFuel, 2)) + " LAPS</font><br><font color='#7f7f7f' size=1>FUEL REMAINING</font>" + remainingRefuels)

                lapValue = 1
                if self.cfg.lapDecimals and self.data.closestILast > 0:
                    lapValue -= self.data.lapProgress
                
                if self.cfg.lapDecimals and round(lapsFuel, 2) < 1 and lapsFuel < lapValue:
                    pal = self.laps.palette()
                    if datetime.datetime.now().microsecond < 500000:
                        pal.setColor(self.laps.backgroundRole(), self.cfg.warningColor1)
                        pal.setColor(self.laps.foregroundRole(), self.cfg.foregroundColor)
                    else:
                        pal.setColor(self.laps.backgroundRole(), self.cfg.warningColor2)
                        pal.setColor(self.laps.foregroundRole(), self.cfg.backgroundColor)
                    self.laps.setPalette(pal)
                elif round(lapsFuel, 2) < 1:
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), self.cfg.warningColor1)
                    pal.setColor(self.laps.foregroundRole(), self.cfg.foregroundColor)
                    self.laps.setPalette(pal)
                elif round(lapsFuel, 2) < 2:
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), self.cfg.backgroundColor)
                    pal.setColor(self.laps.foregroundRole(), self.cfg.advanceWarningColor)
                    self.laps.setPalette(pal)
                else:
                    pal = self.laps.palette()
                    pal.setColor(self.laps.backgroundRole(), self.cfg.backgroundColor)
                    pal.setColor(self.laps.foregroundRole(), self.cfg.foregroundColor)
                    self.laps.setPalette(pal)
            elif curPoint.current_fuel == fuel_capacity:
                self.laps.setText("<font size=1>FOREVER</font>")
                pal = self.laps.palette()
                pal.setColor(self.laps.backgroundRole(), self.cfg.backgroundColor)
                pal.setColor(self.laps.foregroundRole(), self.cfg.foregroundColor)
                self.laps.setPalette(pal)
            else:
                self.laps.setText("<font size=1>MEASURING</font>")
                pal = self.laps.palette()
                pal.setColor(self.laps.backgroundRole(), self.cfg.backgroundColor)
                pal.setColor(self.laps.foregroundRole(), self.cfg.foregroundColor)
                self.laps.setPalette(pal)

    def addPoint(self, curPoint, curLap):
        self.updateFuelAndWarnings(curPoint, curLap)

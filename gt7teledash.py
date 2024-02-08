import sys
import os
import threading
from wakepy import keep
import math
import queue

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout

from gt7telepoint import Point

import gt7telemetryreceiver as tele


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GT7 TeleDash")
        self.queue = queue.Queue()

        
        # Lvl 4
        self.fuel = QLabel("?%")
        self.fuel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.fuel.font()
        font.setPointSize(96)
        font.setBold(True)
        self.fuel.setFont(font)

        self.fuelBar = QWidget()

        self.laps = QLabel("? LAPS LEFT")
        self.laps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.laps.font()
        font.setPointSize(96)
        font.setBold(True)
        self.laps.setFont(font)

        self.tyreFR = QLabel("?°C")
        self.tyreFR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.tyreFR.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreFR.setFont(font)

        self.tyreFL = QLabel("?°C")
        self.tyreFL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.tyreFL.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreFL.setFont(font)
        
        self.tyreRR = QLabel("?°C")
        self.tyreRR.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.tyreRR.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreRR.setFont(font)

        self.tyreRL = QLabel("?°C")
        self.tyreRL.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.tyreRL.font()
        font.setPointSize(72)
        font.setBold(True)
        self.tyreRL.setFont(font)

        self.speedBest = QLabel("BEST")
        self.speedBest.setStyleSheet("background-color:grey;")
        self.speedBest.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.speedBest.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedBest.setFont(font)

        self.speedLast = QLabel("LAST")
        self.speedLast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedLast.setStyleSheet("background-color:grey;")
        font = self.speedLast.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedLast.setFont(font)

        self.speedMedian = QLabel("MEDIAN")
        self.speedMedian.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedMedian.setStyleSheet("background-color:grey;")
        font = self.speedMedian.font()
        font.setPointSize(64)
        font.setBold(True)
        self.speedMedian.setFont(font)

        # Lvl 3
        fuelWidget = QWidget()
        self.fuel.setStyleSheet("background-color:#222;")
        self.laps.setStyleSheet("background-color:#222;")
        fuelLayout = QGridLayout()
        fuelLayout.setContentsMargins(11,11,11,11)
        fuelWidget.setLayout(fuelLayout)
        fuelLayout.setColumnStretch(0, 10)
        fuelLayout.setColumnStretch(1, 1)

        fuelLayout.addWidget(self.fuel, 0, 0, 1, 1)
        fuelLayout.addWidget(self.fuelBar, 0, 1, 1, 1)
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
        speedLayout.addWidget(self.speedBest, 0, 0)
        speedLayout.addWidget(self.speedMedian, 0, 1)
        speedLayout.addWidget(self.speedLast, 0, 3)

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

        headerSpeed = QLabel("SPEED")
        font = headerSpeed.font()
        font.setPointSize(64)
        font.setBold(True)
        headerSpeed.setFont(font)
        headerSpeed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Lvl 1
        masterLayout = QGridLayout()
        masterWidget = QWidget()
        masterWidget.setLayout(masterLayout)
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
        masterLayout.addWidget(headerSpeed, 1, 0, 1, 1)
        masterLayout.addWidget(fuelWidget, 2, 1, 3, 1)
        masterLayout.addWidget(tyreWidget, 4, 0, 1, 1)
        masterLayout.addWidget(speedWidget, 2, 0, 1, 1)

        self.setCentralWidget(masterWidget)

        self.initRace()

        self.receiver = tele.GT7TelemetryReceiver()
        self.receiver.setQueue(self.queue)
        self.thread = threading.Thread(target=self.receiver.runTelemetryReceiver)
        self.thread.start()

        # Timer
        self.timer = QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start()

    def initRace(self):
        self.lastLap = -1
        self.lastFuel = -1
        self.lastFuelUsage = []
        self.fuelFactor = 0
        self.refueled = 0

        self.newLapPos = []
        self.previousLaps = []
        self.bestLap = -1
        self.medianLap = -1

    def tyreTempColor(self, temp):
        col = QColor()
        hue = 0.333 - (temp - 70)/50
        if hue < 0:
            hue = 0
        if hue > 0.666:
            hue = 0.666
        col.setHsvF (hue, 1, 1)

        return "background-color: " + col.name() + ";"

    def speedDiffColor(self, d):
        col = QColor()
        hue = -d/60 + 60/360
        if hue < 0:
            hue = 0
        if hue > 120/360:
            hue = 120/360
        col.setHsvF (hue, 1, 1)

        return "background-color: " + col.name() + ";"

    def distance(self, p1, p2):
        return math.sqrt( (p1.position_x-p2.position_x)**2 + (p1.position_y-p2.position_y)**2 + (p1.position_z-p2.position_z)**2)

    def findClosestPoint(self, lap, p):
        shortestDistance = 100000000
        result = None
        for p2 in lap:
            curDist = self.distance(p, p2)
            if curDist < 10 and curDist < shortestDistance:
                shortestDistance = curDist
                result = p2

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
        val = min (1, max(0.002, val))
        return "background: qlineargradient( x1:0 y1:1, x2:0 y2:0, stop:" + str(val-0.001) + " darkred, stop:" + str (val) + " #222);"

    def updateDisplay(self):
        counter = 0
        while not self.queue.empty():
            counter += 1
            d = self.queue.get()

            curPoint = Point(d)

            if curPoint.current_lap  == 0:
                self.initRace()
                continue

            # TYRE TEMPS
            self.tyreFL.setText (str(round(curPoint.tyre_temp_FL)) + "°C")
            self.tyreFL.setStyleSheet(self.tyreTempColor(curPoint.tyre_temp_FL))
            self.tyreFR.setText (str(round(curPoint.tyre_temp_FR)) + "°C")
            self.tyreFR.setStyleSheet(self.tyreTempColor(curPoint.tyre_temp_FR))
            self.tyreRR.setText (str(round(curPoint.tyre_temp_RR)) + "°C")
            self.tyreRR.setStyleSheet(self.tyreTempColor(curPoint.tyre_temp_RR))
            self.tyreRL.setText (str(round(curPoint.tyre_temp_RL)) + "°C")
            self.tyreRL.setStyleSheet(self.tyreTempColor(curPoint.tyre_temp_RL))

            # LAP DISPLAY
            if self.refueled > 0:
                refuelLaps = "\n" + str (self.refueled) + " SINCE REFUEL"
            else:
                refuelLaps = ""

            if curPoint.total_laps > 0:
                self.header.setText(str(curPoint.total_laps - curPoint.current_lap + 1) + " LAPS LEFT")
            else:
                self.header.setText("LAP " + str(curPoint.current_lap))

            if self.lastLap == -1 and curPoint.current_lap > 0:
                self.lastLap = curPoint.current_lap
                self.lastFuel = curPoint.current_fuel/curPoint.fuel_capacity

            # LAP CHANGE
            if self.lastLap < curPoint.current_lap:
                print("LAP CHANGE")
                self.previousLaps.append([curPoint.last_lap, self.newLapPos])
                self.bestLap = self.findBestLap()
                self.medianLap = self.findMedianLap()
                self.newLapPos = []
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
            elif self.lastLap > curPoint.current_lap or curPoint.current_lap == 0:
                self.initRace()

            # FUEL
            self.fuel.setText(str(round(100 * curPoint.current_fuel / curPoint.fuel_capacity)) + "%\n" + str(round(100 * self.fuelFactor,1)) + "% PER LAP" + refuelLaps)
            self.fuelBar.setStyleSheet(self.makeFuelBar(curPoint.current_fuel / curPoint.fuel_capacity))
            if self.fuelFactor > 0:
                self.laps.setText(str(round(curPoint.current_fuel / curPoint.fuel_capacity / self.fuelFactor, 2)) + " LAPS FUEL")
                if round(curPoint.current_fuel / curPoint.fuel_capacity / self.fuelFactor, 2) < 1:
                    self.laps.setStyleSheet("background-color:red;")
                elif round(curPoint.current_fuel / curPoint.fuel_capacity / self.fuelFactor, 2) < 2:
                    self.laps.setStyleSheet("background-color:orange;")
                else:
                    self.laps.setStyleSheet("background-color:#222;")

            elif curPoint.current_fuel == curPoint.fuel_capacity:
                self.laps.setText("FOREVER")
            else:
                self.laps.setText("measuring")

            # SPEED
            closestPLast = None
            closestPBest = None
            closestPMedian = None
            if len(self.previousLaps) > 0:
                closestPLast = self.findClosestPoint (self.previousLaps[-1][1], curPoint)
                closestPBest = self.findClosestPoint (self.previousLaps[self.bestLap][1], curPoint)
                closestPMedian = self.findClosestPoint (self.previousLaps[self.medianLap][1], curPoint)

            if not closestPLast is None:
                speedDiff = closestPLast.car_speed - curPoint.car_speed
                self.speedLast.setStyleSheet(self.speedDiffColor(speedDiff))
            else:
                self.speedLast.setStyleSheet("background-color:grey;")

            if not closestPBest is None:
                speedDiff = closestPBest.car_speed - curPoint.car_speed
                self.speedBest.setStyleSheet(self.speedDiffColor(speedDiff))
            else:
                self.speedBest.setStyleSheet("background-color:grey;")

            if not closestPMedian is None:
                speedDiff = closestPMedian.car_speed - curPoint.car_speed
                self.speedMedian.setStyleSheet(self.speedDiffColor(speedDiff))
            else:
                self.speedMedian.setStyleSheet("background-color:grey;")

            self.newLapPos.append(curPoint)

    def closeEvent(self, event):
        self.receiver.running = False
        self.thread.join()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    with keep.presenting():
        app.exec()


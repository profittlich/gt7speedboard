import sys
import os
import threading
import traceback
from wakepy import keep
import datetime
from cProfile import Profile

from PyQt6.QtCore import Qt 
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QSpinBox, QFileDialog

from gt7telepoint import Point
from helpers import loadLap, loadLaps, indexToTime
from helpers import Lap, PositionPoint

import gt7telemetryreceiver as tele
from mapview2 import MapView2

class StartWindowVLC(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GT7 SpeedBoard Visual Lap Compare 1.0")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lRefB = QLabel("Blue lap:")
        layout.addWidget(self.lRefB)
        self.bRefB = QPushButton("Select file")
        self.bRefB.clicked.connect(self.chooseReferenceLapB)
        layout.addWidget(self.bRefB)
        self.refBFile = ""
        
        self.idxRefB = QComboBox()
        layout.addWidget(self.idxRefB)

        self.lRefA = QLabel("Violet lap:")
        layout.addWidget(self.lRefA)
        self.bRefA = QPushButton("Select file")
        layout.addWidget(self.bRefA)
        self.bRefA.clicked.connect(self.chooseReferenceLapA)
        self.refAFile = ""
        
        self.idxRefA = QComboBox()
        layout.addWidget(self.idxRefA)

        self.starter = QPushButton("Compare")
        layout.addWidget(self.starter)

    def chooseReferenceLapA(self):
        chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7)")
        if chosen[0] == "":
            print("None")
        else:
            self.refAFile = chosen[0]
            self.lRefA.setText("Red lap: " + chosen[0][chosen[0].rfind("/")+1:])
            self.aLaps = loadLaps(self.refAFile)
            for l in self.aLaps:
                self.idxRefA.addItem(str(l.points[0].current_lap) + ": " + str(indexToTime(len(l.points))))

    def chooseReferenceLapB(self):
        chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7)")
        if chosen[0] == "":
            print("None")
        else:
            self.refBFile = chosen[0]
            self.lRefB.setText("Green lap: " + chosen[0][chosen[0].rfind("/")+1:])
            self.bLaps = loadLaps(self.refBFile)
            for l in self.bLaps:
                self.idxRefB.addItem(str(l.points[0].current_lap) + ": " + str(indexToTime(len(l.points))))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.masterWidget = MapView2()
        self.startWidget = StartWindowVLC()
        self.startWidget.starter.clicked.connect(self.compare)

        self.setWindowTitle("GT7 Visual Lap Comparison")

        self.setCentralWidget(self.startWidget)

    def compare(self):
        lap1 = self.startWidget.aLaps[self.startWidget.idxRefA.currentIndex()]
        lap2 = self.startWidget.bLaps[self.startWidget.idxRefB.currentIndex()]
        self.masterWidget.setLaps(lap1, lap2)
        self.setCentralWidget(self.masterWidget)

    def keyPressEvent(self, e):
        self.masterWidget.delegateKeyPressEvent(e)



def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("=== EXCEPTION ===")
    print("error message:\n", tb)
    with open ("gt7visualcomp.log", "a") as f:
        f.write("=== EXCEPTION ===\n")
        f.write(str(datetime.datetime.now ()) + "\n\n")
        f.write(str(tb) + "\n")
    QApplication.quit()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setOrganizationName("pitstop.profittlich.com");
    app.setOrganizationDomain("pitstop.profittlich.com");
    app.setApplicationName("GT7 Visual Lap Comparison");

    window = MainWindow()

    if len(sys.argv) >= 3:
        lap1 = loadLap(sys.argv[1])
        lap2 = loadLap(sys.argv[2])

        window.masterWidget.setLaps(lap1, lap2)
        window.setCentralWidget(window.masterWidget)
    
    window.show()

    sys.excepthook = excepthook
    app.exec()



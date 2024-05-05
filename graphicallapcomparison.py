import sys
import os
import traceback
from wakepy import keep
import datetime
from cProfile import Profile

from PyQt6.QtCore import Qt 
from PyQt6.QtWidgets import *

from sb.gt7telepoint import Point
from sb.helpers import loadLap, loadLaps, indexToTime
from sb.helpers import Lap, PositionPoint

import sb.gt7telemetryreceiver as tele
from sb.mapview2 import MapView2

class StartWindowVLC(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GT7 SpeedBoard Graphical Lap Comparison")

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
        chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7; *.gt7track; *.gt7lap; *.gt7laps)")
        if chosen[0] == "":
            print("None")
        else:
            self.refAFile = chosen[0]
            self.lRefA.setText("Violet lap: " + chosen[0][chosen[0].rfind("/")+1:])
            if self.refAFile == self.refBFile:
                self.aLaps = self.bLaps
            else:
                self.aLaps = loadLaps(self.refAFile)
            for l in self.aLaps:
                self.idxRefA.addItem(str(l.points[0].current_lap) + ": " + str(indexToTime(len(l.points))))

    def chooseReferenceLapB(self):
        chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7; *.gt7track; *.gt7lap; *.gt7laps)")
        if chosen[0] == "":
            print("None")
        else:
            self.refBFile = chosen[0]
            self.lRefB.setText("Blue lap: " + chosen[0][chosen[0].rfind("/")+1:])
            if self.refAFile == self.refBFile:
                self.bLaps = self.aLaps
            else:
                self.bLaps = loadLaps(self.refBFile)
            for l in self.bLaps:
                self.idxRefB.addItem(str(l.points[0].current_lap) + ": " + str(indexToTime(len(l.points))))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.stackWidget = QStackedWidget()
        self.masterWidget = MapView2()
        self.startWidget = StartWindowVLC()
        self.startWidget.starter.clicked.connect(self.compare)

        self.stackWidget.addWidget(self.startWidget)
        self.stackWidget.addWidget(self.masterWidget)

        self.setWindowTitle("GT7 Graphical Lap Comparison")

        self.setCentralWidget(self.stackWidget)

    def compare(self):
        lap1 = self.startWidget.aLaps[self.startWidget.idxRefA.currentIndex()]
        lap2 = self.startWidget.bLaps[self.startWidget.idxRefB.currentIndex()]
        self.masterWidget.setLaps(self.startWidget.refAFile, lap1, self.startWidget.refBFile, lap2)
        
        self.stackWidget.setCurrentIndex(1)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape.value:
            self.stackWidget.setCurrentIndex(0)
        else:
            self.masterWidget.delegateKeyPressEvent(e)



def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("=== EXCEPTION ===")
    print("error message:\n", tb)
    with open ("gt7glc.log", "a") as f:
        f.write("=== EXCEPTION ===\n")
        f.write(str(datetime.datetime.now ()) + "\n\n")
        f.write(str(tb) + "\n")
    QApplication.quit()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setOrganizationName("pitstop.profittlich.com");
    app.setOrganizationDomain("pitstop.profittlich.com");
    app.setApplicationName("GT7 Graphical Lap Comparison");

    window = MainWindow()

    if len(sys.argv) >= 3:
        lap1 = loadLap(sys.argv[1])
        lap2 = loadLap(sys.argv[2])

        window.masterWidget.setLaps(lap1, lap2)
        window.setCentralWidget(window.masterWidget)
    
    window.show()

    sys.excepthook = excepthook
    app.exec()



from salsa20 import Salsa20_xor
import traceback
import datetime
import threading
import time
import socket
import sys
import struct
from PyQt6.QtCore import Qt 
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QCheckBox, QDoubleSpinBox, QFileDialog
from sb.crypt import salsa20_dec, salsa20_enc

class GT7Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.heartbeat = datetime.datetime.now()


class GT7PlaybackServer:

    def __init__(self, ip, stopCallback=None):
        # ports for send and receive data
        self.s = None
        self.InPort = 33739
        self.ip = ip
        self.running = False
        self.fps = 59.94
        self.filename = None
        self.simulateFrameDrops = False
        self.stopCallback = stopCallback
        self.clients = {}

    def setFPS(self, b):
        self.oldPc = time.perf_counter()
        self.pcCounter = 0
        self.fps = b

    def setFilename(self, f):
        self.filename = f
    
    def stop(self):
        self.running=False

    def internalStop(self):
        self.stop()
        if not self.stopCallback is None:
            self.stopCallback()

    def setSimulateFrameDrops(self, on):
        self.simulateFrameDrops = on

    def checkHeartBeat(self):
      try:
        print("Heartbeat watchdog started")
        noHeartBeat = 0
        self.clients = {}
        while self.running:
            try:
                data, address = self.s.recvfrom(4096)
                print("Received heartbeat from " + address[0] + " [" + str(address[1]) + "]")
                self.clients[address[0] + "--" + str(address[1])] = GT7Client(address[0], address[1])
                noHeartBeat = 0
                connected = True
                now = datetime.datetime.now()
                toBeDeleted = []
                for c in self.clients:
                    if (now - self.clients[c].heartbeat) > datetime.timedelta(seconds=12):
                        toBeDeleted.append(c)
                for c in toBeDeleted:
                    del self.clients[c]
                    print("Remove client", c, len(self.clients), "left")
            except TimeoutError as e:
                noHeartBeat += 1
            except Exception as e:
                self.internalStop()
                print('HB Exception: {}'.format(e))
                print(traceback.format_exception(e))
            if noHeartBeat >= 12:
                print("No heartbeat received.")
                self.internalStop()
                self.clients = {}
      except Exception as e:
          self.internalStop()
          print('Outer Exception: {}'.format(e))


    def runPlaybackServer(self):
        print("Running server...")

        print("Load", self.filename)
        f = open(self.filename, "rb")
        self.allData = f.read()
        f.close()

        print("Frames:", len(self.allData)/296)

        # Create a UDP socket and bind it
        if self.s is None:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind(('0.0.0.0', self.InPort))
            self.s.settimeout(1)

        self.running = True
        connected = False
        while not connected and self.running:
            try:
                data, address = self.s.recvfrom(4096)
                connected = True
            except TimeoutError as e:
                pass
            except Exception as e:
                print('Exception: {}'.format(e))
        if connected:
            print("Connected to ", address)

        hbt = threading.Thread(target = self.checkHeartBeat)
        hbt.start()

        curIndex = 0
        self.oldPc = time.perf_counter()
        self.pcCounter = 0
        pktIdCounter = 0
        while self.running:
            try:
                pc = time.perf_counter()
                self.pcCounter += 1
                while pc-1/self.fps < self.pcCounter/self.fps + self.oldPc:
                    time.sleep(1/(100*self.fps))
                    pc = time.perf_counter()

                decr = bytearray(salsa20_dec(self.allData[curIndex:curIndex+296]))
                newPktId = struct.unpack('i', decr[0x70:0x70+4])[0]
                struct.pack_into('i', decr, 0x70, pktIdCounter)
                newNewPktId = struct.unpack('i', decr[0x70:0x70+4])[0]
                if (curIndex//296) % 600 == 0:
                    print("Serve index", curIndex//296, "pkt", newPktId, "new pkt", newNewPktId)
                encr = salsa20_enc(decr, 296)

                if not self.simulateFrameDrops or pktIdCounter % 8 == 0:
                    for c in self.clients:
                        self.s.sendto(encr, (self.clients[c].ip, self.clients[c].port))


                curIndex += 296
                if curIndex >= len(self.allData):
                    print("Loop")
                    curIndex = 0
                pktIdCounter += 1

            except Exception as e:
                print('Exception: {}'.format(e))
        print("Serving stopped.")

class StartWindowPS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GT7 Playback Server")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lRec = QLabel("File:")
        layout.addWidget(self.lRec)
        self.bRec = QPushButton("Select file")
        layout.addWidget(self.bRec)
        self.recFile = ""

        self.lFps = QLabel("Playback rate:")
        layout.addWidget(self.lFps)
        self.sFps = QDoubleSpinBox()
        self.sFps.setValue(1)
        self.sFps.setMinimum(0.1)
        self.sFps.setMaximum(10)
        self.sFps.setSingleStep(0.1)
        self.sFps.setDecimals(1)
        self.sFps.setSuffix("x")
        layout.addWidget(self.sFps)
        
        self.starter = QPushButton("Serve")
        layout.addWidget(self.starter)
        self.stopper = QPushButton("Stop")
        layout.addWidget(self.stopper)
        self.stopper.hide()


class MainWindow(QMainWindow):
    remoteStopSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.server = GT7PlaybackServer ("127.0.0.1", self.remoteStop)
        self.thread = None
        self.startWidget = StartWindowPS()
        self.startWidget.starter.clicked.connect(self.serve)
        self.startWidget.stopper.clicked.connect(self.stop)
        self.startWidget.bRec.clicked.connect(self.chooseRecording)
        self.startWidget.sFps.valueChanged.connect(self.updateRate)

        self.remoteStopSignal.connect(self.restartServer)

        self.setCentralWidget(self.startWidget)

    def remoteStop(self):
        self.remoteStopSignal.emit()

    def restartServer(self):
        if not self.thread is None:
            self.thread.join()
            self.thread = None
        self.serve()

    def cleanUpAfterStop(self):
        if not self.thread is None:
            self.thread.join()
            self.thread = None
        self.startWidget.stopper.hide()
        self.startWidget.starter.show()

    def stop(self):
        self.server.stop()
        self.cleanUpAfterStop()

    def chooseRecording(self):
        chosen = QFileDialog.getOpenFileName(filter="GT7 Telemetry (*.gt7; *.gt7lap; *.gt7laps)")
        if chosen[0] == "":
            print("None")
        else:
            self.startWidget.recFile = chosen[0]
            self.startWidget.lRec.setText("File: " + chosen[0][chosen[0].rfind("/")+1:])
            self.stop()

    def updateRate(self, rate):
        print("Set rate to", rate, "(" + str(59.94*rate) + " fps)")
        self.server.setFPS(59.94 * rate)

    def serve(self):
        if self.startWidget.recFile != "":
            self.server.setFPS(59.94 * self.startWidget.sFps.value())
            self.server.setFilename(self.startWidget.recFile)
            self.thread = threading.Thread(target=self.server.runPlaybackServer)
            self.thread.start()
            self.startWidget.stopper.show()
            self.startWidget.starter.hide()

    def closeEvent(self, event):
        print("Closing...")
        self.server.stop()
        event.accept()


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("=== EXCEPTION ===")
    print("error message:\n", tb)
    with open ("gt7playbackserver.log", "a") as f:
        f.write("=== EXCEPTION ===\n")
        f.write(str(datetime.datetime.now ()) + "\n\n")
        f.write(str(tb) + "\n")
    QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    app.setOrganizationName("pitstop.profittlich.com");
    app.setOrganizationDomain("pitstop.profittlich.com");
    app.setApplicationName("GT7 Playback Server");

    window = MainWindow()

    ready = False
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--fps":
            fps = float(sys.argv[i+1])
            window.server.setFPS(fps)
            i+=1
        if sys.argv[i] == "--simulate-frame-drops":
            window.server.setSimulateFrameDrops(True)
        else:
            ready = True
            window.server.setFilename(sys.argv[i])
        i+=1
    if ready:
        window.server.runPlaybackServer()
    else:
        window.show()

        sys.excepthook = excepthook
        app.exec()

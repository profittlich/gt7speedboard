from datetime import datetime as dt
from datetime import timedelta as td
from sb.helpers import logPrint
import socket
import sys
import struct
import threading
import queue
import time
from sb.crypt import salsa20_dec

class GT7TelemetryReceiver:

    def __init__(self, ip):
        # ports for send and receive data
        self.SendPort = 33739
        self.ReceivePort = 33740
        self.ip = ip
        self.prevlap = -1
        self.pktid = 0
        self.pknt = time.perf_counter()
        self.s = None
        self.running = False
        self.queue = None
        self.record = None
        self.startRec = False
        self.stopRec = False
        self.ignorePktId = False

    def setQueue(self, q):
        self.queue = q

    def setIgnorePktId(self, b):
        self.ignorePktId = b

    # send heartbeat
    def send_hb(self):
        send_data = 'A'
        #logPrint("Send heartbeat to " + self.ip)
        self.s.sendto(send_data.encode('utf-8'), (self.ip, self.SendPort))
        #logPrint('send heartbeat')

    def startRecording(self, sessionName, withTimeStamp = True):
        logPrint("Start recording")
        self.startRec = True
        self.timeStampRecording = withTimeStamp
        self.sessionName = sessionName

    def stopRecording(self):
        logPrint("Stop recording")
        self.startRec = False
        self.stopRec = True

    def runTelemetryReceiver(self):
        # Create a UDP socket and bind it
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bindTries=10
        while bindTries > 0:
            try:
                self.s.bind(("0.0.0.0", self.ReceivePort))
                bindTries = 0
            except:
                self.ReceivePort += 1
                bindTries -= 1
        self.s.settimeout(2)

        # start by sending heartbeat
        self.send_hb()

        self.running = True
        while self.running:
            try:
                if self.startRec:
                    if self.timeStampRecording:
                        fn = self.sessionName + "recording-" + dt.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7"
                    else:
                        fn = self.sessionName + "recording-last.gt7"
                    logPrint("record to", fn)
                    self.record = open (fn, "wb")
                    self.startRec = False
                if self.stopRec:
                    self.stopRec = False
                    self.record.close()
                    self.record = None

                data, address = self.s.recvfrom(4096)
                if not address[0] == self.ip:
                    continue

                if not self.record is None:
                    self.record.write(data)
                
                ddata = salsa20_dec(data)
                newPktId = struct.unpack('i', ddata[0x70:0x70+4])[0]
                if len(ddata) > 0 and newPktId < self.pktid:
                    logPrint("Time travel or new recording")
                    self.pktid = newPktId-1
                    
                if len(ddata) > 0 and (self.ignorePktId or newPktId > self.pktid):
                    if self.pktid != newPktId-1:
                        logPrint("Packet loss:", newPktId-self.pktid-1)
                    self.pktid = newPktId

                    if not self.queue is None:
                        self.queue.put((ddata, data))

                newPknt = time.perf_counter()
                if newPknt - self.pknt > 5:
                    self.send_hb()
                    self.pknt = time.perf_counter()
            except Exception as e:
                logPrint('Exception in telemetry receiver: {}'.format(e))
                self.send_hb()
                self.pknt = time.perf_counter()

        self.s.close()


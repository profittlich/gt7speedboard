from datetime import datetime as dt
from datetime import timedelta as td
import socket
import sys
import struct
import threading
import queue
from helpers import salsa20_dec

class GT7TelemetryReceiver:

    def __init__(self, ip):
        # ports for send and receive data
        self.SendPort = 33739
        self.ReceivePort = 33740
        self.ip = ip
        self.prevlap = -1
        self.pktid = 0
        self.pknt = 0
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
        #print("Send heartbeat to " + self.ip)
        self.s.sendto(send_data.encode('utf-8'), (self.ip, self.SendPort))
        #print('send heartbeat')

    def startRecording(self, sessionName):
        print("Start recording")
        self.startRec = True
        self.sessionName = sessionName

    def stopRecording(self):
        print("Stop recording")
        self.startRec = False
        self.stopRec = True

    def runTelemetryReceiver(self):
        # Create a UDP socket and bind it
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("0.0.0.0", self.ReceivePort))
        self.s.settimeout(2)

        # start by sending heartbeat
        self.send_hb()

        self.running = True
        while self.running:
            try:
                if self.startRec:
                    fn = self.sessionName + "recording-" + dt.now().strftime("%Y-%m-%d_%H-%M-%S") + ".gt7"
                    print("record to", fn)
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
                
                self.pknt = self.pknt + 1
                ddata = salsa20_dec(data)
                newPktId = struct.unpack('i', ddata[0x70:0x70+4])[0]
                if len(ddata) > 0 and (self.ignorePktId or newPktId > self.pktid):
                    if self.pktid != newPktId-1:
                        print("Packet loss:", newPktId-self.pktid-1)
                    self.pktid = newPktId

                    if not self.queue is None:
                        self.queue.put((ddata, data))

                if self.pknt > 100:
                    self.send_hb()
                    self.pknt = 0
            except Exception as e:
                print('Exception: {}'.format(e))
                self.send_hb()
                self.pknt = 0


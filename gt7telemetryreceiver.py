from datetime import datetime as dt
from datetime import timedelta as td
import socket
import sys
import struct
import threading
import queue
# pip3 install salsa20
from salsa20 import Salsa20_xor

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

    def setQueue(self, q):
        self.queue = q

    # data stream decoding
    def salsa20_dec(self, dat):
        KEY = b'Simulator Interface Packet GT7 ver 0.0'
        # Seed IV is always located here
        oiv = dat[0x40:0x44]
        iv1 = int.from_bytes(oiv, byteorder='little')
        # Notice DEADBEAF, not DEADBEEF
        iv2 = iv1 ^ 0xDEADBEAF
        IV = bytearray()
        IV.extend(iv2.to_bytes(4, 'little'))
        IV.extend(iv1.to_bytes(4, 'little'))
        ddata = Salsa20_xor(dat, bytes(IV), KEY[0:32])
        magic = int.from_bytes(ddata[0:4], byteorder='little')
        if magic != 0x47375330:
            return bytearray(b'')
        return ddata

    # send heartbeat
    def send_hb(self):
        send_data = 'A'
        #print("Send heartbeat to " + self.ip)
        self.s.sendto(send_data.encode('utf-8'), (self.ip, self.SendPort))
        #print('send heartbeat')


    def runTelemetryReceiver(self):
        # Create a UDP socket and bind it
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('0.0.0.0', self.ReceivePort))
        self.s.settimeout(2)

        # start by sending heartbeat
        self.send_hb()

        self.running = True
        while self.running:
            try:
                data, address = self.s.recvfrom(4096)
                self.pknt = self.pknt + 1
                ddata = self.salsa20_dec(data)
                if len(ddata) > 0 and struct.unpack('i', ddata[0x70:0x70+4])[0] > self.pktid:

                    if not self.queue is None:
                        self.queue.put(ddata)

                if self.pknt > 100:
                    self.send_hb()
                    self.pknt = 0
            except Exception as e:
                print('Exception: {}'.format(e))
                self.send_hb()
                self.pknt = 0


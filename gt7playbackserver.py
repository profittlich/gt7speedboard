from salsa20 import Salsa20_xor
import time
import socket
import sys

class GT7PlaybackServer:

    def __init__(self, ip):
        # ports for send and receive data
        self.SendPort = 33739
        self.ReceivePort = 33740
        self.ip = ip
        self.running = False
        self.fps = 60
        self.filename = None

    def setFPS(self, b):
        self.fps = b

    def setFilename(self, f):
        self.filename = f
    
    def salsa20_enc(self, dat, iv1):
        KEY = b'Simulator Interface Packet GT7 ver 0.0'
        # Seed IV is always located here
        oiv = iv1.to_bytes(4, 'little')
        iv1 = int.from_bytes(oiv, byteorder='little')
        # Notice DEADBEAF, not DEADBEEF
        iv2 = iv1 ^ 0xDEADBEAF
        IV = bytearray()
        IV.extend(iv2.to_bytes(4, 'little'))
        IV.extend(iv1.to_bytes(4, 'little'))
        dat[0:4] = 0x47375330.to_bytes(4, 'little')
        print(type(dat), type(bytes(IV)), type(KEY[0:32]))
        ddata = bytearray(Salsa20_xor(bytes(dat), bytes(IV), KEY[0:32]))
        ddata[0x40:0x44] = oiv
        return ddata

    def runPlaybackServer(self):
        # Create a UDP socket and bind it
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('0.0.0.0', self.SendPort))
        self.s.settimeout(2)

        f = open(self.filename, "rb")
        allData = f.read()
        f.close()

        print("Samples:", len(allData)/296)

        connected = False
        while not connected:
            try:
                data, address = self.s.recvfrom(4096)
                print(address)
                connected = True
            except Exception as e:
                print('Exception: {}'.format(e))
        print("Connected to ", address)

        self.running = True
        curIndex = 0
        oldPc = 0
        while self.running:
            try:
                pc = time.perf_counter()
                while pc-1/self.fps < oldPc:
                    time.sleep(1/(10*self.fps))
                    pc = time.perf_counter()
                oldPc = pc

                self.s.sendto(allData[curIndex:curIndex + 296], (self.ip, self.ReceivePort))
                curIndex += 296
                if curIndex >= len(allData):
                    print("Loop")
                    curIndex = 0

            except Exception as e:
                print('Exception: {}'.format(e))


if __name__ == '__main__':
    tester = GT7PlaybackServer ("127.0.0.1")
    ready = False
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--fps":
            fps = float(sys.argv[i+1])
            tester.setFPS(fps)
            i+=1
        else:
            ready = True
            tester.setFilename(sys.argv[i])
        i+=1
    if ready:
        tester.runPlaybackServer()
    else:
        print("usage: " + sys.argv[0] + " [options] <filename>")

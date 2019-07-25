import gatt
import time
import multiprocessing
import socket
import struct
import glob


## from the gatt library example at https://github.com/getsenic/gatt-python


global optDataQueue
optDataQueue = multiprocessing.Queue()

global dataServer
global dataClient
global dataStore

dataServer = False
dataClient = False
dataStore = ""

from sys import platform
#if on linux, import functions for IMU and ip
if platform == "linux" or platform == "linux2":
    import fcntl  # linux specific (keep note)
    import sys, getopt

    sys.path.append('.')
    import RTIMU #imu library
    import os.path
else:
    try :
        from msvcrt import getch
    except Exception as e:
        print (str(e))


def get_ip_address(ifname): #Who is this code based on?
    if (platform == "linux") or (platform == "linux2"):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Resolving ip address")
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    else:
        print("Not linux... cant find ipAddress")

tiBaseID = "F0000000-0451-4000-B000-000000000000"
manager = gatt.DeviceManager(adapter_name='hci0')
#
global opt_data
opt_data = 0

global clientConnection
global SeverSocket

# opt_config = "AA72"
# opt_period = "AA73"

def runServer():
    global SeverSocket
    global dataServer

    print("Setting up sockets...")
    try:
        if (platform == "linux") or (platform == "linux2"):
            HOST =  get_ip_address('eth0'.encode())  # socket.gethostbyname(socket.gethostname()) #socket.gethostname()
        else:
            HOST = "localhost"

        PORT = 5003

        # create a socket to establish a server
        print("Binding the socket...")
        SeverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SeverSocket.bind((HOST, PORT))
        SeverSocket.settimeout(5)

        # listen to incoming connections on PORT
        print("Socket opened at %s listening to port %s", HOST, PORT)
        SeverSocket.listen(1)
        dataServer = True
    except Exception as e:
        print("%s", str(e))
        dataServer = False
        print("Sleeping...")
        time.sleep(5)


def waitForClient():
    global SeverSocket
    global dataClient
    global clientConnection
    # for each connection received create a tunnel to the client
    try:
        print("Ready for a new client to connect...(5s Timeout)")
        clientConnection,clientAddress = SeverSocket.accept()
        print("Connected by %s", clientAddress)
        # send welcome message

        print("Sending welcome message...")
        dataStore = "S0"
        clientConnection.send(dataStore.encode())
        print("Getting data ACK from Client")
        dataStore = clientConnection.recv(1024).decode()
        if dataStore == "S1":
            print("Client Connection Validated")
            dataClient = True
        else:
            print("Client Connection FAILED :( Try again...")
            clientConnection.close
            dataClient = False
    except Exception as e:
        print(str(e))

class BTDevice(gatt.Device):

    #firmware_version_characteristic = None
    global clientConnection

    optSense_data = None
    optSense_config = None
    optSense_period = None

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        optSense_service = next(
            s for s in self.services
            if s.uuid == 'f000aa70-0451-4000-b000-000000000000')

        self.optSense_data = next(
            c for c in optSense_service.characteristics
            if c.uuid == 'f000aa71-0451-4000-b000-000000000000')


        self.optSense_config = next(
            c for c in optSense_service.characteristics
            if c.uuid == 'f000aa72-0451-4000-b000-000000000000')


        self.optSense_period = next(
            c for c in optSense_service.characteristics
            if c.uuid == 'f000aa73-0451-4000-b000-000000000000')

        frame = bytearray()
        #frame.append(0x00)
        frame.append(0x01)

        self.optSense_data.enable_notifications()
        #optSense_config.read_value()
        self.optSense_config.write_value(frame)
        self.optSense_period.write_value([0x0A])
        #time.sleep(1)

        #optSense_config.read_value()

        #time.sleep(1)
        #for i in range (20):
        #while True:
        self.optSense_data.read_value()
            #time.sleep(0.100)


    def characteristic_enable_notification_succeeded():
        print("successfully subscribed to notifications on ", characteristic.uuid)

    def characteristic_enable_notification_failed():
        pass

    def characteristic_write_value_succeeded(self, characteristic):
        #print("successfully written data to ", characteristic.uuid)
        pass
    def characteristic_write_value_failed(error):
        print("Data Write Failed: ", error)

    def characteristic_value_updated(self, characteristic, value):
        decValue = (value[1]*15 + value[0])
        print("Characteristic ", str(characteristic.uuid) , ": ", decValue )
        #if characteristic.uuid == self.optSense_data:
        #print("sending Data")
        if decValue >0:
            try:
                clientConnection.send(str(decValue).encode())
                clientConnection.send("\n".encode())
            except:
                pass
                #optDataQueue.put(decValue)
                #print("Firmware version:", value.decode("utf-8"))


device = BTDevice(mac_address= 'CC:78:AB:77:22:07', manager=manager)
device.connect()

while not dataServer:
    runServer()
    while not dataClient:
        #print("waiting for client")
        waitForClient()
        #while dataClient:
        #    pass
        #     if not nodeQueue.empty():
        #         clientConnection.send(str(nodeQueue.get()))
        #     time.sleep(0.02)

manager.run()

#device.firmware_version_characteristic.read_value()

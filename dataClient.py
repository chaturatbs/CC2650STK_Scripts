#based on the logging example on the python documentation

import pickle
import logging
import logging.handlers
#import socketserver
import struct
import time
import random

import socket
import serial
import sys
from msvcrt import getch

import csv
from datetime import datetime

#define variables for speed/angle/direction

#set the server address and port
HOST = "192.168.137.252" #raw_input("Please enter the server address: ") #"192.168.137.242" #"192.168.137.154"  #input("Enter the server address to connect to (default port is 5002) - ") #socket.gethostbyname(socket.gethostname()) #socket.gethostname()
PORT = 5003

#create a socket to connect to the server
s = socket.socket()
#connect to the server at HOST through PORT
print ('Trying to connect to ', HOST, 'at port ', PORT)
s.connect((HOST, PORT))

#if connected (add error checking)

#recieve welcome message
print (("Server says - " + s.recv(1024).decode()))

#initialise user input buffer and notify the server (for debugging)
usInput = ""
data = "S1"
print("sending ", data, "\n")
s.send(data.encode())
vCon = False
logToFile = False

try:
    print("Trying to open a serial connection... ")
    viewerCon = serial.Serial('COM7', 19200)
    viewerCon.open()

except Exception as e:
    print("Error! = " + str(e))

finally:
    if viewerCon:
        vCon = True
        print ("Vcon = True")
#
# if logToFile:
#     dt = datetime.now()
#     fileName = "Logfile - " + dt.strftime("%Y_%m_%d-%H%M") + ".csv"
#     logFile = open(fileName, 'wb')
#     spamwriter = csv.writer(logFile, delimiter=' ',quotechar=' ',
#                              quoting=csv.QUOTE_MINIMAL)

#while the user doesnt stop communication using "esc"...

while True:
    data = s.recv(1024).decode()
    #print(data)
    #print("got new Data")
    data.rstrip("\n")
    #print (data)
    try:
        # if logToFile:
        #     #data.rstrip("")
        #     #print (data[0:len(data)-1])
        #     check = data.split(',')
        #     #print len(check)
        #     if len(check) == 38:
        #         spamwriter.writerow(data[0:len(data)-1])
        viewerCon.write(data.encode())
        if len(data) > 1 :
            print (data)

    except Exception as e:
        print(str(e))
        try:
            print ("trying to connect to viewer")
            viewerCon = serial.Serial('COM7', 19200)
            viewerCon.open()

        except Exception as e:
            print(str(e))


s.close()

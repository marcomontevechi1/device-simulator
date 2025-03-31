#!/usr/bin/env python3

import socket
import threading

from .ParamList import ParamList

DEVICES_LIST = []

class Device:

    """
    Simulates a device.
    """

    def __init__(self, name: str = None , param_source: dict = None, port: int = None, log_severity : int = 3):
        
        self.port = port
        self.sock = None
        self.name = name
        self._log_severity = log_severity
        self.paramList = ParamList(source = param_source)
        self.name_lock = threading.Lock()

        self.registerName()
        sockThread = threading.Thread(target = self.createSocket)
        sockThread.start()

    def registerName(self):
        """
        Puts name in device list.
        If name is already there, add an integer to its end. 
        If name is not defined, define it as DeviceSim<N> 
        where N is a number from 0 onwards.
        """
        if self.name is None:
            self.name = "DeviceSim"
        
        n = 0
        self.name_lock.acquire()
        while "{}{}".format(self.name, n) in DEVICES_LIST:
            n+=1

        self.name = "{}{}".format(self.name, n)
        DEVICES_LIST.append(self.name)
        self.name_lock.release()
        self.log("Added name {} to devices list.".format(self.name))

    def createSocket(self):
        """
        Creates socket. Binds to self.port if it's defined.
        Chooses a random port if not.
        """

        while True:

            host = "0.0.0.0"
            port = 0
            if self.port:
                port = self.port
            
            self.sock = socket.socket()
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((host, port))
            (host, port) = self.sock.getsockname()
            self.port = port
            self.log("Bound socket to {}:{}".format(host, port))
            self.sock.listen()
            conn, address = self.sock.accept()
            self.log("Connection from: " + str(address))

            while True:

                try:
                    # receive data stream. it won't accept data packet greater than 1024 bytes
                    data = conn.recv(1024).decode()
                    if not data:
                        # if data is not received break
                        break
                    print("from connected user: " + str(data))
                    data = input(' -> ')
                    conn.send(data.encode())  # send data to the client
                except UnicodeDecodeError:
                    conn.close()  # close the connection
                    break

    def log(self, msg: str, severity: int = 3):
        """
        If severity is high enough, print msg.
        """

        if severity >= self._log_severity:
            print("{}: {}".format(self.name, msg))

    def printParamList(self):
        # TODO: get this mess from some actuall pretty print function from Param class
        print("Parameter from {}".format(self.name))
        for parameter in self.paramList.parameters.values():
            print("Name: {}".format(parameter.name))
            print("\tType: {}".format(parameter.type_))
            print("\tInitial value: {}".format(parameter.init_val))
            print("\tRandSum: {}".format(parameter.randsum))
            print("\tRandSumStep: {}".format(parameter.randsumstep))
            print("\tRandMul: {}".format(parameter.randmul))
            print("\tRandMulStep: {}".format(parameter.randmulstep))

    @property
    def log_severity(self):
        return self._log_severity
    
    @log_severity.setter
    def log_severity(self, val):
        self._log_severity = val
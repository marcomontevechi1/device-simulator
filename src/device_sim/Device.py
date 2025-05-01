#!/usr/bin/env python3

import os
import socket
import threading
import re
import atexit

from .ParamList import ParamList
from .Param import BadArgType

DEVICES_LIST = []
PROTOCOL_PARSE = re.compile(r"(W|R|P):([a-zA-Z0-9_]+):([a-zA-Z0-9_]*)")


class Device(ParamList):
    """
    Simulates a device.
    """

    def __init__(
        self,
        name: str = None,
        param_source: dict = None,
        port: int = None,
        log_severity: int = 3,
        portfile_prefix: str = None,
    ):

        super().__init__(param_source)
        self.port = port
        self.sock = None
        self.name = name
        self._log_severity = log_severity
        self.portfile_prefix = portfile_prefix
        self.name_lock = threading.Lock()

        self.registerName()
        sockThread = threading.Thread(target=self.createSocket)
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
            n += 1

        self.name = "{}{}".format(self.name, n)
        DEVICES_LIST.append(self.name)
        self.name_lock.release()
        self.log("Added name {} to devices list.".format(self.name))

    def createSocket(self):
        """
        Creates socket. Binds to self.port if it's defined.
        Chooses a random port if not.
        """

        host = "0.0.0.0"
        port = 0
        if self.port:
            port = self.port

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        (self.host, self.port) = self.sock.getsockname()
        self.writeInfo()
        self.sock.listen()

        while True:

            conn, address = self.sock.accept()
            self.log("Connection from: " + str(address))

            while True:

                try:
                    # receive data stream. it won't accept data packet greater than 1024 bytes
                    data = conn.recv(1024).decode()
                    if not data:
                        # if data is not received break
                        break
                    self.log("From connected user: " + str(data), 2)
                    answer = self.reply(data)
                    conn.send(f"{answer}\n".encode())  # send data to the client
                    self.log("To connected user: " + answer, 2)
                except (UnicodeDecodeError, ConnectionResetError):
                    conn.close()  # close the connection
                    break

    def writeInfo(self):
        """
        Logs info about which server and port it's bound.
        If there is a file prefix to write, create file with device
        name and write <self.host:stlf.port> to it.
        """

        self.log("Bound socket to {}:{}".format(self.host, self.port))

        if self.portfile_prefix is None:
            return

        if not os.path.isdir(self.portfile_prefix):
            msg = "Provided path {} for portfile".format(self.portfile_prefix)
            msg += " is not a directory."
            raise Exception(msg)

        filepath = os.path.join(self.portfile_prefix, "{}.port".format(self.name))

        counter = 0
        while os.path.isfile(filepath):

            counter += 1
            filepath = os.path.join(
                self.portfile_prefix, "{}-{}.port".format(self.name, counter)
            )

        self.log(f"Writing address to file {filepath}")

        with open(filepath, "w") as file:
            file.write("{}:{}".format(self.host, self.port))
            atexit.register(
                lambda: os.remove(filepath) if os.path.exists(filepath) else None
            )

    def reply(self, data: str):
        """
        Tries to execute action.
        Replies with success or failure.
        Returns reply message.
        """

        ret = ""
        parameter = None

        try:
            action, param, val = self.parseProtocol(data)
        except Exception as e:
            return "E:BADPROTOCOLMATCH:"

        if (
            (action == "W" and val == "")
            or ((action == "R" or action == "P") and val != "")
            or (action == "P" and param not in ["S", "C"])
        ):
            return "E:BADCOMMAND:"

        if action == "P":
            if param == "S":
                self.printParamList()
                return "P:S:OK"
            else:
                msg = "Parameters from {}:\n".format(self.name)
                for parameter in self.parameters.values():
                    msg += "{}\n".format(parameter)
                return msg

        try:
            parameter = self.parameters[param]
        except KeyError:
            return "E:PARAMNOTFOUND:"

        if action == "R":
            return "R:{}:{}".format(param, parameter.value)

        try:
            parameter.value = val
        except BadArgType as b:
            ret += "E:BADARGTYPE:"

        return "S:{}:{}".format(param, parameter.value)

    def parseProtocol(self, data: str):
        """
        Matches protocol against pattern. Raises exception if not good.
        Returns action, parameter and value otherwise.
        """
        parsed = PROTOCOL_PARSE.match(str(data))

        try:
            action, param, val = parsed.group(1), parsed.group(2), parsed.group(3)
        except AttributeError as err:
            msg = "Protocol parse error. Message received:"
            msg += " {}. but protocol expects something that matches {}.".format(
                data, PROTOCOL_PARSE.pattern
            )
            msg += " Error: {}".format(err)
            raise Exception(msg)

        return str(action), str(param), str(val)

    def log(self, msg: str, severity: int = 3):
        """
        If severity is high enough, print msg.
        """

        if severity >= self._log_severity:
            print("{}: {}".format(self.name, msg))

    def printParamList(self):
        print("Parameters from {}: ".format(self.name))
        for parameter in self.parameters.values():
            print(parameter)

    @property
    def log_severity(self):
        return self._log_severity

    @log_severity.setter
    def log_severity(self, val):
        self._log_severity = val

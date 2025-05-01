#!/usr/bin/env python3

import yaml
from schema import Schema, Optional, Or
from .Device import Device

DeviceFile = Schema({
        "Devices": {
            str: {
                Optional("source"): str,
                Optional("port"): int,
                Optional("log"): int,
                Optional("portfile") : str,
                Optional("Params"): dict
            }
        }
    })

class DevicePool:
    """
    Class to manage creation of several devices.
    """

    def __init__(self, source: str | dict = None, number: int = 0, log_severity : int = 3, portfile_prefix : str = None):
        """
        source: dictionary or yaml file containing device definition. A dictionary with
                     format defined by DeviceFile.
        number: number of devices to be created. If provided together with
                source_file, creates all the devices in the source file plus 
                number more default devices.
        log_severity: default log severity for devices not from yaml file.
        portfile_prefix: directory in which to save files with <host>:<port> for devices not from yaml file.
        """
        
        self.number = number
        self.source = source
        self.log_severity = log_severity
        self.portfile_prefix = portfile_prefix
        self.devices = {}

        self.loadSource()
        self.createDevices()

    def loadSource(self):
        """
        Makes sure self.source is a dictionary.
        """

        if self.source is None:
            self.source = {}

        if isinstance(self.source, str):
            with open(self.source) as stream:
                local_src = yaml.safe_load(stream)
            self.source = local_src

            return
        
        if not isinstance(self.source, dict):
            raise Exception("Source is neither a valid string nor a dictionary. Source object: {}".format(self.source))

    def createDevices(self):
        """
        Creates and stores devices in self.devices
        If no source file is provided, creates self.number default devices.
        If only source is provided, creates devices described in source file.

        For each device, if both source and Params is provided, provide them as union
        of dictionaries to Device object.
        """

        for n in range(0, self.number):
            device = Device(log_severity = self.log_severity, portfile_prefix = self.portfile_prefix)
            self.devices[device.name] = device


        if len(self.source) != 0:
            DeviceFile.validate(self.source)
            for device, vals in self.source.items():
                params_source = vals.get("source")
                port = vals.get("port")
                log = vals.get("log")
                portfile = vals.get("portfile")
                params = {"Params": vals.get("Params")}

                if (params_source is not None) and (params is not None):
                    with open(params_source) as stream:
                        params_source = yaml.safe_load(params_source)

                dev = Device(name = device, param_source=params_source|params, port=port, log_severity=log, portfile_prefix = portfile)
                self.devices[dev.name] = dev
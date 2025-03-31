#!/usr/bin/env python3

import yaml

from .Param import Param

DEFAULT_PARAMS = {"Params": [{"name": "A", "type": "b"}, 
                             {"name": "B", "type": "a", "init": 10}, 
                             {"name": "C", "type": "a", "init": 10, "randsum": 0.5, "randmul": 0.2},
                             {"name": "D", "type": "s", "init": "mystring"}]}

def loadParamAttribute(param: dict, attribute):
    """
    Return None if key not found in dictionary
    """
    try:
        return param[attribute]
    except:
        return None

class ParamList:

    def __init__(self, source = None):
        """
        sources: a string containing the file path to a yaml file with the defined parameters or a dictionary
        containing the parameters definition.
        """

        self.source = source
        self.parameters = {}

        self.loadParamsSource()

    def loadParamsSource(self):
        """
        For each entry in  the parameter definition file/dictionary, create a parameter
        and append to self.parameters.
        """

        if self.source is None:
            self.source = DEFAULT_PARAMS

        if isinstance(self.source, str):
            with open(self.source) as stream:
                try:
                    local_src = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    self.log("Problem loading yaml file: {}".format(exc))
        elif isinstance(self.source, dict):
            local_src = self.source
        else:
            raise Exception("Parameters source must be string pointing to yaml source file or python dictionary.")
        
        self.loadParams(local_src)
        
    def loadParams(self, source: dict):
        """
        Checks if dictionary is in correct format and if all keys and values make sense.
        """

        if len(list(source.keys())) != 1 or "Params" not in list(source.keys()):
            err_msg += "Params dictionary is inadequate. Should have only one key called 'Params'. Has {} instead.\n".format(list(source.keys()))
            raise Exception(err_msg)

        if not isinstance(source["Params"], list):
            err_msg += "Params key should point to a list. It points instead to {}.\n".format(type(source["Params"]))
            raise Exception(err_msg)

        for parameter in source["Params"]:
            try:
                name = parameter["name"]
            except KeyError:
                raise Exception("Parameter without a name found! All parameters need a name.\n")
            type_ = loadParamAttribute(parameter, "type")
            init_val = loadParamAttribute(parameter, "init")
            randsum = loadParamAttribute(parameter, "randsum")
            randmul = loadParamAttribute(parameter, "randmul")
            randsumstep = loadParamAttribute(parameter, "randsumstep")
            randmulstep = loadParamAttribute(parameter, "randmulstep")
            self.parameters[name] = ( Param(name = name, typ = type_, init_val = init_val, randmul = randmul,
                                          randmulstep = randmulstep, randsum = randsum, randsumstep = randsumstep) )
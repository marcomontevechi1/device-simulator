#!/usr/bin/env python3

from enum import StrEnum
import random

STRING_TO_BOOL = {"true": True, "1": True, "false": False, "0": False}

DEFAULTS = {"randsum": 0.1,
            "randmul": 0.1}

class BadArgType(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class ParamType(StrEnum):
    binary = "b"
    analog = "a"
    integer = "i"
    string = "s"

class Param:

    def __init__(self, name: str = None, typ: ParamType = ParamType.analog, init_val = None, 
                 randsum: float = DEFAULTS["randsum"], randmul: float = DEFAULTS["randmul"]):
        """
        typ: Parameter type. Should be one of ParamType options.
        init_val: Initial value. Will assume default value if not provided.
        randsum: Random interval from which to get number to sum when value is gotten. 
                 Is simmetrical around 0. Defaults to 0. 
                 Only used if type is int or float.
        randmul: Random interval from which to get number to multiply when value is gotten. 
                 Is simmetrical around 1. Defaults to 1.
                 Only used if type is int or float.
        """

        if name == None:
            raise Exception("Parameter needs a name! name = None is not acceptable.\n")

        self.name = name
        self.type_ = ParamType(typ)
        self.init_val = init_val
        self._value = init_val
        self.randsum = randsum
        self.randmul = randmul

        self.initRand()
        self.parseTypeAndVal()

    def initRand(self):
        """
        Initialize default values to random fluctuation parameters
        """
        if self.randmul == None: self.randmul = DEFAULTS["randmul"]
        if self.randsum == None: self.randsum = DEFAULTS["randsum"]

    @property
    def value(self):
        if self.type_ in [ParamType.integer, ParamType.analog]:
            self._value = self._value*random.uniform(1 - self.randmul, 
                                                     1 + self.randmul) + random.uniform(- self.randsum, self.randsum)
        return self._value
    
    @value.setter
    def value(self, val):
        try:
            if self.type_ in [ParamType.integer, ParamType.analog]:
                self._value = float(val)
            elif self.type_ == ParamType.binary:
                if isinstance(val, str):
                    self._value = STRING_TO_BOOL[val.lower()]
                else:
                    self._value = bool(val)
            elif self.type_ == ParamType.string:
                self._value = str(val)
        except:
            raise BadArgType("Bad value type {}. Should be {}.".format(type(val), self.type_))

    def parseTypeAndVal(self):
        """
        Makes sure type and initial value make sense.
        """

        types_per_val = {ParamType.binary: bool, ParamType.analog: (float,int), 
                        ParamType.integer: int,  ParamType.string: str}
        initial_vals = {ParamType.binary: False, ParamType.analog: 0, 
                         ParamType.integer: 0,   ParamType.string: ""}

        if not self._value:
            self._value = initial_vals[self.type_]

        if not isinstance(self._value, types_per_val[self.type_]):
            msg = "Initial value {} not allowed for type {}!".format(self._value, self.type_)
            raise Exception(msg)

    def __str__(self):
        string = f"Name: {self.name}\n\ttype: {self.type_}\n\tcurrent value: {self._value}\n\t"
        string += f"initial value: {self.init_val}\n\trandsum: {self.randsum}\n\trandmul: {self.randmul}"
        return string
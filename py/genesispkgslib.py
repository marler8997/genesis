#
# This file contains helper functions/definitions
# to create genesis package definitions.
#
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import log

class Config:
    def __init__(self):
        self.map = {}

    def try_get(self, name):
        return self.map.get(name)
    def get(self, name):
        result = self.try_get(name)
        if not result:
            log.flushall()
            raise Exception("Error: undefined config '{}'".format(name))
        return result

    def set(self, name, value):
        existing = self.map.get(name)
        if existing != None:
            log.log("Error: multiple values have been set to config property '{}':".format(name))
            log.log("  current '{}'".format(existing))
            log.log("  new     '{}'".format(value))
            sys.exit(1)
        self.map[name] = value

#
# Helper Functions
#
def select(cond,true,false):
    return true if cond else false

def kwselect(key,**kwargs):
    value = kwargs.get(key)
    if value == None:
        raise Exception("undefined keyword arg '{}'".format(key))
    return value

def make_rpath(*ins):
    result = ''
    prefix = ''
    for in_name in ins:
        result += "{}@in.{}/lib".format(prefix, in_name)
        prefix = ':'
    return result
def make_rpath2(*ins):
    result = ''
    prefix = ''
    for in_name in ins:
        result += "{}@{}/lib".format(prefix, in_name)
        prefix = ':'
    return result

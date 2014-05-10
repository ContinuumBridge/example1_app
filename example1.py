#!/usr/bin/env python
# example1.py
"""
Copyright (c) 2014 ContinuumBridge Limited

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
ModuleName = "example1" 
SET_TEMP = 21.0

import sys
import os.path
import time
import logging
from cbcommslib import CbApp
from cbconfig import *

class App(CbApp):
    def __init__(self, argv):
        logging.basicConfig(filename=CB_LOGFILE,level=CB_LOGGING_LEVEL,format='%(asctime)s %(message)s')
        # The following 3 declarations must be made
        CbApp.processAdaptor = self.processAdaptor
        CbApp.appConfigure = self.configure
        CbApp.processConcentrator = self.processConcentrator
        #
        self.state = "stopped"
        self.sensorID = ""
        self.switchID = ""
        #CbApp.__init__ MUST be called
        CbApp.__init__(self, argv)

    def states(self, action):
        self.state = action
        msg = {"id": self.id,
               "status": "state",
               "state": self.state}
        self.cbSendManagerMsg(msg)

    def processServices(self, message):
        for p in message["services"]:
            if p["parameter"] == "temperature":
                self.sensorID = message["id"]
                req = {"id": self.id,
                      "req": "services",
                      "services":[
                                 "parameter": "temperature",
                                 "interval": 30.0
                                 ]
                      }
                self.cbSendMsg(req, self.message["id"])
            elif p["parameter"] == "switch":
                self.switchID = message["id"]

    def processAdaptor(self, message):
        if message["content"] == "services":
            self.processServices(message)
        elif message["id"] = self.sensorID:
            command = {"id": self.id,
                       "content": "command"}
        if message["content"] == "temperature":
            if message["data"] > SET_TEMP + 0.2:
                command["data"] = "off"
                self.cbSendMsg(command, self.switchID)
            elif message["data"] < SET_TEMP - 0.2:
                command["data"] = "on"
                self.cbSendMsg(command, self.switchID)
            elif message["id"] == self.switchID:
                self.switchState = message["body"]

    def configure(self, config):
        self.states("starting")

if __name__ == '__main__':
    app = App(sys.argv)

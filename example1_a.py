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
SET_TEMP = 22.5

import sys
import os.path
import time
import logging
from cbcommslib import CbApp
from cbconfig import *

class App(CbApp):
    def __init__(self, argv):
        logging.basicConfig(filename=CB_LOGFILE,level=CB_LOGGING_LEVEL,format='%(asctime)s %(message)s')
        self.appClass = "control"
        self.state = "stopped"
        self.gotSwitch = False
        self.sensorID = ""
        self.switchID = ""
        # Temporary botch - set temperature from a file
        try:
            tempFile = CB_CONFIG_DIR + 'set-temp'
            with open(tempFile, 'r') as f:
                s = f.read()
            if s.endswith('\n'):
                s = s[:-1]
            SET_TEMP = s
            logging.debug("%s Set temperature: %s", ModuleName, SET_TEMP)
        except:
            logging.debug("%s Could not read set-temp file", ModuleName)
        #CbApp.__init__ MUST be called
        CbApp.__init__(self, argv)

    def setState(self, action):
        self.state = action
        msg = {"id": self.id,
               "status": "state",
               "state": self.state}
        self.sendManagerMessage(msg)

    def onAdaptorService(self, message):
        for p in message["service"]:
            if p["characteristic"] == "temperature":
                self.sensorID = message["id"]
                req = {"id": self.id,
                      "request": "service",
                      "service": [
                                    {"characteristic": "temperature",
                                     "interval": 30.0}
                                 ]
                      }
                self.sendMessage(req, message["id"])
                logging.debug("%s onadaptorservice, req: %s", ModuleName, req)
            elif p["characteristic"] == "switch":
                self.switchID = message["id"]
                self.gotSwitch = True
                logging.debug("%s switchID: %s", ModuleName, self.switchID)
        self.setState("running")

    def onAdaptorData(self, message):
        if message["id"] == self.sensorID:
            if self.gotSwitch:
                command = {"id": self.id,
                           "request": "command"}
                if message["characteristic"] == "temperature":
                    logging.debug("%s %s Temperature = %s", ModuleName, self.id, message["data"])
                    if message["data"] > SET_TEMP + 0.2:
                        command["data"] = "off"
                        logging.debug("%s %s Switching off", ModuleName, self.id)
                        self.sendMessage(command, self.switchID)
                    elif message["data"] < SET_TEMP - 0.2:
                        command["data"] = "on"
                        logging.debug("%s %s Switching on", ModuleName, self.id)
                        self.sendMessage(command, self.switchID)
            else:
                logging.debug("%s Trying to process temperature before switch connected", ModuleName)
        elif message["id"] == self.switchID:
            self.switchState = message["body"]

    def onConfigureMessage(self, config):
        self.setState("starting")

if __name__ == '__main__':
    app = App(sys.argv)

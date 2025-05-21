from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import os
import datetime

import sb.component
from sb.helpers import logPrint

class RecordingController(sb.component.Component):
    def description():
        return "Handle raw data recording"
    
    def __init__(self, cfg, data, callbacks):
        super().__init__(cfg, data, callbacks)

    def defaultTitle(self):
        return "Raw data"

    def getWidget(self):
        return None

    def actions():
        return {
                "toggleRecording":"Toggle raw data recording",
               }
    
    def toggleRecording(self):
        logPrint("toggleRecording")
        if self.cfg.recordingEnabled or self.cfg.developmentMode:
            if self.data.isRecording:
                self.data.isRecording = False
                self.data.receiver.stopRecording()
            else:
                if not os.path.exists(self.cfg.storageLocation):
                    self.callbacks.showUiMsg("Error: Storage location\n'" + self.storageLocation[self.cfg.storageLocation.rfind("/")+1:] + "'\ndoes not exist", 2)
                    return
                prefix = self.cfg.storageLocation + "/"
                if self.cfg.developmentMode:
                    prefix += "debug/"
                if len(self.cfg.sessionName) > 0:
                    prefix += self.cfg.sessionName + "-"
                self.data.receiver.startRecording(prefix)#, not self.cfg.developmentMode)
                self.data.isRecording = True

    def callAction(self, a):
        if a == "toggleRecording":
            self.toggleRecording()

sb.component.componentLibrary['RecordingController'] = RecordingController

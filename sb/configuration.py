from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import os
import json

class Configuration:
    def __init__(self):
        pass

    def saveConstants(self):
        settings = QSettings()

        settings.setValue("fontScale", self.fontScale)
        settings.setValue("lapDecimals", self.lapDecimals)
        settings.setValue("showOptimalLap", self.showOptimalLap)
        settings.setValue("showBestLap", self.showBestLap)
        settings.setValue("showMedianLap", self.showMedianLap)
        settings.setValue("showLastLap", self.showLastLap)

        settings.setValue("showRefALap", self.showRefALap)
        settings.setValue("showRefBLap", self.showRefBLap)
        settings.setValue("showRefCLap", self.showRefCLap)
        settings.setValue("refAFile", self.refAFile)
        settings.setValue("refBFile", self.refBFile)
        settings.setValue("refCFile", self.refCFile)
        
        settings.setValue("recordingEnabled", self.recordingEnabled)
        settings.setValue("messagesEnabled", self.messagesEnabled)

        settings.setValue("storageLocation", self.storageLocation)

        settings.setValue("speedcomp", self.speedcomp)
        settings.setValue("linecomp", self.linecomp)
        settings.setValue("timecomp", self.timecomp)
        settings.setValue("loadMessagesFromFile", self.loadMessagesFromFile)
        settings.setValue("messageFile", self.messageFile)

        settings.setValue("brakepoints", self.brakepoints)
        settings.setValue("throttlepoints", self.throttlepoints)
        settings.setValue("countdownBrakepoint", self.countdownBrakepoint)
        settings.setValue("bigCountdownTarget", self.bigCountdownBrakepoint)
        settings.setValue("switchToBestLap", self.switchToBestLap)

        settings.sync()

    def loadConstants(self):
        self.foregroundColor = QColor("#FFF")
        self.backgroundColor = QColor("#222")
        self.brightBackgroundColor = QColor("#333")

        self.warningColor1 = QColor("#f00")
        self.warningColor2 = QColor("#ff0")
        self.advanceWarningColor = QColor("#f80")

        self.countdownColor3 = QColor("#22F")
        self.countdownColor2 = QColor("#2FF")
        self.countdownColor1 = QColor("#FFF")

        self.tyreTempMinHue = 0
        self.tyreTempMaxHue = 0.667
        self.tyreTempCenterHue = 0.5 * (self.tyreTempMaxHue + self.tyreTempMinHue)
        self.tyreTempCenter = 70
        self.tyreTempSpread = 16.6667
        self.tyreTempSaturation = 1
        self.tyreTempValue = 1

        self.brakeColorHue = 0
        self.brakeColorSaturation = 1
        self.brakeColorMinValue = 0x22/0xff

        self.brakeMinimumLevel = 0.1

        self.circuitExperienceEndPointPurgeDistance = 15
        self.circuitExperienceShortLapSecondsThreshold = 10
        self.circuitExperienceNoThrottleTimeout = 10
        self.circuitExperienceJumpDistance = 10

        self.validLapEndpointDistance = 20

        self.fuelStatisticsLaps = 5
        self.fuelLastLapFactor = 0.667

        self.messageDisplayDistance = 100
        self.messageAdvanceTime = 5
        self.messageBlinkingPhase = 100000

        self.mapCurrentColor = QColor("#F00")
        self.mapStandingColor = QColor("#000")

        self.speedDiffMinHue = 0
        self.speedDiffMaxHue = 120/360
        self.speedDiffCenterHue = 0.5 * (self.speedDiffMaxHue + self.speedDiffMinHue)
        self.speedDiffColorSaturation = 1
        self.speedDiffColorValue = 1
        self.speedDiffSpread = 10

        self.closestPointValidDistance = 15
        self.closestPointGetAwayDistance = 20
        self.closestPointCancelSearchDistance = 500

        self.pollInterval = 20

        self.fontScale = 1

        self.fontSizeVerySmallPreset = 32
        self.fontSizeSmallPreset = 48
        self.fontSizeNormalPreset = 64
        self.fontSizeLargePreset = 72

        self.psFPS = 59.94

        if os.path.exists("gt7speedboardinternals.json"):
            with open("gt7speedboardinternals.json", "r") as f:
                j = f.read()
            d = json.loads(j)

            if "foregroundColor" in d: self.foregroundColor = QColor(d["foregroundColor"])
            if "backgroundColor" in d: self.backgroundColor = QColor(d["backgroundColor"])
            if "brightBackgroundColor" in d: self.brightBackgroundColor = QColor(d["brightBackgroundColor"])

            if "warningColor1" in d: self.warningColor1 = QColor(d["warningColor1"])
            if "warningColor2" in d: self.warningColor2 = QColor(d["warningColor2"])
            if "advanceWarningColor" in d: self.advanceWarningColor = QColor(d["advanceWarningColor"])

            if "countdownColor3" in d: self.countdownColor3 = QColor(d["countdownColor3"])
            if "countdownColor2" in d: self.countdownColor2 = QColor(d["countdownColor2"])
            if "countdownColor1" in d: self.countdownColor1 = QColor(d["countdownColor1"])

            if "tyreTempMinHue" in d: self.tyreTempMinHue = d["tyreTempMinHue"]
            if "tyreTempMaxHue" in d: self.tyreTempMaxHue = d["tyreTempMaxHue"]
            if "tyreTempCenterHue" in d: self.tyreTempCenterHue = d["tyreTempCenterHue"]
            if "tyreTempCenter" in d: self.tyreTempCenter = d["tyreTempCenter"]
            if "tyreTempSpread" in d: self.tyreTempSpread = d["tyreTempSpread"]
            if "tyreTempSaturation" in d: self.tyreTempSaturation = d["tyreTempSaturation"]
            if "tyreTempValue" in d: self.tyreTempValue = d["tyreTempValue"]

            if "brakeColorHue" in d: self.brakeColorHue = d["brakeColorHue"]
            if "brakeColorSaturation" in d: self.brakeColorSaturation = d["brakeColorSaturation"]
            if "brakeColorMinValue" in d: self.brakeColorMinValue = d["brakeColorMinValue"]

            if "brakeMinimumLevel" in d: self.brakeMinimumLevel = d["brakeMinimumLevel"]

            if "circuitExperienceEndPointPurgeDistance" in d: self.circuitExperienceEndPointPurgeDistance = d["circuitExperienceEndPointPurgeDistance"]
            if "circuitExperienceShortLapSecondsThreshold" in d: self.circuitExperienceShortLapSecondsThreshold = d["circuitExperienceShortLapSecondsThreshold"]
            if "circuitExperienceNoThrottleTimeout" in d: self.circuitExperienceNoThrottleTimeout = d["circuitExperienceNoThrottleTimeout"]
            if "circuitExperienceJumpDistance" in d: self.circuitExperienceJumpDistance = d["circuitExperienceJumpDistance"]

            if "validLapEndpointDistance" in d: self.validLapEndpointDistance = d["validLapEndpointDistance"]

            if "fuelStatisticsLaps" in d: self.fuelStatisticsLaps = d["fuelStatisticsLaps"]
            if "fuelLastLapFactor" in d: self.fuelLastLapFactor = d["fuelLastLapFactor"]

            if "messageDisplayDistance" in d: self.messageDisplayDistance = d["messageDisplayDistance"]
            if "messageAdvanceTime" in d: self.messageAdvanceTime = d["messageAdvanceTime"]
            if "messageBlinkingPhase" in d: self.messageBlinkingPhase = d["messageBlinkingPhase"]

            if "mapCurrentColor" in d: self.mapCurrentColor = QColor(d["mapCurrentColor"])
            if "mapStandingColor" in d: self.mapStandingColor = QColor(d["mapStandingColor"])

            if "speedDiffMinHue" in d: self.speedDiffMinHue = d["speedDiffMinHue"]
            if "speedDiffMaxHue" in d: self.speedDiffMaxHue = d["speedDiffMaxHue"]
            if "speedDiffCenterHue" in d: self.speedDiffCenterHue = d["speedDiffCenterHue"]
            if "speedDiffColorSaturation" in d: self.speedDiffColorSaturation = d["speedDiffColorSaturation"]
            if "speedDiffColorValue" in d: self.speedDiffColorValue = d["speedDiffColorValue"]
            if "speedDiffSpread" in d: self.speedDiffSpread = d["speedDiffSpread"]

            if "closestPointValidDistance" in d: self.closestPointValidDistance = d["closestPointValidDistance"]
            if "closestPointGetAwayDistance" in d: self.closestPointGetAwayDistance = d["closestPointGetAwayDistance"]
            if "closestPointCancelSearchDistance" in d: self.closestPointCancelSearchDistance = d["closestPointCancelSearchDistance"]

            if "pollInterval" in d: self.pollInterval = d["pollInterval"]

            #if "fontScale" in d: self.fontScale = d["fontScale"]
            if "fontSizeVerySmall" in d: self.fontSizeVerySmallPreset = d["fontSizeVerySmall"]
            if "fontSizeSmall" in d: self.fontSizeSmallPreset = d["fontSizeSmall"]
            if "fontSizeNormal" in d: self.fontSizeNormalPreset = d["fontSizeNormal"]
            if "fontSizeLarge" in d: self.fontSizeLargePreset = d["fontSizeLarge"]

            if "playStationFPS" in d: self.psFPS = d["playStationFPS"]

        if False: # write default file, only activate on demand
            d = {}
            d["foregroundColor"] = self.foregroundColor.name()
            d["backgroundColor"] = self.backgroundColor.name()
            d["brightBackgroundColor"] = self.brightBackgroundColor.name()

            d["warningColor1"] = self.warningColor1.name()
            d["warningColor2"] = self.warningColor2.name()
            d["advanceWarningColor"] = self.advanceWarningColor.name()

            d["countdownColor3"] = self.countdownColor3.name()
            d["countdownColor2"] = self.countdownColor2.name()
            d["countdownColor1"] = self.countdownColor1.name()

            d["tyreTempMinHue"] = self.tyreTempMinHue
            d["tyreTempMaxHue"] = self.tyreTempMaxHue
            d["tyreTempCenterHue"] = self.tyreTempCenterHue
            d["tyreTempCenter"] = self.tyreTempCenter
            d["tyreTempSpread"] = self.tyreTempSpread
            d["tyreTempSaturation"] = self.tyreTempSaturation
            d["tyreTempValue"] = self.tyreTempValue

            d["brakeColorHue"] = self.brakeColorHue
            d["brakeColorSaturation"] = self.brakeColorSaturation
            d["brakeColorMinValue"] = self.brakeColorMinValue

            d["brakeMinimumLevel"] = self.brakeMinimumLevel

            d["circuitExperienceEndPointPurgeDistance"] = self.circuitExperienceEndPointPurgeDistance
            d["circuitExperienceShortLapSecondsThreshold"] = self.circuitExperienceShortLapSecondsThreshold
            d["circuitExperienceNoThrottleTimeout"] = self.circuitExperienceNoThrottleTimeout
            d["circuitExperienceJumpDistance"] = self.circuitExperienceJumpDistance

            d["validLapEndpointDistance"] = self.validLapEndpointDistance

            d["fuelStatisticsLaps"] = self.fuelStatisticsLaps
            d["fuelLastLapFactor"] = self.fuelLastLapFactor

            d["messageDisplayDistance"] = self.messageDisplayDistance
            d["messageAdvanceTime"] = self.messageAdvanceTime
            d["messageBlinkingPhase"] = self.messageBlinkingPhase

            d["mapCurrentColor"] = self.mapCurrentColor.name()
            d["mapStandingColor"] = self.mapStandingColor.name()

            d["speedDiffMinHue"] = self.speedDiffMinHue
            d["speedDiffMaxHue"] = self.speedDiffMaxHue
            d["speedDiffCenterHue"] = self.speedDiffCenterHue
            d["speedDiffColorSaturation"] = self.speedDiffColorSaturation
            d["speedDiffColorValue"] = self.speedDiffColorValue
            d["speedDiffSpread"] = self.speedDiffSpread

            d["closestPointValidDistance"] = self.closestPointValidDistance
            d["closestPointGetAwayDistance"] = self.closestPointGetAwayDistance
            d["closestPointCancelSearchDistance"] = self.closestPointCancelSearchDistance

            d["pollInterval"] = self.pollInterval

            #d["fontScale"] = self.fontScale
            d["fontSizeVerySmall"] = self.fontSizeVerySmallPreset
            d["fontSizeSmall"] = self.fontSizeSmallPreset
            d["fontSizeNormal"] = self.fontSizeNormalPreset
            d["fontSizeLarge"] = self.fontSizeLargePreset

            d["playStationFPS"] = self.psFPS
            
            j = json.dumps(d, indent=4)
            with open("gt7speedboardinternals.json", "w") as f:
                f.write(j)

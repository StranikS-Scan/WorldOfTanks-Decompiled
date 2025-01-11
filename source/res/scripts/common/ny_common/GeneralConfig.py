# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/GeneralConfig.py
from ny_common.settings import NYGeneralConsts
from random import randint
from typing import Tuple, Optional

class GeneralConfig(object):

    def __init__(self, config):
        self._config = config

    def getAtmosphereLevelLimits(self):
        return self._config.get(NYGeneralConsts.ATMOSPHERE_LEVEL_LIMITS)

    def calculateAtmosphereLevel(self, atmPoints):
        return self.calculateLevelByPoints(atmPoints)

    def getAtmosphereProgress(self, totalPoints):
        atmosphereLimits = self.getAtmosphereLevelLimits()
        for level, bound in enumerate(atmosphereLimits):
            if totalPoints < bound:
                prevBound = atmosphereLimits[level - 1]
                return (totalPoints - prevBound, bound - prevBound)

        finalDelta = atmosphereLimits[-1] - atmosphereLimits[-2]
        return (finalDelta, finalDelta)

    def calculateLevelByPoints(self, totalPoints):
        levelLimits = self.getAtmosphereLevelLimits()
        for level, bound in enumerate(levelLimits):
            if totalPoints < bound:
                return level

        return len(levelLimits)

    def getMaxLevelLimit(self):
        levelLimits = self.getAtmosphereLevelLimits()
        return levelLimits[-1] if levelLimits else 0

    def getResourceConverterCoefficients(self):
        return self._config.get(NYGeneralConsts.RESOURCE_CONVERTER_COEFFICIENTS)

    def calculateReceivedValueByInitial(self, initialValue):
        initialValueCoeff, receivedValueCoeff = self.getResourceConverterCoefficients()
        return int(initialValue // initialValueCoeff * receivedValueCoeff)

    def calculateInitialValueByReceived(self, receivedValue):
        initialValueCoeff, receivedValueCoeff = self.getResourceConverterCoefficients()
        return int(receivedValue // receivedValueCoeff * initialValueCoeff)

    def getHangarNameRerollToken(self):
        return self._config.get(NYGeneralConsts.HANGAR_NAME_REROLL_TOKEN)

    def getHangarNameSetToken(self):
        return self._config.get(NYGeneralConsts.HANGAR_NAME_SET_TOKEN)

    def getEventStartTime(self):
        return self._config[NYGeneralConsts.EVENT_START_TIME]

    def getEventEndTime(self):
        return self._config.get(NYGeneralConsts.EVENT_END_TIME)

    def getFriendServiceEnabled(self):
        return self._config.get(NYGeneralConsts.FRIEND_SERVICE_ENABLED)

    def getFriendServiceRequestDelay(self):
        return self._config.get(NYGeneralConsts.FRIEND_SERVICE_REQUEST_DELAY)

    def getMaxNameTitleID(self):
        return self._config[NYGeneralConsts.MAX_NAME_TITLE_ID]

    def getMaxNameDescriptionID(self):
        return self._config[NYGeneralConsts.MAX_NAME_DESCRIPTION_ID]

    def getRandomNameIDs(self):
        return (randint(1, self.getMaxNameTitleID()), randint(1, self.getMaxNameDescriptionID()))

    def getSurpriseToken(self):
        return self._config.get(NYGeneralConsts.SURPRISE_TOKEN)

    @staticmethod
    def makeHangarNameMask(titleID, descriptionID):
        return (descriptionID << 16) + titleID

    @staticmethod
    def parseHangarNameMask(hangarNameMask):
        titleID = hangarNameMask & 65535
        descriptionID = hangarNameMask >> 16 & 65535
        return (titleID, descriptionID)

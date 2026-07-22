# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/skeletons/sub_controllers.py
import typing
if typing.TYPE_CHECKING:
    from typing import List, Optional, Tuple, Dict, Any
    from gui.server_events.event_items import Quest

class ITanksBirthdayProgressionSubController(object):

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def parseQuests(self):
        raise NotImplementedError

    @property
    def progressionConfig(self):
        raise NotImplementedError

    def __parseEventData(self, eventData):
        raise NotImplementedError

    @staticmethod
    def isBirthdayProgressionQuest(qID):
        raise NotImplementedError

    @staticmethod
    def getProgressionPointsRequiredFromQuest(questData):
        raise NotImplementedError

    def __onEventsDataUpdated(self, diff):
        raise NotImplementedError

    def __onTokensUpdate(self, diff):
        raise NotImplementedError

    def getProgressionTokensCount(self):
        raise NotImplementedError

    def isInfinityLevel(self):
        raise NotImplementedError

    def getCurrentProgressionLevel(self):
        raise NotImplementedError

    def getLevelByPoints(self, points):
        raise NotImplementedError

    def getInfinityLevel(self):
        raise NotImplementedError

    def getSimpleLevels(self):
        raise NotImplementedError


class IGiftSystemSubController(object):

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def isGiftEventActive(self):
        raise NotImplementedError

    def getStampCount(self, stampName):
        raise NotImplementedError

    def getSimpleStampCount(self):
        raise NotImplementedError

    def getSpecialStampCount(self):
        raise NotImplementedError

    def getExpirationTime(self):
        raise NotImplementedError

    def getMagicPercent(self):
        raise NotImplementedError

    def getAllowMultipleSendCount(self):
        raise NotImplementedError

    def getLimitResetTime(self):
        raise NotImplementedError

    def isAlreadyReceivedGift(self, playerID):
        raise NotImplementedError

    def getKeeper(self):
        raise NotImplementedError

    def getGifter(self):
        raise NotImplementedError

    def getStamper(self):
        raise NotImplementedError

    def getMessenger(self):
        raise NotImplementedError

    def sendGifts(self, stampType, receiversIDs, messageIdx, callback=None):
        raise NotImplementedError

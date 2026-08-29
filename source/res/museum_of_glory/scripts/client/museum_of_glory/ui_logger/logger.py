# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/ui_logger/logger.py
import json
import math
import sys
from collections import defaultdict
from helpers.time_utils import getCurrentTimestamp
from museum_of_glory.museum_of_glory_constants import AUDIO_GUIDE_ENABLED
from museum_of_glory.ui_logger.tank_item import TankItem
from museum_of_glory_account_settings import getMuseumOfGlorySetting
from uilogging.base.logger import _BaseLogger as Logger
from uilogging.constants import LogLevels
_FEATURE = 'museum_of_glory'
_GROUP = 'museum_of_glory'
_ACTION = 'museum_closed'
_VOICEOVER_KEY = 'voiceoverEnabled'
_VIEW_TIME_KEY = 'viewTimeSec'
_TANKS_KEY = 'tanks'
_AUDIO_GUIDE_KEY = 'audioGuideCount'

class MuseumLogger(Logger):
    __slots__ = ('__rawJsonData', '__isLogged', '__viewOpenTime', '__excursionStartIndex')

    def __init__(self):
        super(MuseumLogger, self).__init__(feature=_FEATURE, group=_GROUP)
        self.__rawJsonData = {_VOICEOVER_KEY: getMuseumOfGlorySetting(AUDIO_GUIDE_ENABLED),
         _VIEW_TIME_KEY: 0,
         _AUDIO_GUIDE_KEY: 0,
         _TANKS_KEY: defaultdict(TankItem)}
        self.__rawJsonData = self.getEmptyConfig()
        self.__isLogged = False
        self.__excursionStartIndex = sys.maxint
        self.__viewOpenTime = getCurrentTimestamp()

    @staticmethod
    def getEmptyConfig():
        return {_VOICEOVER_KEY: getMuseumOfGlorySetting(AUDIO_GUIDE_ENABLED),
         _VIEW_TIME_KEY: 0,
         _AUDIO_GUIDE_KEY: 0,
         _TANKS_KEY: defaultdict(TankItem)}

    def log(self):
        if self.__isLogged:
            return
        self.__rawJsonData[_VIEW_TIME_KEY] = int(math.ceil(getCurrentTimestamp() - self.__viewOpenTime))
        self._log(action=_ACTION, loglevel=LogLevels.NOTSET, json_data=json.dumps(self.__rawJsonData))
        self.__isLogged = True

    def setVoiceoverEnabled(self, state):
        self.__rawJsonData[_VOICEOVER_KEY] = state

    def increaseTankClickCount(self, tankName):
        self.__rawJsonData[_TANKS_KEY][tankName].increaseClickCount()

    def updateTankVoiceoverTime(self, tankName, duration):
        if tankName not in self.__rawJsonData[_TANKS_KEY]:
            return
        self.__rawJsonData[_TANKS_KEY][tankName].updateVoiceoverTime(duration)

    def setAudioGuideInitialIndex(self, index):
        self.__excursionStartIndex = index

    def updateAudioGuideCount(self, currentIndex):
        count = max(currentIndex - self.__excursionStartIndex, 0)
        self.__rawJsonData[_AUDIO_GUIDE_KEY] = max(self.__rawJsonData[_AUDIO_GUIDE_KEY], count)

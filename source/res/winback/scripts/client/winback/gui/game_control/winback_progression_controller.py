# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/game_control/winback_progression_controller.py
import logging
import typing
import Event
from account_helpers.AccountSettings import Winback
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from shared_utils import first
from winback.gui.impl.lobby.views.winback_bonus_packer import getWinbackBonuses
from winback.gui.winback_helpers import getWinbackSetting, setWinbackSetting
from winback.gui.shared.event_dispatcher import fireUpdateVOHeaderEvent
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)

class WinbackQuests(object):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.questsIds = {}

    def getQuests(self):
        return self.__eventsCache.getAllQuests(self._filterFunc)

    def getAvailableQuests(self):
        return self.__eventsCache.getAllQuests(self._availableFilterFunc)

    def setQuestsIds(self, questsIds):
        self.questsIds = questsIds

    def hasQuestId(self, questsId):
        return questsId in self.questsIds

    def _filterFunc(self, quest):
        return quest.getID() in self.questsIds

    def _availableFilterFunc(self, quest):
        return quest.getID() in self.questsIds and (quest.isCompleted() or quest.accountReqs.isAvailable())


class WinbackProgressionController(object):
    __eventsCache = dependency.descriptor(IEventsCache)
    PREV_POINTS_ACC_SETTINGS_KEY = Winback.WINBACK_PROGRESSION_POINTS_SEEN
    PROGRESSION_FILTER_FUNC_KEY = 'WinbackFuncKey'

    def __init__(self, winbackController):
        self.__stages = []
        self.__stageRatings = []
        self.__pointsForLevel = 0
        self.__isEnabled = False
        self.__winbackController = winbackController
        self.questContainer = WinbackQuests()
        self.onProgressPointsUpdated = Event.Event()
        self.onGiftTokenUpdated = Event.Event()
        self.onSettingsChanged = Event.Event()

    def init(self):
        self.__addListeners()

    def fini(self):
        self.__stages = None
        self.__stageRatings = None
        self.__clearListeners()
        self.onProgressPointsUpdated.clear()
        self.onGiftTokenUpdated.clear()
        self.onSettingsChanged.clear()
        return

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def isFinished(self):
        return False if not self.isEnabled else self.getCurPoints() >= self._getPointsForLevel() * len(self.__stages)

    def __onTokensUpdate(self, tokens):
        if self.__winbackController.progressionToken in tokens:
            self.onProgressPointsUpdated()
        if any((self.__winbackController.isWinbackOfferToken(token) and token.endswith('_gift') for token in tokens)):
            self.onGiftTokenUpdated()

    def setSettings(self, settings, isProgressionSwitched):
        self.__stages = sorted([ stage for stage in settings.get('awardList', []) if stage[0] is not None ], key=lambda s: s[0])
        self.__stageRatings = [ stage[0] for stage in self.__stages ]
        self.__pointsForLevel = first(self.__stageRatings, 0)
        self.__isEnabled = bool(self.__stages) and settings.get('isProgressionEnabled', False)
        questsIds = settings.get('questIds', ())
        self.questContainer.setQuestsIds(questsIds)
        filterFunc = lambda quest: quest.getID() in questsIds
        self.__eventsCache.questsProgress.addFilterFunc(filterFunc, key=self.PROGRESSION_FILTER_FUNC_KEY)
        fireUpdateVOHeaderEvent()
        self.onSettingsChanged(isProgressionSwitched)
        return

    def getProgressionData(self):
        currentPoints = self.getCurPoints()
        previousPoints = self.getPrevPoints()
        return {'currentPoints': currentPoints,
         'pointsForLevel': self._getPointsForLevel(),
         'previousPoints': previousPoints,
         'progressionLevels': self.getProgressionLevelsData()}

    def getBattleQuestData(self):
        return self.questContainer.getAvailableQuests()

    def getCurrentStage(self):
        points = self.getCurPoints()
        currentStage = 1
        for stageRating in self.__stageRatings:
            if points < stageRating:
                break
            currentStage += 1

        return currentStage

    @property
    def isLastStage(self):
        currentStage = self.getCurrentStage()
        return currentStage == len(self.__stages)

    def getProgressionLevelsData(self):
        result = []
        for stageAwards in zip(*self.__stages)[1]:
            bonuses = getWinbackBonuses(stageAwards)
            result.append({'rewards': bonuses})

        return result

    def getTokensIdsByRewardFromLevel(self, level):
        if level < 1:
            return None
        else:
            stages = self.__stages
            if level > len(stages):
                return []
            _, bonuses = stages[level - 1]
            return [ tokenID.replace('_gift', '') for tokenID in bonuses.get('tokens', {}).keys() ]

    def saveCurPoints(self):
        self._cachePoints(self.getCurPoints())

    def getPrevPoints(self):
        return self._getCachedPoints()

    def getCurPoints(self):
        return self.__eventsCache.questsProgress.getTokenCount(self.__winbackController.progressionToken)

    def __addListeners(self):
        self.__winbackController.onTokensUpdated += self.__onTokensUpdate

    def __clearListeners(self):
        self.__winbackController.onTokensUpdated -= self.__onTokensUpdate

    def _getPointsForLevel(self):
        if self.__pointsForLevel == 0:
            _logger.error('WinbackProgressionController without stages or incorrect stage configuration')
        return self.__pointsForLevel

    def _cachePoints(self, curPoints):
        settings = getWinbackSetting(self.PREV_POINTS_ACC_SETTINGS_KEY)
        if curPoints != settings.get(self.__winbackController.progressionName):
            settings[self.__winbackController.progressionName] = curPoints
            setWinbackSetting(self.PREV_POINTS_ACC_SETTINGS_KEY, settings)

    def _getCachedPoints(self):
        settings = getWinbackSetting(self.PREV_POINTS_ACC_SETTINGS_KEY)
        return settings.get(self.__winbackController.progressionName, 0)

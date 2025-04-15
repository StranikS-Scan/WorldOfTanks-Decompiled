# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/game_control/progression_controller.py
import typing
import Event
import copy
from PlayerEvents import g_playerEvents
import HBAccountSettings
from gui.server_events.bonuses import getNonQuestBonuses, SimpleBonus
from helpers import dependency
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles_common.hb_constants import AccountSettingsKeys
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from historical_battles.gui.hb_helpers import isDiscountBonus, getDiscountFromEntitlementBonus, isVehicleTokenBonus, repackTokenToVehicle
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from typing import List, Dict

class ProgressionOnTokensController(IHBProgressionOnTokensController):
    PREV_POINTS_ACC_SETTINGS_KEY = 'exampleLastPointsSeen'
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(ProgressionOnTokensController, self).__init__()
        self.onProgressPointsUpdated = Event.Event()
        self.onSettingsChanged = Event.Event()
        self._progressionToken = None
        self.__discountData = None
        return

    def init(self):
        g_playerEvents.onClientUpdated += self.__onTokensUpdate
        self._gameEventController.frontDataUpdated += self._onFrontDataUpdated

    def fini(self):
        g_playerEvents.onClientUpdated -= self.__onTokensUpdate
        self._gameEventController.frontDataUpdated -= self._onFrontDataUpdated
        self.onProgressPointsUpdated.clear()
        self.onSettingsChanged.clear()

    def saveCurPoints(self):
        self._cachePoints(self.getCurPoints())

    def getPrevPoints(self):
        return self._getCachedPoints()

    def getCurPoints(self):
        return self.getCurrentPointsByToken(self.progressionToken)

    @classmethod
    def getCurrentPointsByToken(cls, token):
        return cls.eventsCache.questsProgress.getTokenCount(token)

    def getProgessionPointsData(self):
        curPoints = self.getCurPoints()
        prevPoint = self.getPrevPoints()
        if curPoints < prevPoint:
            prevPoint = 0
        progressionLevelsData = self.getProgressionLevelsData()
        if self.__discountData is None:
            self.__discountData = self.__getDiscounts(progressionLevelsData)
        return {'curPoints': curPoints,
         'pointsForLevel': self._getPointsForLevel(),
         'prevPoints': prevPoint,
         'progressionLevels': progressionLevelsData,
         'discountsByLevel': self.__discountData}

    def getProgressionData(self):
        return self.getProgessionPointsData()

    def _cachePoints(self, curPoints):
        frontSettings = copy.deepcopy(HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS))
        progressPoints = frontSettings.get(self.PREV_POINTS_ACC_SETTINGS_KEY, 0)
        if curPoints != progressPoints:
            frontSettings[self.PREV_POINTS_ACC_SETTINGS_KEY] = curPoints
            HBAccountSettings.setSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS, frontSettings)

    def _getCachedPoints(self):
        frontSettings = HBAccountSettings.getSettings(AccountSettingsKeys.HISTORICAL_BATTLES_FRONTS)
        return frontSettings.get(self.PREV_POINTS_ACC_SETTINGS_KEY, 0)

    def _getPointsForLevel(self):
        raise NotImplementedError

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens')
        if not tokens:
            return
        if set(tokens.keys()) & self.getAllProgressionTokens():
            self.onProgressPointsUpdated()

    def __getDiscounts(self, progressionLevelsData):
        result = {}
        for level, data in enumerate(progressionLevelsData, 1):
            rewards = data['rewards']
            for bonus in rewards:
                if isDiscountBonus(bonus):
                    result[level] = getDiscountFromEntitlementBonus(bonus)

        return result

    def _onFrontDataUpdated(self, frontId, divisionId):
        pass

    def _updateProgressionTokenValue(self):
        pass

    @property
    def progressionToken(self):
        if self._progressionToken is None:
            self._progressionToken = self._gameEventController.frontController.currentFrontProgressionTokenID
        return self._progressionToken


class HBProgressionController(ProgressionOnTokensController):
    PREV_POINTS_ACC_SETTINGS_KEY = AccountSettingsKeys.SEEN_historical_battles_POINTS

    def __init__(self):
        super(HBProgressionController, self).__init__()
        self.settings = {}

    def fini(self):
        self.settings = None
        super(HBProgressionController, self).fini()
        return

    @property
    def isEnabled(self):
        return bool(self.settings)

    @property
    def isFinished(self):
        if not self.isEnabled:
            return False
        points = self._getPointsForLevel()
        lastLevelScore = points[-1] if points else 0
        return self.getCurPoints() >= lastLevelScore

    @property
    def isFirstStage(self):
        if not self.isEnabled:
            return False
        points = self._getPointsForLevel()
        secondLevelScore = points[0] if points else 0
        return self.getCurPoints() < secondLevelScore

    def setSettings(self, settings):
        self.settings = settings
        self.onSettingsChanged()

    def getCurrentStageData(self):
        frontId = self._gameEventController.frontController.getSelectedFrontID()
        return self.getCurrentStageDataForFront(frontId)

    def getCurrentStageDataForFront(self, frontId):
        if not self.isEnabled:
            return {}
        front = self._gameEventController.frontController.getFrontByID(frontId)
        curPoints = self.getCurrentPointsByToken(front.getProgressionTokenName())
        curStage = 0
        stagePoints = 0
        stageMaxPoints = 0
        prevStageMaxPoints = 0
        for stage, maxPoints in enumerate(zip(*self._getStagesForFront(frontId))[0], 1):
            curStage = stage
            stagePoints = curPoints - prevStageMaxPoints
            stageMaxPoints = maxPoints - prevStageMaxPoints
            prevStageMaxPoints = maxPoints
            if curPoints < maxPoints:
                break
        else:
            stagePoints = min(stagePoints, stageMaxPoints)

        results = {'currentStage': curStage,
         'finishedStage': curStage if self.isFinished else curStage - 1,
         'stagePoints': stagePoints,
         'stageMaxPoints': stageMaxPoints}
        return results

    def getCurrentStageAbsoluteData(self):
        if not self.isEnabled:
            return {}
        frontId = self._gameEventController.frontController.getSelectedFrontID()
        front = self._gameEventController.frontController.getFrontByID(frontId)
        curPoints = self.getCurrentPointsByToken(front.getProgressionTokenName())
        curStage = 0
        maxPoints = 0
        prevStageMaxPoints = 0
        for stage, maxPoints in enumerate(zip(*self._getStagesForFront(frontId))[0], 1):
            curStage = stage
            if curPoints < maxPoints:
                break
            prevStageMaxPoints = maxPoints

        results = {'currentStage': curStage,
         'finishedStage': curStage if self.isFinished else curStage - 1,
         'currentPoints': curPoints,
         'stageMaxPoints': maxPoints,
         'stageMinPoints': prevStageMaxPoints}
        return results

    def getProgressionLevelsData(self):
        result = []
        frontId = self._gameEventController.frontController.getSelectedFrontID()
        for stageAwards in zip(*self._getStagesForFront(frontId))[1]:
            bonuses = []
            for key, value in stageAwards:
                bonus = getNonQuestBonuses(key, value)
                for i, _ in enumerate(bonus):
                    if bonus[i].getName() == 'battleToken' and isVehicleTokenBonus(bonus[i]):
                        bonus[i] = repackTokenToVehicle(bonus[i])

                bonuses.extend(bonus)

            result.append({'rewards': bonuses})

        return result

    def getAllProgressionTokens(self):
        if self.settings:
            return set([ self.settings[k]['token'] for k in self.settings ])
        return set()

    def _getStagesForFront(self, frontId):
        return sorted([ stage for stage in self.__getAwardListForFront(frontId) if stage[0] is not None ], key=lambda stage: stage[0])

    def _getPointsForLevel(self):
        frontId = self._gameEventController.frontController.getSelectedFrontID()
        return [ point for point, _ in self.__getAwardListForFront(frontId) ]

    def _onFrontDataUpdated(self, frontId, divisionId):
        self._updateProgressionTokenValue()

    def _updateProgressionTokenValue(self):
        self._progressionToken = self._gameEventController.frontController.currentFrontProgressionTokenID

    def __getAwardListForFront(self, frontId):
        return self.settings[frontId].get('awardList', [])

    def getMaxProgressionLevelForFront(self, frontId):
        return len(self.__getAwardListForFront(frontId))

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/game_control/progression_controller.py
import typing
import Event
from PlayerEvents import g_playerEvents
import HBAccountSettings
from gui.server_events.bonuses import getNonQuestBonuses, SimpleBonus
from helpers import dependency
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles_common.hb_constants import AccountSettingsKeys
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from historical_battles.gui.hb_helpers import isDiscountBonus, getDiscountFromEntitlementBonus, isVehicleTokenBonus, repackTokenToVehicle
if typing.TYPE_CHECKING:
    from typing import List, Dict

class ProgressionOnTokensController(IHBProgressionOnTokensController):
    PREV_POINTS_ACC_SETTINGS_KEY = 'exampleLastPointsSeen'
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    progressionToken = ''

    def __init__(self):
        super(ProgressionOnTokensController, self).__init__()
        self.onProgressPointsUpdated = Event.Event()
        self.onSettingsChanged = Event.Event()
        self.__discountData = None
        return

    def init(self):
        g_playerEvents.onClientUpdated += self.__onTokensUpdate

    def fini(self):
        g_playerEvents.onClientUpdated -= self.__onTokensUpdate
        self.onProgressPointsUpdated.clear()
        self.onSettingsChanged.clear()

    def saveCurPoints(self):
        self._cachePoints(self.getCurPoints())

    def getPrevPoints(self):
        return self._getCachedPoints()

    def getCurPoints(self):
        return self.eventsCache.questsProgress.getTokenCount(self.progressionToken)

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
        HBAccountSettings.setSettings(self.PREV_POINTS_ACC_SETTINGS_KEY, curPoints)

    def _getCachedPoints(self):
        return HBAccountSettings.getSettings(self.PREV_POINTS_ACC_SETTINGS_KEY)

    def _getPointsForLevel(self):
        raise NotImplementedError

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens')
        if not tokens:
            return
        if self.progressionToken and self.progressionToken in tokens:
            self.onProgressPointsUpdated()

    def __getDiscounts(self, progressionLevelsData):
        result = {}
        for level, data in enumerate(progressionLevelsData, 1):
            rewards = data['rewards']
            for bonus in rewards:
                if isDiscountBonus(bonus):
                    result[level] = getDiscountFromEntitlementBonus(bonus)

        return result


class HBProgressionController(ProgressionOnTokensController):
    PREV_POINTS_ACC_SETTINGS_KEY = AccountSettingsKeys.SEEN_historical_battles_POINTS
    progressionToken = 'hb_coin_offence'

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
        if self.settings.get('token'):
            self.progressionToken = self.settings.get('token')
        self.onSettingsChanged()

    def getCurrentStageData(self):
        if not self.isEnabled:
            return {}
        curPoints = self.getCurPoints()
        curStage = 0
        stagePoints = 0
        stageMaxPoints = 0
        prevStageMaxPoints = 0
        for stage, maxPoints in enumerate(zip(*self._getStages())[0], 1):
            curStage = stage
            stagePoints = curPoints - prevStageMaxPoints
            stageMaxPoints = maxPoints - prevStageMaxPoints
            prevStageMaxPoints = maxPoints
            if curPoints < maxPoints:
                break
        else:
            stagePoints = min(stagePoints, stageMaxPoints)

        results = {'currentStage': curStage,
         'stagePoints': stagePoints,
         'stageMaxPoints': stageMaxPoints}
        return results

    def getProgressionLevelsData(self):
        result = []
        for stageAwards in zip(*self._getStages())[1]:
            bonuses = []
            for key, value in stageAwards:
                bonus = getNonQuestBonuses(key, value)
                for i, _ in enumerate(bonus):
                    if bonus[i].getName() == 'battleToken' and isVehicleTokenBonus(bonus[i]):
                        bonus[i] = repackTokenToVehicle(bonus[i])

                bonuses.extend(bonus)

            result.append({'rewards': bonuses})

        return result

    def _getStages(self):
        return sorted([ stage for stage in self.settings.get('awardList', []) if stage[0] is not None ], key=lambda stage: stage[0])

    def _getPointsForLevel(self):
        return [ point for point, _ in self.settings.get('awardList', []) ]

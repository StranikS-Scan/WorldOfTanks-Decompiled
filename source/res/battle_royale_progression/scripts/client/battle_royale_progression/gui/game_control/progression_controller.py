# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/game_control/progression_controller.py
import logging
import typing
import Event
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BR_PROGRESSION_POINTS_SEEN
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class ProgressionOnTokensController(IBRProgressionOnTokensController):
    PREV_POINTS_ACC_SETTINGS_KEY = 'exampleLastPointsSeen'
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    progressionToken = ''

    def __init__(self):
        super(ProgressionOnTokensController, self).__init__()
        self.onProgressPointsUpdated = Event.Event()
        self.onSettingsChanged = Event.Event()

    def init(self):
        g_playerEvents.onClientUpdated += self.__onTokensUpdate

    def fini(self):
        g_playerEvents.onClientUpdated -= self.__onTokensUpdate
        self.onProgressPointsUpdated.clear()
        self.onSettingsChanged.clear()

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens', {})
        if not tokens:
            return
        if self.progressionToken and self.progressionToken in tokens:
            self.onProgressPointsUpdated()

    def saveCurPoints(self):
        self._cachePoints(self.getCurPoints())

    def getPrevPoints(self):
        return self._getCachedPoints()

    def getCurPoints(self):
        return self.eventsCache.questsProgress.getTokenCount(self.progressionToken)

    def getProgessionPointsData(self):
        curPoings = self.getCurPoints()
        prevPoint = self.getPrevPoints()
        if curPoings < prevPoint:
            prevPoint = 0
        return {'curPoints': curPoings,
         'pointsForLevel': self._getPointsForLevel(),
         'prevPoints': prevPoint,
         'progressionLevels': self.getProgressionLevelsData()}

    def getProgressionData(self):
        return self.getProgessionPointsData()

    def _cachePoints(self, curPoints):
        AccountSettings.setSettings(self.PREV_POINTS_ACC_SETTINGS_KEY, curPoints)

    def _getCachedPoints(self):
        return AccountSettings.getSettings(self.PREV_POINTS_ACC_SETTINGS_KEY)

    def _getPointsForLevel(self):
        raise NotImplementedError


class ProgressionOnConfig(ProgressionOnTokensController):

    def __init__(self):
        super(ProgressionOnConfig, self).__init__()
        self.settings = {}

    def fini(self):
        self.settings = None
        super(ProgressionOnConfig, self).fini()
        return

    @property
    def isEnabled(self):
        return bool(self.settings)

    @property
    def isFinished(self):
        return False if not self.isEnabled else self.getCurPoints() >= self._getPointsForLevel() * len(self._getStages())

    def _getStages(self):
        return sorted([ stage for stage in self.settings.get('awardList', []) if stage[0] is not None ], key=lambda stage: stage[0])

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

    def _getPointsForLevel(self):
        stages = self._getStages()
        if len(self.settings) < 2:
            _logger.error('ProgressionOnConfig cant find stages')
            return 0
        firstStageInfo, secondStageInfo = stages[:2]
        return secondStageInfo[0] - firstStageInfo[0]

    def getProgressionLevelsData(self):
        result = []
        for stageAwards in zip(*self._getStages())[1]:
            bonuses = []
            for key, value in stageAwards.iteritems():
                bonuses.extend(getNonQuestBonuses(key, value))

            result.append({'rewards': bonuses})

        return result


class _QuestInListContainer(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.questsIds = {}

    def getQuests(self):
        return self.eventsCache.getAllQuests(self._filterFunc)

    def setQuestsIds(self, questsIds):
        self.questsIds = questsIds

    def _filterFunc(self, quest):
        return quest.getID() in self.questsIds and quest.accountReqs.isAvailable()


class BaseProgressionWithBattleQuests(ProgressionOnConfig):
    ProgressionFilterFuncKey = 'BRFuncKey'

    def __init__(self):
        super(BaseProgressionWithBattleQuests, self).__init__()
        self.questContainer = self._getQuestContainer()

    def _getQuestContainer(self):
        return _QuestInListContainer()

    def setSettings(self, settings):
        questsIds = settings.get('questIds', ())
        self.questContainer.setQuestsIds(questsIds)
        filterFunc = lambda quest: quest.getID() in questsIds
        self.eventsCache.questsProgress.addFilterFunc(filterFunc, key=self.ProgressionFilterFuncKey)
        super(BaseProgressionWithBattleQuests, self).setSettings(settings)

    def getBattleQuestData(self):
        return {'battleQuests': self.questContainer.getQuests()}

    def getProgressionData(self):
        result = self.getProgessionPointsData()
        result.update(self.getBattleQuestData())
        return result


class BRQuests(_QuestInListContainer):
    pass


class BRProgressionController(BaseProgressionWithBattleQuests):
    PREV_POINTS_ACC_SETTINGS_KEY = BR_PROGRESSION_POINTS_SEEN
    progressionToken = 'img:battle_royale:progression'
    PROGRESSION_QUEST_PREFIX = 'battle_royale:ticket:progression:'

    def _getQuestContainer(self):
        return BRQuests()

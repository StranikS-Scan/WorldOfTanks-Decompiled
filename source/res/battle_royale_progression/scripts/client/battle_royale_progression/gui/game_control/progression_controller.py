# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/game_control/progression_controller.py
import logging
import typing
import Event
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BR_PROGRESSION_POINTS_SEEN, BR_UI_SECTION
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class ProgressionOnTokensController(IBRProgressionOnTokensController):
    STORAGE_SECTION_ACC_SETTINGS_KEY = 'exampleStorage'
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

    def saveCurPoints(self):
        self._cachePoints(self.getCurPoints())

    def getPrevPoints(self):
        return self._getCachedPoints()

    def getCurPoints(self):
        return self.eventsCache.questsProgress.getTokenCount(self.progressionToken)

    def getProgessionPointsData(self):
        curPoints = self.getCurPoints()
        prevPoints = self.getPrevPoints()
        if curPoints < prevPoints:
            prevPoints = 0
        return {'curPoints': curPoints,
         'prevPoints': prevPoints}

    def _getProgressionLevels(self):
        return []

    def _cachePoints(self, curPoints):
        settings = AccountSettings.getUIFlag(self.STORAGE_SECTION_ACC_SETTINGS_KEY)
        settings[self.PREV_POINTS_ACC_SETTINGS_KEY] = curPoints
        AccountSettings.setUIFlag(self.STORAGE_SECTION_ACC_SETTINGS_KEY, settings)

    def _getCachedPoints(self):
        settings = AccountSettings.getUIFlag(self.STORAGE_SECTION_ACC_SETTINGS_KEY)
        return settings.get(self.PREV_POINTS_ACC_SETTINGS_KEY, 0)

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens', {})
        if not tokens:
            return
        if self.progressionToken and self.progressionToken in tokens:
            self.onProgressPointsUpdated()


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
        return False if not self.isEnabled else self.getCurPoints() >= self._getMaxPoints()

    def setSettings(self, settings):
        self.settings = settings
        if self.settings.get('token'):
            self.progressionToken = self.settings.get('token')
        self.onSettingsChanged()

    def getProgessionPointsData(self):
        curPoints = self.getCurPoints()
        prevPoints = self.getPrevPoints()
        if curPoints < prevPoints:
            prevPoints = 0
        curStage = 0
        prevStage = 0
        stageProgress = 0
        prevStageProgress = 0
        stagePoints = 0
        prevStagePoints = 0
        prevStageMaxPoints = 0
        maxPoints = 0
        for stage, maxPoints in enumerate(zip(*self._getStages())[0], 1):
            if curPoints < maxPoints and curStage == 0:
                curStage = stage
                stageProgress = curPoints - prevStageMaxPoints
                stagePoints = maxPoints - prevStageMaxPoints
            if prevPoints < maxPoints and prevStage == 0:
                prevStage = stage
                prevStageProgress = prevPoints - prevStageMaxPoints
                prevStagePoints = maxPoints - prevStageMaxPoints
            prevStageMaxPoints = maxPoints

        return {'curPoints': curPoints,
         'prevPoints': prevPoints,
         'stage': curStage,
         'prevStage': prevStage,
         'stageProgress': stageProgress,
         'prevStageProgress': prevStageProgress,
         'stagePoints': stagePoints,
         'prevStagePoints': prevStagePoints,
         'totalPoints': maxPoints}

    def _getProgressionLevels(self):
        progressionLevels = []
        for stageAwards in zip(*self._getStages())[1]:
            bonuses = []
            for key, value in stageAwards:
                bonuses.extend(getNonQuestBonuses(key, value))

            progressionLevels.append({'rewards': bonuses})

        return progressionLevels

    def getProgressionData(self):
        return {'progressionLevels': self._getProgressionLevels()}

    def _getStages(self):
        return sorted([ stage for stage in self.settings.get('awardList', []) if stage[0] is not None ], key=lambda stage: stage[0])

    def _getMaxPoints(self):
        stages = self._getStages()
        if len(self.settings) < 2:
            _logger.error('ProgressionOnConfig cant find stages')
            return 0
        lastStage = stages[-1]
        return lastStage[0]


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

    def setSettings(self, settings):
        questsIds = settings.get('questIds', ())
        self.questContainer.setQuestsIds(questsIds)
        filterFunc = lambda quest: quest.getID() in questsIds
        self.eventsCache.questsProgress.addFilterFunc(filterFunc, key=self.ProgressionFilterFuncKey)
        super(BaseProgressionWithBattleQuests, self).setSettings(settings)

    def getProgressionData(self):
        result = super(BaseProgressionWithBattleQuests, self).getProgressionData()
        result.update(self.__getBattleQuestData())
        return result

    def _getQuestContainer(self):
        return _QuestInListContainer()

    def __getBattleQuestData(self):
        return {'battleQuests': self.questContainer.getQuests()}


class BRQuests(_QuestInListContainer):
    pass


class BRProgressionController(BaseProgressionWithBattleQuests):
    STORAGE_SECTION_ACC_SETTINGS_KEY = BR_UI_SECTION
    PREV_POINTS_ACC_SETTINGS_KEY = BR_PROGRESSION_POINTS_SEEN
    progressionToken = 'img:battle_royale:progression'
    PROGRESSION_QUEST_PREFIX = 'battle_royale:ticket:progression:'

    def _getQuestContainer(self):
        return BRQuests()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/game_control/comp7_light_progression_controller.py
import typing
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_LIGHT_UI_SECTION, COMP7_LIGHT_PROGRESSION_POINTS_SEEN
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.server_events import IEventsCache

class ProgressionOnTokensController(IComp7LightProgressionController):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(ProgressionOnTokensController, self).__init__()
        self._progressionToken = ''
        self.onProgressPointsUpdated = Event.Event()
        self.onSettingsChanged = Event.Event()

    @property
    def progressionToken(self):
        return self._progressionToken

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
        return self._eventsCache.questsProgress.getTokenCount(self.progressionToken)

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
        settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
        settings[COMP7_LIGHT_PROGRESSION_POINTS_SEEN] = curPoints
        AccountSettings.setUIFlag(COMP7_LIGHT_UI_SECTION, settings)

    def _getCachedPoints(self):
        settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
        return settings.get(COMP7_LIGHT_PROGRESSION_POINTS_SEEN, 0)

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
            self._progressionToken = self.settings.get('token')
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
            return 0
        firstStageInfo, secondStageInfo = stages[:2]
        return secondStageInfo[0] - firstStageInfo[0]

    def getProgressionLevelsData(self):
        result = []
        stages = self._getStages()
        if not stages:
            return result
        for stageAwards in zip(*stages)[1]:
            bonuses = []
            for key, value in stageAwards:
                bonuses.extend(getNonQuestBonuses(key, value))

            result.append({'rewards': bonuses})

        return result


class _QuestInListContainer(object):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.questsIds = ()

    def getQuests(self):
        return self._eventsCache.getAllQuests(self._filterFunc)

    def getQuestsOrder(self):
        quests = self.getQuests()
        return [ questId for questId in self.questsIds if questId in quests ]

    def setQuestsIds(self, questsIds):
        self.questsIds = questsIds

    def _filterFunc(self, quest):
        return quest.getID() in self.questsIds and quest.accountReqs.isAvailable()


class BaseProgressionWithBattleQuests(ProgressionOnConfig):
    _PROGRESSION_FILTER_FUNC_KEY = 'Comp7LightFuncKey'

    def __init__(self):
        super(BaseProgressionWithBattleQuests, self).__init__()
        self.questContainer = self._getQuestContainer()

    def _getQuestContainer(self):
        return _QuestInListContainer()

    def setSettings(self, settings):
        questsIds = settings.get('questIds', ())
        self.questContainer.setQuestsIds(questsIds)
        filterFunc = lambda quest: quest.getID() in questsIds
        self._eventsCache.questsProgress.addFilterFunc(filterFunc, key=self._PROGRESSION_FILTER_FUNC_KEY)
        super(BaseProgressionWithBattleQuests, self).setSettings(settings)

    def getBattleQuestData(self):
        return {'battleQuests': self.questContainer.getQuests(),
         'questsOrder': self.questContainer.getQuestsOrder()}

    def getProgressionData(self):
        result = self.getProgessionPointsData()
        result.update(self.getBattleQuestData())
        return result


class Comp7LightQuests(_QuestInListContainer):
    pass


class Comp7LightProgressionController(BaseProgressionWithBattleQuests):

    def __init__(self):
        super(Comp7LightProgressionController, self).__init__()
        self._progressionToken = 'img:comp7_light:progression'

    def _getQuestContainer(self):
        return Comp7LightQuests()

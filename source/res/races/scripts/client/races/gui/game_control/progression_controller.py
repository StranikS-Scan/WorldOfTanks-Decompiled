# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/game_control/progression_controller.py
import logging
from collections import OrderedDict
import typing
import re
import Event
from PlayerEvents import g_playerEvents
from constants import EVENT_TYPE
from skeletons.gui.game_control import IRacesBattleController
from races.skeletons.progression_controller import IRacesProgressionController
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.server_events.event_items import Quest
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, List, Union, Optional
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
QUEST_STEP_REGEX = re.compile('races:step_([0-9]{1,2})')
WELCOME_QUEST_REGEX = re.compile('birthday_award_vehicle')
FIRST_WIN_QUEST_REGEX = re.compile('races_first_win')

class RacesProgressionController(IRacesProgressionController):
    eventsCache = dependency.descriptor(IEventsCache)
    racesBattleController = dependency.descriptor(IRacesBattleController)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(RacesProgressionController, self).__init__()
        self._quests = None
        self._lastSeenPoints = None
        self.onProgressPointsUpdated = Event.Event()
        return

    def init(self):
        super(RacesProgressionController, self).init()
        g_playerEvents.onClientUpdated += self._onTokensUpdate

    def fini(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onSettingsChanged
        g_playerEvents.onClientUpdated -= self._onTokensUpdate

    def onLobbyInited(self, event):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onSettingsChanged
        self.eventsCache.questsProgress.addFilterFunc(self._filterFunc)

    def onAccountBecomePlayer(self):
        self._quests = None
        return

    def onAvatarBecomePlayer(self):
        if self._lastSeenPoints is None:
            self._lastSeenPoints = self.getCurrentPoints()
        return

    def getQuests(self):
        tokenID = self.racesBattleController.getTokenProgressionID()
        return {quest.getID():quest for quest in self.eventsCache.getQuestsByTokenRequirement(tokenID)}

    def getDailyQuests(self):
        return self.eventsCache.getAllQuests(lambda q: self._filterFunc(q) and q.getType() == EVENT_TYPE.BATTLE_QUEST)

    def getMaxProgressionPoints(self):
        quests = self.collectSortedQuests()
        if quests:
            lastQuest = quests.values()[-1]
            return self._getNeededPointsCount(lastQuest)

    def getCurrentPoints(self):
        tokenID = self.racesBattleController.getTokenProgressionID()
        return self.eventsCache.questsProgress.getTokenCount(tokenID) if tokenID else 0

    def getProgression(self):
        return (self.getCurrentPoints(), self.getCurrentStage(), self.getMaxProgressionPoints())

    def getProgressionStage(self, quest):
        matchObject = QUEST_STEP_REGEX.search(quest.getID())
        return int(matchObject.group(1)) if matchObject else None

    def _getNeededPointsCount(self, quest):
        tokenReq = quest.accountReqs.getTokens()[0]
        return tokenReq.getNeededCount()

    def _onSettingsChanged(self, diff):
        self._quests = None
        return

    def _onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens', {})
        if not tokens:
            return
        tokenID = self.racesBattleController.getTokenProgressionID()
        if tokenID in tokens:
            self.onProgressPointsUpdated()

    def _filterFunc(self, quest):
        try:
            return self.isRacesProgressionQuest(quest.getID()) and quest.accountReqs.isAvailable()
        except Exception:
            _logger.exception('Filter meet unexpected type %s', quest)
            return False

    def getQuestsForAwardsScreen(self):
        quests = self.eventsCache.getAllQuests(lambda quest: bool(QUEST_STEP_REGEX.search(quest.getID())))
        return OrderedDict(sorted(quests.items()))

    def getWelcomeQuestForAwardsScreen(self):
        quests = self.eventsCache.getAllQuests(lambda quest: bool(WELCOME_QUEST_REGEX.search(quest.getID())))
        return OrderedDict(sorted(quests.items()))

    def isProgressionFinished(self):
        quests = self.collectSortedQuests()
        if quests:
            lastQuest = quests.values()[-1]
            return lastQuest.isCompleted()
        return False

    def getFirstWinQuestForAwardsScreen(self):
        quests = self.eventsCache.getAllQuests(lambda quest: bool(FIRST_WIN_QUEST_REGEX.search(quest.getID())))
        return OrderedDict(sorted(quests.items()))

    def getPointsForLevel(self):
        stages = self.getBonuses()
        firstStageInfo, secondStageInfo = stages[:2]
        return secondStageInfo[0] - firstStageInfo[0]

    def collectSortedQuests(self):
        quests = self.getQuests()
        return OrderedDict(sorted(quests.items(), key=lambda key_value: int(key_value[0].split('_')[-1])))

    def collectSortedDailyQuests(self):
        quests = self.getDailyQuests()
        return OrderedDict(sorted(quests.items(), key=lambda key_value: key_value[0]))

    def isRacesProgressionQuest(self, questID):
        questionPrefix = self.racesBattleController.getProgressionQuestPrefix()
        return questID.startswith(questionPrefix)

    def isRacesWelcomeQuest(self, questID):
        return questID.startswith('birthday_award_vehicle')

    def isRacesFirstWinQuest(self, questID):
        return questID.startswith('races_first_win')

    def getBonuses(self):
        result = []
        for quest in self.collectSortedQuests().values():
            pointsCondition = self._getNeededPointsCount(quest)
            bonuses = quest.getBonuses()
            result.append((pointsCondition, bonuses))

        return result

    def getCurrentStage(self):
        stageIdx = 0
        nextIdx = 1
        currentPoints = self.getCurrentPoints()
        _logger.debug('CurrentPoints: %s', currentPoints)
        for nextPoints, _ in self.getBonuses():
            _logger.debug('stage: %s, nextStage: %s, nextStagePoints: %s', stageIdx, nextIdx, nextPoints)
            if currentPoints < nextPoints:
                return stageIdx
            stageIdx = nextIdx
            nextIdx += 1
            continue

        return stageIdx

    def setQuestProgressAsViewed(self, quest):
        self.eventsCache.questsProgress.markQuestProgressAsViewed(quest.getID())

    def getQuestCompletionChanged(self, quest):
        return self.eventsCache.questsProgress.getQuestCompletionChanged(quest.getID())

    def getLastSeenPoints(self):
        return self._lastSeenPoints if self._lastSeenPoints is not None else self.getCurrentPoints()

    def updateLastSeenPoints(self, points=None):
        self._lastSeenPoints = points or self.getCurrentPoints()

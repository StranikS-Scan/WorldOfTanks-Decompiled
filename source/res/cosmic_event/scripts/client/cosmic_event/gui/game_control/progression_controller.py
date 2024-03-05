# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/game_control/progression_controller.py
import logging
from collections import OrderedDict
import typing
import re
import Event
from PlayerEvents import g_playerEvents
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.server_events.event_items import Quest
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Tuple, List, Union, Optional
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
QUEST_STEP_REGEX = re.compile('cosmic_event:step_([0-9]{1,2})')
ACHIEVEMENT_STEP_REGEX = re.compile('cosmic_event:achievements_(\\d)')

class CosmicProgressionController(ICosmicEventProgressionController):
    eventsCache = dependency.descriptor(IEventsCache)
    cosmicBattleController = dependency.descriptor(ICosmicEventBattleController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(CosmicProgressionController, self).__init__()
        self._quests = None
        self._lastSeenPoints = None
        self.onProgressPointsUpdated = Event.Event()
        return

    @property
    def quests(self):
        if self._quests is None:
            self._quests = self.collectSortedQuests()
        return self._quests

    def init(self):
        super(CosmicProgressionController, self).init()
        g_playerEvents.onClientUpdated += self._onTokensUpdate

    def fini(self):
        lobbyContext = dependency.instance(ILobbyContext)
        lobbyContext.getServerSettings().onServerSettingsChange -= self._onSettingsChanged
        g_playerEvents.onClientUpdated -= self._onTokensUpdate

    def onLobbyInited(self, event):
        lobbyContext = dependency.instance(ILobbyContext)
        lobbyContext.getServerSettings().onServerSettingsChange += self._onSettingsChanged
        self.eventsCache.questsProgress.addFilterFunc(self._filterFunc)

    def onAccountBecomePlayer(self):
        self._quests = None
        return

    def onAvatarBecomePlayer(self):
        if self._lastSeenPoints is None:
            self._lastSeenPoints = self.getCurrentPoints()
        return

    def getQuests(self):
        tokenID = self.cosmicBattleController.getTokenProgressionID()
        return {quest.getID():quest for quest in self.eventsCache.getQuestsByTokenRequirement(tokenID)}

    def getDailyQuests(self):
        return self.eventsCache.getBattleQuests(self._filterFunc)

    def getAchievementsQuests(self):
        quests = self.eventsCache.getAllQuests(lambda quest: bool(ACHIEVEMENT_STEP_REGEX.search(quest.getID())))
        return quests

    def getMaxProgressionPoints(self):
        if self.quests:
            lastQuest = self.quests.values()[-1]
            return self._getNeededPointsCount(lastQuest)

    def getCurrentPoints(self):
        tokenID = self.cosmicBattleController.getTokenProgressionID()
        return self.eventsCache.questsProgress.getTokenCount(tokenID) if tokenID else 0

    def getProgression(self):
        return (self.getCurrentPoints(), self.getCurrentStage(), self.getMaxProgressionPoints())

    def getProgressionStage(self, quest):
        matchObject = QUEST_STEP_REGEX.search(quest.getID())
        return int(matchObject.group(1)) if matchObject else None

    def getAchievementNumber(self, quest):
        matchObject = ACHIEVEMENT_STEP_REGEX.search(quest.getID())
        return int(matchObject.group(1)) if matchObject else None

    def getQuestsForAwardsScreen(self):

        def filterFunc(quest):
            questType = bool(ACHIEVEMENT_STEP_REGEX.search(quest[0]))
            index = int(quest[0].split('_')[-1])
            return (questType, index)

        quests = self.eventsCache.getAllQuests(lambda quest: bool(ACHIEVEMENT_STEP_REGEX.search(quest.getID()) or QUEST_STEP_REGEX.search(quest.getID())))
        return OrderedDict(sorted(quests.items(), key=filterFunc))

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
        tokenID = self.cosmicBattleController.getTokenProgressionID()
        if tokenID in tokens:
            self.onProgressPointsUpdated()

    def _filterFunc(self, quest):
        try:
            return self.isCosmicProgressionQuest(quest.getID()) and quest.accountReqs.isAvailable()
        except Exception:
            _logger.exception('Filter meet unexpected type %s', quest)
            return False

    def collectSortedQuests(self):
        quests = self.getQuests()
        return OrderedDict(sorted(quests.items(), key=lambda key_value: int(key_value[0].split('_')[-1])))

    def collectSortedDailyQuests(self):
        quests = self.getDailyQuests()
        return OrderedDict(sorted(quests.items(), key=lambda key_value: key_value[0]))

    def isCosmicProgressionQuest(self, questID):
        questionPrefix = self.cosmicBattleController.getProgressionQuestPrefix()
        return questID.startswith(questionPrefix)

    def getBonuses(self):
        result = []
        for quest in self.quests.values():
            if not quest.isHidden():
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

    def isProgressionFinished(self):
        finishedToken = self.cosmicBattleController.getProgressionFinishedToken()
        return self.itemsCache.items.tokens.isTokenAvailable(finishedToken)

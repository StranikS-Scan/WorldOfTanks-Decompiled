# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/game_control/comp7_weekly_quests_controller.py
import logging
import typing
from functools import partial
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from comp7_common_const import Comp7QuestType, offerWeeklyQuestsRewardGiftTokenBySeasonNumber, offerWeeklyQuestsRewardTokenBySeasonNumber
from comp7.gui.impl.gen.view_models.views.lobby.missions.comp7_widget_quest_model import State
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import Comp7ParsedQuestID
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Callable, List, Optional, Tuple, Union
    from comp7.gui.game_control.comp7_controller import Comp7Controller
    from gui.server_events import EventsCache
    from gui.server_events.event_items import Quest, TokenQuest
    from gui.shared.items_cache import ItemsCache
    from gui.offers import OffersDataProvider
_logger = logging.getLogger(__name__)

class Comp7WeeklyQuestsController(IComp7WeeklyQuestsController, IGlobalListener):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self):
        super(Comp7WeeklyQuestsController, self).__init__()
        self.__quests = None
        self.__timer = CallbackDelayer()
        self.__eventsManager = em = EventManager()
        self.onWeeklyQuestsUpdated = Event(em)
        return

    def fini(self):
        self.__eventsManager.clear()
        self.__quests = None
        self.__timer.destroy()
        self.__timer = None
        super(Comp7WeeklyQuestsController, self).fini()
        return

    def getQuests(self):
        if not self.__quests:
            self.__quests = self.__getUpdatedQuests()
            self.__setNewQuestsCallback()
        return self.__quests

    def isInHideState(self):
        return self.getQuests().newQuestState == State.HIDE

    def onConnected(self):
        g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated

    def onDisconnected(self):
        self.__removeListeners()
        self.stopGlobalListening()
        self.__quests = None
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        return

    def onPrbEntitySwitched(self):
        if self.__comp7Controller.isComp7PrbActive():
            self.__addListeners()
        else:
            self.__quests = None
            self.__timer.clearCallbacks()
            self.__removeListeners()
        return

    def __onPrbDispatcherCreated(self):
        self.startGlobalListening()
        if self.__comp7Controller.isComp7PrbActive():
            self.__addListeners()

    def __addListeners(self):
        self.__eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        self.__comp7Controller.onStatusUpdated += self.__onComp7StatusUpdated
        self.__offersProvider.onOffersUpdated += self.__onOffersUpdated

    def __removeListeners(self):
        self.__eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        self.__comp7Controller.onStatusUpdated -= self.__onComp7StatusUpdated
        self.__offersProvider.onOffersUpdated -= self.__onOffersUpdated

    def __onEventsCacheSyncCompleted(self):
        self.__updateQuests()

    def __onComp7StatusUpdated(self, _):
        self.__updateQuests()

    def __onOffersUpdated(self):
        if self.__isFinalRewardChosen():
            quests = self.__quests
            quests.newQuestState = State.HIDE
            self.onWeeklyQuestsUpdated(quests)

    def __updateQuests(self):
        self.__quests = self.__getUpdatedQuests()
        self.__setNewQuestsCallback()
        self.onWeeklyQuestsUpdated(self.__quests)

    @classmethod
    def __getUpdatedQuests(cls):
        battleQuests, tokenQuests = [], []
        cls.__eventsCache.getAllQuests(partial(_filterAndAppend, battleQuests.append, tokenQuests.append))
        battleQuests.sort()
        tokenQuests.sort()
        if not battleQuests or not tokenQuests:
            _logger.error('Events cache failed to provide quests to the Comp7WeeklyQuestsController.')
            return _Comp7WeeklyQuestsInErrorState()
        else:
            completedCnt, oldQuest, newQuest, newQuestState = (0, None, None, None)
            for _, quest in battleQuests:
                if quest.isCompleted():
                    completedCnt += 1
                    oldQuest = quest
                if not newQuest:
                    newQuest = quest
                    newQuestState = State.ACTIVE if quest.isStarted() else State.WAITING
                if not quest.isStarted():
                    timeOfNewQuests = quest.getStartTime()
                    break
            else:
                timeOfNewQuests = None

            numBattleQuests = len(battleQuests)
            if numBattleQuests == completedCnt:
                newQuestState = State.HIDE if cls.__isFinalRewardChosen() else State.REWARD
            return _Comp7WeeklyQuests(battleQuests, tokenQuests, oldQuest, newQuest, newQuestState, numBattleQuests, completedCnt, timeOfNewQuests)

    def __setNewQuestsCallback(self):
        self.__timer.clearCallbacks()
        timeToNewQuests = self.__quests.getTimeToNewQuests()
        if timeToNewQuests != -1:
            self.__timer.delayCallback(timeToNewQuests, self.__updateQuests)

    @classmethod
    def __isFinalRewardChosen(cls):
        season = cls.__comp7Controller.getActualSeasonNumber()
        if season is None:
            return True
        else:
            tokens = cls.__itemsCache.items.tokens.getTokens()
            rewardToken = offerWeeklyQuestsRewardTokenBySeasonNumber(season)
            giftToken = offerWeeklyQuestsRewardGiftTokenBySeasonNumber(season)
            return rewardToken in tokens and giftToken not in tokens


class _Comp7WeeklyQuests(object):
    __slots__ = ('sortedBattleQuests', 'sortedTokenQuests', 'oldQuest', 'newQuest', 'newQuestState', 'numBattleQuests', 'numCompletedBattleQuests', 'numBattleQuestsToCompleteByTokenQuestIdx', '__timeOfNewQuests')

    def __init__(self, battleQuests, tokenQuests, oldQuest, newQuest, newQuestState, numBattleQuests, numCompletedBattleQuests, timeOfNewQuests):
        self.sortedBattleQuests = battleQuests
        self.sortedTokenQuests = tokenQuests
        self.oldQuest = oldQuest
        self.newQuest = newQuest
        self.newQuestState = newQuestState
        self.numBattleQuests = numBattleQuests
        self.numCompletedBattleQuests = numCompletedBattleQuests
        self.numBattleQuestsToCompleteByTokenQuestIdx = tuple((quest.accountReqs.getConditions().find('token').getNeededCount() for _, quest in tokenQuests))
        self.__timeOfNewQuests = timeOfNewQuests

    def getTimeToNewQuests(self):
        timeOfNewQuests = self.__timeOfNewQuests
        if timeOfNewQuests is None:
            return -1
        else:
            timeToNewQuests = time_utils.getTimeDeltaFromNowInLocal(timeOfNewQuests)
            return 1 if timeToNewQuests < 0 else timeToNewQuests

    def __repr__(self):
        return '{}\n{}'.format(self.__class__.__name__, '\n'.join(('{}={}'.format(n, getattr(self, n, 'priv')) for n in self.__slots__)))


class _Comp7WeeklyQuestsInErrorState(_Comp7WeeklyQuests):

    def __init__(self):
        super(_Comp7WeeklyQuestsInErrorState, self).__init__([], [], None, None, State.HIDE, 0, 0, None)
        return


def _filterAndAppend(appendToBattle, appendToToken, quest, battleQuestType=Comp7QuestType.WEEKLY, tokenQuestType=Comp7QuestType.TOKENS):
    parsedID = Comp7ParsedQuestID(quest.getID())
    if not parsedID:
        return False
    if parsedID.questType == battleQuestType:
        appendToBattle((parsedID.extraInfo, quest))
        return True
    if parsedID.questType == tokenQuestType:
        appendToToken((int(parsedID.extraInfo), quest))
        return True
    return False

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/game_event/game_event_progress.py
import logging
import typing
from functools import partial
from weakref import proxy
from Event import Event, EventManager
from helpers import dependency, server_settings
from skeletons.gui.server_events import IEventsCache
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import getTimestampFromNow
from gui.shared.money import Currency
from gui.server_events.conditions import getTokenNeededCountInCondition, getTokenReceivedCountInCondition
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from typing import Optional, List, Dict
    from historical_battles.gui.server_events.game_event.frontman_item import FrontmanItem
_logger = logging.getLogger(__name__)
_BONUS_ORDER = (Currency.CREDITS,
 Currency.GOLD,
 Currency.CRYSTAL,
 'creditsFactor',
 'freeXP',
 'freeXPFactor',
 'tankmenXP',
 'tankmenXPFactor',
 'xp',
 'xpFactor',
 'dailyXPFactor',
 'items')
_DEFAULT_BONUS_ORDER = len(_BONUS_ORDER)

class GameEventCollection(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__em = EventManager()
        self.onItemsUpdated = Event(self.__em)

    def init(self):
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()

    def fini(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.__em.clear()

    def _onSyncCompleted(self):
        pass


class GameEventProgress(CallbackDelayer):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)
    settingsCore = dependency.descriptor(ISettingsCore)
    _CALLBACK_OFFSET = 2.0

    def __init__(self, questGroupPrefix, questGroupProgressPrefix, questFinalRewardGroupPrefix, questBonusGroupSuffix, maxLevelBoughtTokenName):
        super(GameEventProgress, self).__init__()
        self._items = None
        self._questGroupPrefix = questGroupPrefix
        self._questGroupProgressPrefix = questGroupProgressPrefix
        self._questBonusGroupSuffix = questBonusGroupSuffix
        self._maxLevelBoughtTokenName = maxLevelBoughtTokenName
        self._questFinalRewardGroupPrefix = questFinalRewardGroupPrefix
        self.__em = EventManager()
        self.onItemsUpdated = Event(self.__em)
        return

    def init(self):
        self._items = [self._createProgressItemEmpty()]
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()

    def fini(self):
        self._items = None
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.__em.clear()
        self.destroy()
        return

    def getItems(self):
        return self._items

    def getQuestGroupPrefix(self):
        return self._questGroupPrefix

    def getQuestBonusGroupSuffix(self):
        return self._questBonusGroupSuffix

    def isCompleted(self):
        return self.isMaxLevelBought() or len(self._items) > 1 and all((item.isCompleted() for item in self._items))

    def isMaxLevelBought(self):
        return bool(self.eventsCache.questsProgress.getTokenCount(self._maxLevelBoughtTokenName))

    def getCurrentProgressItem(self):
        return next((item for item in reversed(self._items) if item.isCompleted() or self.isMaxLevelBought()), None)

    def getProgressLeftToNextLevel(self):
        item = self.getCurrentProgressItem()
        if item.getLevel() == self.getMaxLevel():
            return 0
        nextLevel = self._items[item.getLevel() + 1]
        return nextLevel.getMaxProgress() - nextLevel.getCurrentProgress() if nextLevel.isAvailable() else 0

    def getNextProgressItem(self):
        item = self.getCurrentProgressItem()
        return None if item.getLevel() == self.getMaxLevel() else self._items[item.getLevel() + 1]

    def getCurrentProgressLevel(self):
        currentLevel = self.getCurrentProgressItem()
        return currentLevel.getLevel() if currentLevel else 0

    def getCurrentProgress(self):
        res = 0
        for item in self._items:
            if item.isCompleted():
                res += item.getMaxProgress()
            if item.isAvailable():
                res += item.getCurrentProgress()
                res += item.getBonusCount() * item.getMaxProgress()
            break

        return res

    def getTotalProgressForLevel(self, level):
        res = 0
        for itemID in xrange(level + 1):
            item = self._items[itemID]
            if item.isCompleted():
                res += item.getMaxProgress()
            if item.isAvailable():
                res += (item.getBonusCount() + 1) * item.getMaxProgress()
            break

        return res

    def getProgressForLevel(self, level, bonusCount):
        res = 0
        for itemID in xrange(level + 1):
            item = self._items[itemID]
            if item.isCompleted():
                res += item.getMaxProgress()
            if item.isAvailable():
                res += bonusCount * item.getMaxProgress()
            break

        return res

    def getTotalProgress(self):
        item = self.getNextProgressItem()
        if item is None:
            item = self.getCurrentProgressItem()
        return self.getTotalProgressForLevel(item.getLevel())

    def isMaxLevelBuyEnabled(self):
        return self.gameEventController.isEnabled()

    def getMaxProgressItem(self):
        return self._items[-1] if self._items else None

    def getCurrentMaxProgressLevel(self):
        return next((item.getLevel() for item in reversed(self._items) if item.isUnlocked()), 0)

    def getMaxLevel(self):
        return len(self._items) - 1

    def getStartTime(self):
        return self._items[1].getStartTime() if len(self._items) > 1 else 0

    def isStarted(self):
        return getTimestampFromNow(self.getStartTime()) <= 0

    def getLastQuestStartTime(self):
        return self._items[-1].getStartTime() if self._items else 0

    def getFinishTime(self):
        return self._items[-1].getFinishTime() if self._items else 0

    def getFinishTimeLeft(self):
        return self._items[-1].getFinishTimeLeft() if self._items else 0

    def getFirstLockItem(self):
        return next((item for item in self._items if not item.isUnlocked()), None)

    def getProgressTokenName(self):
        raise NotImplementedError

    def _onSyncCompleted(self):
        if self._items is None:
            return
        else:
            quests = sorted([ q for q in self.eventsCache.getHiddenQuests().itervalues() if self._isMyProgressQuest(q) ], key=GameEventProgressItem.getLevelFromQuest)
            if len(self._items) > len(quests) + 1:
                self._items = self._items[:len(quests) + 1]
            self._items[0].setQuest(None)
            for index, quest in enumerate(quests, start=1):
                if index >= len(self._items):
                    self._items.append(self._createProgressItem(quest))
                self._items[index].setQuest(quest)

            self.onItemsUpdated()
            self.stopCallback(self._onSyncCompletedCallback)
            lockItem = self.getFirstLockItem()
            if lockItem:
                self.delayCallback(lockItem.getStartTimeLeft() + self._CALLBACK_OFFSET, self._onSyncCompletedCallback)
            return

    def _onSyncCompletedCallback(self):
        self._onSyncCompleted()

    def _isMyProgressQuest(self, quest):
        groupID = quest.getGroupID()
        return groupID and groupID.startswith(self._questGroupPrefix) and groupID.endswith(self._questGroupProgressPrefix)

    def _createProgressItem(self, quest):
        return GameEventProgressItem(self, quest)

    def _createProgressItemEmpty(self):
        return GameEventProgressItemEmpty(self)


class GameEventProgressQuest(object):

    def __init__(self, quest, tokenProgresName):
        super(GameEventProgressQuest, self).__init__()
        self._quest = quest
        self.tokenProgresName = tokenProgresName

    def getQuest(self):
        return self._quest

    def setQuest(self, quest):
        self._quest = quest

    def isAvailable(self):
        return self._quest.isAvailable().isValid

    def isCompleted(self):
        return self._quest.isCompleted()

    def isUnlocked(self):
        return self.getStartTimeLeft() <= 0

    def getCurrentProgress(self):
        maxProgress = self.getMaxProgress()
        if self.isCompleted():
            return maxProgress
        return min(getTokenReceivedCountInCondition(self._quest, self.tokenProgresName, default=0), maxProgress) if self.isAvailable() else 0

    def getMaxProgress(self):
        return getTokenNeededCountInCondition(self._quest, self.tokenProgresName, default=0)

    def getStartTime(self):
        return self._quest.getStartTime()

    def getStartTimeLeft(self):
        return self._quest.getStartTimeLeft()

    def getFinishTimeLeft(self):
        return self._quest.getFinishTimeLeft()

    def getFinishTime(self):
        return self._quest.getFinishTime()


class GameEventProgressItem(GameEventProgressQuest):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, progressController, quest):
        super(GameEventProgressItem, self).__init__(quest, progressController.getProgressTokenName())
        self._progressController = proxy(progressController)

    def getLevel(self):
        return self.getLevelFromQuest(self._quest)

    @staticmethod
    def getLevelFromQuest(quest):
        return int(quest.getID().split('_')[-1])

    def isAvailable(self):
        return False if not self._quest.isAvailable().isValid else self._progressController.getCurrentProgressLevel() == self.getLevel() - 1

    def getBonuses(self):
        return sorted(self._quest.getBonuses(), key=self._getBonusPriority)

    def getActiveBonuses(self):
        bonuses = []
        bonusQuest = self.getCorrespondBonusQuest()
        if bonusQuest:
            bonuses.extend(bonusQuest.getBonuses())
        return sorted(bonuses, key=self._getBonusPriority)

    def isBonusQuestCompleted(self):
        bonusQuest = self.getCorrespondBonusQuest()
        return False if bonusQuest is None else bonusQuest.isCompleted()

    def getBonusCount(self):
        return self._quest.getBonusCount()

    def _getBonusPriority(self, bonus):
        return _BONUS_ORDER.index(bonus.getName()) if bonus.getName() in _BONUS_ORDER else _DEFAULT_BONUS_ORDER

    def getCorrespondBonusQuest(self):
        return next((q for q in self.eventsCache.getHiddenQuests().itervalues() if self._isMyBonusQuest(q)), None)

    def _isMyBonusQuest(self, quest):
        groupID = quest.getGroupID()
        if not groupID:
            return False
        return False if not (groupID.startswith(self._progressController.getQuestGroupPrefix()) and groupID.endswith(self._progressController.getQuestBonusGroupSuffix())) else self._getLevelFromBonusQuest(quest) == self.getLevel()

    def _getLevelFromBonusQuest(self, quest):
        return int(quest.getID().split('_')[-1])


class GameEventProgressItemEmpty(GameEventProgressQuest):

    def __init__(self, progressController):
        super(GameEventProgressItemEmpty, self).__init__(None, None)
        return

    def getLevel(self):
        pass

    def isAvailable(self):
        return True

    def isCompleted(self):
        return True

    def getMaxProgress(self):
        pass

    def isUnlocked(self):
        return True

    def getStartTimeLeft(self):
        pass

    def getFinishTimeLeft(self):
        pass

    def getFinishTime(self):
        pass

    def getStartTime(self):
        pass

    def getBonuses(self):
        return []

    def getBonusCount(self):
        pass


class ProgressItemsController(object):
    eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(ProgressItemsController, self).__init__()
        self._container = {}
        self._em = EventManager()
        self.onItemsUpdated = Event(self._em)

    def start(self):
        self._container = {}
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._onSyncCompleted()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def stop(self):
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__clearContainer()
        self._em.clear()

    @server_settings.serverSettingsChangeListener('historical_battles')
    def __onServerSettingsChanged(self, _):
        self._onSyncCompleted()

    def getItems(self):
        return self._container

    def getInstanceClass(self):
        raise NotImplementedError

    def getActiveItemIDs(self):
        raise NotImplementedError

    def _onSyncCompleted(self):
        if self.__gameEventController.isEnabled():
            activeIDs = self.getActiveItemIDs()
        else:
            self.__clearContainer()
            activeIDs = []
        unusedIDs = [ itemID for itemID in self._container.iterkeys() if itemID not in activeIDs ]
        for itemID in unusedIDs:
            self._removeProgressItem(itemID)

        for itemID in activeIDs:
            self._addProgressItem(itemID)

    def _addProgressItem(self, itemID):
        if itemID in self._container:
            _logger.debug('Progress item with id %s already exist', itemID)
            return
        item = self.getInstanceClass()(itemID)
        self._container[itemID] = item
        item.init()
        item.onItemsUpdated += partial(self._onItemsUpdated, itemID)

    def _removeProgressItem(self, itemID):
        if itemID not in self._container:
            _logger.error("Progress item with id %s doesn't exist", itemID)
            return
        item = self._container[itemID]
        item.fini()
        self._container.pop(itemID)

    def _onItemsUpdated(self, itemID):
        self.onItemsUpdated(itemID)

    def __clearContainer(self):
        keysCopy = self._container.keys()
        for itemID in keysCopy:
            self._removeProgressItem(itemID)

        self._container = {}

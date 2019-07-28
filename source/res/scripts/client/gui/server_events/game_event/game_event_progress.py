# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/game_event_progress.py
import logging
from weakref import proxy
from Event import Event, EventManager
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers.CallbackDelayer import CallbackDelayer
from gui.shared.money import Currency
from gui.server_events.conditions import getTokenNeededCountInCondition, getTokenReceivedCountInCondition
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

class GameEventProgress(CallbackDelayer):
    eventsCache = dependency.descriptor(IEventsCache)
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

    @property
    def items(self):
        return self._items

    def getQuestGroupPrefix(self):
        return self._questGroupPrefix

    def getQuestBonusGroupSuffix(self):
        return self._questBonusGroupSuffix

    def isCompleted(self):
        return self.isMaxLevelBought() or len(self.items) > 1 and all((item.isCompleted() for item in self.items))

    def isMaxLevelBought(self):
        return bool(self.eventsCache.questsProgress.getTokenCount(self._maxLevelBoughtTokenName))

    def getCurrentProgressItem(self):
        return next((item for item in reversed(self.items) if item.isCompleted() or self.isMaxLevelBought()), None)

    def getProgressLeftToNextLevel(self):
        item = self.getCurrentProgressItem()
        if item.getLevel() == self.getMaxLevel():
            return 0
        nextLevel = self.items[item.getLevel() + 1]
        return nextLevel.getMaxProgress() - nextLevel.getCurrentProgress() if nextLevel.isAvailable() else 0

    def getNextProgressItem(self):
        item = self.getCurrentProgressItem()
        return None if item.getLevel() == self.getMaxLevel() else self.items[item.getLevel() + 1]

    def getCurrentProgressLevel(self):
        currentLevel = self.getCurrentProgressItem()
        return currentLevel.getLevel() if currentLevel else 0

    def getCurrentCostForLevel(self, *args, **kwargs):
        pass

    def getCurrentProgress(self):
        res = 0
        for item in self.items:
            if item.isCompleted():
                res += item.getMaxProgress()
            if item.isAvailable():
                res += item.getCurrentProgress()
            break

        return res

    def getTotalProgressForLevel(self, level):
        return sum((self.items[itemID].getMaxProgress() for itemID in xrange(level + 1)))

    def getTotalProgress(self):
        return self.getTotalProgressForLevel(self.getMaxLevel())

    def isMaxLevelBuyEnabled(self):
        return self.eventsCache.isEventEnabled()

    def getMaxProgressItem(self):
        return self.items[-1] if self.items else None

    def getCurrentMaxProgressLevel(self):
        return next((item.getLevel() for item in reversed(self.items) if item.isUnlocked()), 0)

    def getMaxLevel(self):
        return len(self.items) - 1

    def getStartTime(self):
        return self.items[1].getStartTime() if len(self.items) > 1 else 0

    def getLastQuestStartTime(self):
        return self.items[-1].getStartTime() if self.items else 0

    def getFinishTime(self):
        return self.items[-1].getFinishTime() if self.items else 0

    def getFinishTimeLeft(self):
        return self.items[-1].getFinishTimeLeft() if self.items else 0

    def getFirstLockItem(self):
        return next((item for item in self.items if not item.isUnlocked()), None)

    def getProgressTokenName(self):
        raise NotImplementedError

    def _onSyncCompleted(self):
        if self.items is None:
            return
        else:
            quests = sorted([ q for q in self.eventsCache.getHiddenQuests().itervalues() if self._isMyProgressQuest(q) ], key=GameEventProgressItem.getLevelFromQuest)
            if len(self.items) > len(quests) + 1:
                self._items = self.items[:len(quests) + 1]
            self.items[0].setQuest(None)
            for index, quest in enumerate(quests, start=1):
                if index >= len(self.items):
                    self.items.append(self._createProgressItem(quest))
                self.items[index].setQuest(quest)

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

    def _getGameEventServerSetting(self, key, default=None):
        value = self.settingsCore.serverSettings.getGameEventStorage().get(key)
        return default if value is None else value

    def _createProgressItem(self, quest):
        return GameEventProgressItem(self, quest)

    def _createProgressItemEmpty(self):
        return GameEventProgressItemEmpty(self)


class GameEventProgressItem(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, progressController, quest):
        super(GameEventProgressItem, self).__init__()
        self._progressController = proxy(progressController)
        self._quest = quest

    def setQuest(self, quest):
        self._quest = quest

    def getLevel(self):
        return self.getLevelFromQuest(self._quest)

    @staticmethod
    def getLevelFromQuest(quest):
        return int(quest.getID().split('_')[-1])

    def isAvailable(self):
        return False if not self._quest.isAvailable().isValid else self._progressController.getCurrentProgressLevel() == self.getLevel() - 1

    def isCompleted(self):
        isCompleted = self._quest.isCompleted()
        return isCompleted

    def isUnlocked(self):
        return self.getStartTimeLeft() <= 0

    def getCurrentProgress(self):
        maxProgress = self.getMaxProgress()
        if self.isCompleted():
            return maxProgress
        return min(getTokenReceivedCountInCondition(self._quest, self._progressController.getProgressTokenName(), default=0), maxProgress) if self.isAvailable() else 0

    def getMaxProgress(self):
        return getTokenNeededCountInCondition(self._quest, self._progressController.getProgressTokenName(), default=0)

    def getStartTime(self):
        return self._quest.getStartTime()

    def getStartTimeLeft(self):
        return self._quest.getStartTimeLeft()

    def getFinishTimeLeft(self):
        return self._quest.getFinishTimeLeft()

    def getFinishTime(self):
        return self._quest.getFinishTime()

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


class GameEventProgressItemEmpty(GameEventProgressItem):

    def __init__(self, progressController):
        super(GameEventProgressItemEmpty, self).__init__(progressController, None)
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

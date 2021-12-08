# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/auto_boxes_subformatters.py
import typing
import BigWorld
from adisp import async, process
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.loot_box import NewYearLootBoxes, EventLootBoxes
from gui.shared.notifications import NotificationGroup
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import WaitItemsSyncFormatter, ServiceChannelFormatter, BattlePassQuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForBoxes
from skeletons.gui.shared import IItemsCache

class IAutoLootBoxSubFormatter(object):

    @classmethod
    def getBoxesOfThisGroup(cls, boxIDs):
        pass

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        pass

    @classmethod
    def _isBoxOfRequiredTypes(cls, boxID, boxTypes):
        pass


class AutoLootBoxSubFormatter(IAutoLootBoxSubFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getBoxesOfThisGroup(cls, boxIDs):
        return set((boxID for boxID in boxIDs if cls._isBoxOfThisGroup(boxID)))

    @classmethod
    def _isBoxOfRequiredTypes(cls, boxID, boxTypes):
        box = cls.__itemsCache.items.tokens.getLootBoxByID(boxID)
        return box is not None and box.getType() in boxTypes


class AsyncAutoLootBoxSubFormatter(WaitItemsSyncFormatter, AutoLootBoxSubFormatter):

    def __init__(self):
        super(AsyncAutoLootBoxSubFormatter, self).__init__()
        self._achievesFormatter = BattlePassQuestAchievesFormatter()


class SyncAutoLootBoxSubFormatter(ServiceChannelFormatter, AutoLootBoxSubFormatter):

    def __init__(self):
        super(SyncAutoLootBoxSubFormatter, self).__init__()
        self._achievesFormatter = BattlePassQuestAchievesFormatter()


class EventBoxesFormatter(AsyncAutoLootBoxSubFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __MESSAGE_TEMPLATE = 'EventLootBoxesAutoOpenMessage'
    __R_LOOT_BOXES = R.strings.messenger.serviceChannelMessages.lootBoxesAutoOpen.event

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data.keys())
            rewards = getRewardsForBoxes(message, openedBoxesIDs)
            fmtBoxes = self.__getFormattedBoxes(message, openedBoxesIDs)
            fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processTokens=False)
            ctx = {'boxes': fmtBoxes,
             'rewards': backport.text(self.__R_LOOT_BOXES.rewards(), rewards=fmt)}
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx=ctx)
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            callback([MessageData(formatted, settings)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, EventLootBoxes.ALL())

    def __getFormattedBoxes(self, message, openedBoxesIDs):
        boxes = []
        for boxID in openedBoxesIDs:
            box = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
            boxes.append(backport.text(self.__R_LOOT_BOXES.counter(), boxName=box.getUserName(), count=message.data[boxID]['count']))

        return ', '.join(boxes)


class NYPostEventBoxesFormatter(AsyncAutoLootBoxSubFormatter):
    __MESSAGE_TEMPLATE = 'LootBoxesAutoOpenMessage'
    __REWARDS_TEMPLATE = 'LootBoxRewardsSysMessage'
    __REQUIERED_BOX_TYPES = {NewYearLootBoxes.COMMON, NewYearLootBoxes.PREMIUM, NewYearLootBoxes.SPECIAL}

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data.keys())
            callback([self.__getMainMessage(message, openedBoxesIDs), self.__getRewardsMessage(message, openedBoxesIDs)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, cls.__REQUIERED_BOX_TYPES)

    def __getMainMessage(self, message, openedBoxesIDs):
        oldStyleCount = {bID:message.data[bID]['count'] for bID in openedBoxesIDs}
        rewards = getRewardsForBoxes(message, openedBoxesIDs)
        formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={}, data={'savedData': {'rewards': rewards,
                       'boxIDs': oldStyleCount}})
        settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
        settings.groupID = NotificationGroup.OFFER
        settings.showAt = BigWorld.time()
        return MessageData(formatted, settings)

    def __getRewardsMessage(self, message, openedBoxesIDs):
        allRewards = getRewardsForBoxes(message, openedBoxesIDs)
        fmt = self._achievesFormatter.formatQuestAchieves(allRewards, asBattleFormatter=False, processTokens=False)
        formattedRewards = g_settings.msgTemplates.format(self.__REWARDS_TEMPLATE, ctx={'text': fmt})
        settingsRewards = self._getGuiSettings(message, self.__REWARDS_TEMPLATE)
        settingsRewards.showAt = BigWorld.time()
        return MessageData(formattedRewards, settingsRewards)


class NYGiftSystemSurpriseFormatter(AsyncAutoLootBoxSubFormatter):
    __MESSAGE_TEMPLATE = 'NYSpecialLootBoxesAutoOpenMessage'
    __REQUIERED_BOX_TYPES = {NewYearLootBoxes.SPECIAL_AUTO}

    @async
    @process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data.keys())
            rewards = getRewardsForBoxes(message, openedBoxesIDs)
            fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processTokens=False)
            formattedData = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'achieves': fmt})
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            settings.showAt = BigWorld.time()
            callback([MessageData(formattedData, settings)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, cls.__REQUIERED_BOX_TYPES)

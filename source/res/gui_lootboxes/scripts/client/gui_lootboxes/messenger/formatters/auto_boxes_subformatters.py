# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/messenger/formatters/auto_boxes_subformatters.py
import typing
from adisp import adisp_async, adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.loot_box import EventLootBoxes, WTLootBoxes
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import LootBoxAchievesFormatter, ServiceChannelFormatter, WaitItemsSyncFormatter
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
        self._achievesFormatter = LootBoxAchievesFormatter()


class SyncAutoLootBoxSubFormatter(ServiceChannelFormatter, AutoLootBoxSubFormatter):

    def __init__(self):
        super(SyncAutoLootBoxSubFormatter, self).__init__()
        self._achievesFormatter = LootBoxAchievesFormatter()


class EventBoxesFormatter(AsyncAutoLootBoxSubFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data.keys())
            rewards = getRewardsForBoxes(message, openedBoxesIDs)
            fmtBoxes = self.__getFormattedBoxes(message, openedBoxesIDs)
            fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processTokens=False)
            ctx = {'boxes': fmtBoxes,
             'rewards': backport.text(self._getTextResPath().rewards(), rewards=fmt)}
            formatted = g_settings.msgTemplates.format(self._getMessageTemplate(), ctx=ctx)
            settings = self._getGuiSettings(message, self._getMessageTemplate())
            callback([MessageData(formatted, settings)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, WTLootBoxes.ALL())

    @staticmethod
    def _getMessageTemplate():
        pass

    @staticmethod
    def _getTextResPath():
        return R.strings.messenger.serviceChannelMessages.lootBoxesAutoOpen.event

    def __getFormattedBoxes(self, message, openedBoxesIDs):
        boxes = []
        for boxID in openedBoxesIDs:
            box = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
            boxes.append(backport.text(self._getTextResPath().counter(), boxName=box.getUserName(), count=message.data[boxID]['count']))

        return ', '.join(boxes)


class EventLootBoxesFormatter(EventBoxesFormatter):

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, EventLootBoxes.ALL())

    @staticmethod
    def _getMessageTemplate():
        pass

    @staticmethod
    def _getTextResPath():
        return R.strings.lootboxes.notification.lootBoxesAutoOpen

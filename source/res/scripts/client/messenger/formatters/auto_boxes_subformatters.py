# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/auto_boxes_subformatters.py
import typing
import BigWorld
from adisp import adisp_async, adisp_process
from dossiers2.ui.achievements import BADGES_BLOCK
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.gui_items.dossier import getAchievementFactory
from gui.shared.gui_items.loot_box import ALL_LUNAR_NY_LOOT_BOX_TYPES, EventLootBoxes, WTLootBoxes, NewYearLootBoxes
from gui.shared.notifications import NotificationGroup
from helpers import dependency
from items.components.ny_constants import NySackLootBox
from messenger import g_settings
from messenger.formatters.service_channel import LootBoxAchievesFormatter, QuestAchievesFormatter, ServiceChannelFormatter, WaitItemsSyncFormatter
from messenger.formatters.service_channel_helpers import MessageData, getCustomizationItemData, getRewardsForBoxes
from new_year.gift_machine_helper import getCoinID
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


class NYPostEventBoxesFormatter(AsyncAutoLootBoxSubFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __MESSAGE_TEMPLATE = 'LootBoxesAutoOpenMessage'
    __REWARDS_TEMPLATE = 'LootBoxRewardsSysMessage'
    __REQUIERED_BOX_TYPES = {NewYearLootBoxes.PREMIUM, NySackLootBox.TYPE}

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            boxIDs = message.data.keys()
            if boxIDs:
                openedBoxesIDs = self.getBoxesOfThisGroup(boxIDs)
                callback([self.__getMainMessage(message, openedBoxesIDs), self.__getRewardsMessage(message, openedBoxesIDs)])
            else:
                callback([MessageData(None, None)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        coins = cls.__itemsCache.items.tokens.getNyCoins()
        return cls._isBoxOfRequiredTypes(boxID, cls.__REQUIERED_BOX_TYPES) or coins and coins.getID() == boxID

    def __getMainMessage(self, message, openedBoxesIDs):
        rows = []
        boxesCount = coinsCount = sacksCount = 0
        coinID = getCoinID()
        boxes = {bID:message.data[bID]['count'] for bID in openedBoxesIDs}
        for boxId, count in boxes.iteritems():
            lootbox = self.__itemsCache.items.tokens.getLootBoxByID(boxId)
            if boxId == coinID:
                coinsCount += count
            if lootbox.getType() == NySackLootBox.TYPE:
                sacksCount += count
            boxesCount += count

        accessor = R.strings.messenger.serviceChannelMessages.lootBoxesAutoOpen
        if boxesCount > 0:
            rows.append(backport.text(accessor.boxesCounter(), count=text_styles.stats(boxesCount)))
        if coinsCount > 0:
            rows.append(backport.text(accessor.coinsCounter(), count=text_styles.stats(coinsCount)))
        if sacksCount > 0:
            rows.append(backport.text(accessor.sacksCounter(), count=text_styles.stats(sacksCount)))
        lootboxes = '<br/>'.join(rows)
        bodyAccessor = accessor.boxesAndCoins
        rewards = getRewardsForBoxes(message, openedBoxesIDs)
        formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'body': backport.text(bodyAccessor()),
         'lootboxes': lootboxes}, data={'savedData': {'rewards': rewards,
                       'boxIDs': boxes}})
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

    @adisp_async
    @adisp_process
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


class LunarNYEnvelopeAutoOpenFormatter(AsyncAutoLootBoxSubFormatter):
    __MESSAGE_TEMPLATE = 'LunarBoxesAutoOpenMessage'
    _DECAL_TYPE_NAME = 'projection_decal'

    def __init__(self):
        super(LunarNYEnvelopeAutoOpenFormatter, self).__init__()
        self._achievesFormatter = QuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            openedBoxesIDs = self.getBoxesOfThisGroup(message.data.keys())
            rewards = getRewardsForBoxes(message, openedBoxesIDs)
            if 'charms' in rewards:
                rewards.pop('charms')
            if 'customizationSum' in rewards:
                rewards.pop('customizationSum')
            fmt = self.formatAchieves(rewards, self._achievesFormatter)
            formattedRewards = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'rewards': fmt})
            settingsRewards = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            settingsRewards.showAt = BigWorld.time()
            callback([MessageData(formattedRewards, settingsRewards)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def formatAchieves(cls, rewards, formatter):
        result = []
        items = getMergedBonusesFromDicts((rewards,))
        formatedItems = formatter.formatQuestAchieves(items, False, processCustomizations=False)
        if formatedItems:
            result.append(formatedItems)
        if 'customizations' in rewards:
            customizations = rewards.get('customizations')
            decalsStr = cls.__makeDecalsString(customizations)
            if decalsStr:
                result.append(decalsStr)
        achievementsNames = cls.__extractAchievements(items)
        if achievementsNames:
            result.append(cls.__makeAchieve('dossiersAccruedInvoiceReceived', dossiers=', '.join(achievementsNames)))
        return '<br/>'.join(result)

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, ALL_LUNAR_NY_LOOT_BOX_TYPES)

    @classmethod
    def __makeAchieve(cls, key, **kwargs):
        return g_settings.htmlTemplates.format(key, kwargs)

    @staticmethod
    def __extractAchievements(data):
        result = set()
        for block in data.get('dossier', {}).values():
            if isinstance(block, dict):
                for record in block.keys():
                    if record[0] == BADGES_BLOCK:
                        continue
                    factory = getAchievementFactory(record)
                    if factory is not None:
                        a = factory.create()
                        if a is not None:
                            result.add(a.getUserName())

        return result

    @classmethod
    def __makeDecalsString(cls, customizations):
        decals = []
        for customization in customizations:
            custType = customization.get('custType', None)
            custValue = customization.get('value', 0)
            if custType == cls._DECAL_TYPE_NAME and custValue > 0:
                _, itemUserName = getCustomizationItemData(customization['id'], custType)
                decals.append(itemUserName)

        if len(decals) > 1:
            decalsTitle = backport.text(R.strings.messenger.serviceChannelMessages.lunarBoxesAutoOpen.many.projection_decal())
            return decalsTitle + ' '.join(decals)
        elif decals:
            decalsTitle = backport.text(R.strings.messenger.serviceChannelMessages.lunarBoxesAutoOpen.projection_decal())
            return ''.join((decalsTitle, decals[0]))
        else:
            return ''

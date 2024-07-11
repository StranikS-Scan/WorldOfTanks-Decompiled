# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/messenger/formatters/service_channel.py
import typing
from adisp import adisp_async, adisp_process
from constants import LOOTBOX_TOKEN_PREFIX, LOOTBOX_KEY_PREFIX
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_helper import getLootBoxIDFromToken
from gui.shared.formatters import text_styles
from gui.shared.formatters.currency import applyAll
from helpers import time_utils, dependency
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, QuestAchievesFormatter, WaitItemsSyncFormatter, LootBoxAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForBoxes
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IGuiLootBoxesController
from gui_lootboxes.gui.bonuses.bonuses_helpers import TOKEN_COMPENSATION_PREFIX
from gui_lootboxes.gui.bonuses.bonuses_helpers import parseCompenstaionToken
from gui.shared.gui_items.loot_box import LootBoxKeyType
if typing.TYPE_CHECKING:
    from typing import List

class LootBoxOpenedFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLootbox = dependency.descriptor(IGuiLootBoxesController)
    __MESSAGE_TEMPLATE = 'LootBoxOpenedSysMessage'
    __SEPARATOR = '<br/>'

    def format(self, message, *args):
        allRewards = message.get('rewards')
        openedLootBoxes = message.get('openedLootBoxes')
        failedKeys = message.get('failedKeys')
        usedKeys = message.get('usedKeys')
        self.__lootboxesAsRewards = self.__getLootboxesAsReceivedRewards(allRewards)
        header = message.get('header', self.__formHeader(openedLootBoxes))
        infoText = message.get('infoText', '')
        receivedRewards, vehicleCompensatedRewards, collectionCompensatedRewards = self.__splitRewards(allRewards)
        dateFmt = backport.getDateTimeFormat(time_utils.getServerRegionalTime())
        openedFmt = self.__formOpenedBoxesSection(openedLootBoxes)
        failFmt = self.__formFailBoxesSection(openedLootBoxes, failedKeys)
        receivedRewardsFmt = self.__formReceivedRewardsSection(receivedRewards)
        compensationFmt = self.__formCompensationSection(vehicleCompensatedRewards, collectionCompensatedRewards)
        failKeyFmt = self.__formFailKeySection(usedKeys)
        mainText = openedFmt + failFmt + receivedRewardsFmt + compensationFmt + failKeyFmt
        formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'header': header,
         'infoText': infoText,
         'date': dateFmt,
         'mainText': mainText})
        settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
        return [MessageData(formatted, settings)]

    def __formHeader(self, openedLootBoxes):
        allCount = 0
        for boxID in openedLootBoxes:
            if boxID not in self.__lootboxesAsRewards:
                allCount += openedLootBoxes[boxID]

        headerStr = backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBox.header()) if allCount == 1 else backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBoxes.header())
        return headerStr

    def __formOpenedBoxesSection(self, openedLootBoxes):
        openedBoxes = []
        for boxID, count in openedLootBoxes.iteritems():
            if self.__lootboxesAsRewards and boxID in self.__lootboxesAsRewards:
                continue
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
            if lootBox is not None and count > 0:
                openedStr = makeHtmlString('html_templates:lobby/quests/bonuses', 'lootBox', {'name': lootBox.getUserName(),
                 'count': count})
                openedBoxes.append(openedStr)

        title = text_styles.titleFont(backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBox.opened()))
        return '' if not openedBoxes else title + self.__SEPARATOR + self.__SEPARATOR.join(openedBoxes) + self.__SEPARATOR

    def __formFailBoxesSection(self, openedLootBoxes, failedKeys):
        failBoxes = []
        for boxID, _ in openedLootBoxes.iteritems():
            if self.__lootboxesAsRewards and boxID in self.__lootboxesAsRewards:
                continue
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
            if lootBox.openedWithKey() and lootBox is not None:
                boxKeys = lootBox.getUnlockKeyIDs()
                countFail = 0
                for keyID, countK in failedKeys.iteritems():
                    if keyID in boxKeys and countK > 0:
                        countFail += countK

                if countFail:
                    openedStr = makeHtmlString('html_templates:lobby/quests/bonuses', 'lootBox', {'name': lootBox.getUserName(),
                     'count': countFail})
                    failBoxes.append(openedStr)

        if not failBoxes:
            return ''
        else:
            title = text_styles.titleFont(backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBox.failopened()))
            return self.__SEPARATOR + title + self.__SEPARATOR + self.__SEPARATOR.join(failBoxes) + self.__SEPARATOR

    def __formFailKeySection(self, usedKeys):
        lockpick = []
        countKey = 0
        countLockpick = 0
        for keyID, count in usedKeys.iteritems():
            key = self.__guiLootbox.getKeyByID(keyID)
            if key:
                if key.keyType == LootBoxKeyType.SIMPLE:
                    countKey += count
                else:
                    countLockpick += count

        if countLockpick:
            lockpick.append(makeHtmlString('html_templates:lobby/quests/bonuses', 'lootBoxKey', {'name': backport.text(R.strings.quests.bonuses.item.lockpick()),
             'count': countLockpick}))
        if countKey:
            lockpick.append(makeHtmlString('html_templates:lobby/quests/bonuses', 'lootBoxKey', {'name': backport.text(R.strings.quests.bonuses.item.lootBoxKey()),
             'count': countKey}))
        title = text_styles.titleFont(backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBox.draw()))
        return '' if not lockpick else self.__SEPARATOR + title + self.__SEPARATOR + self.__SEPARATOR.join(lockpick)

    def __splitRewards(self, allRewards):
        receivedRewards = {}
        vehicleCompensatedRewards = {}
        collectionCompensatedRewards = {}
        for vehicleDict in allRewards.get('vehicles', []):
            vehData = next(vehicleDict.itervalues())
            if 'rentCompensation' in vehData or 'customCompensation' in vehData:
                vehicleCompensatedRewards.setdefault('vehicles', []).append(vehicleDict)
            receivedRewards.setdefault('vehicles', []).append(vehicleDict)

        for token in allRewards.get('tokens', {}).keys():
            if token.startswith(TOKEN_COMPENSATION_PREFIX):
                collectionCompensatedRewards[token] = allRewards['tokens'][token]
            if not token.startswith(LOOTBOX_TOKEN_PREFIX) and not token.startswith(LOOTBOX_KEY_PREFIX) or allRewards['tokens'][token].get('count', 0) > 0:
                receivedRewards.setdefault('tokens', {})[token] = allRewards['tokens'][token]

        for k, v in allRewards.iteritems():
            if k != 'vehicles' and k != 'tokens':
                receivedRewards[k] = v

        return (receivedRewards, vehicleCompensatedRewards, collectionCompensatedRewards)

    def __formReceivedRewardsSection(self, receivedRewards):
        if not receivedRewards:
            return ''
        title = text_styles.titleFont(backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBox.receivedRewards.header()))
        receivedRewardsFmt = QuestAchievesFormatter.formatQuestAchieves(receivedRewards, False)
        return self.__SEPARATOR + title + self.__SEPARATOR + receivedRewardsFmt + self.__SEPARATOR

    def __getVehicleCompensationString(self, compensatedVehicles):
        vehicleCompensationFmt = QuestAchievesFormatter.formatQuestAchieves(compensatedVehicles, False)
        return vehicleCompensationFmt

    def __getCollectionCompensationString(self, compensatedCollections):
        result = []
        for token, data in compensatedCollections.iteritems():
            htmlTemplates = g_settings.htmlTemplates
            currency, value, _, _ = parseCompenstaionToken(token)
            count = data.get('count', 1)
            key = '{}Compensation'.format(currency)
            comp = htmlTemplates.format(key + 'InvoiceReceived', ctx={'amount': applyAll(currency, value * count)})
            result.append(htmlTemplates.format('collectionsCompensation', ctx={'amount': str(count),
             'compensation': comp}))

        return self.__SEPARATOR.join(result)

    def __formCompensationSection(self, vehicleCompensatedRewards, collectionCompensatedRewards):
        if not vehicleCompensatedRewards and not collectionCompensatedRewards:
            return ''
        title = text_styles.titleFont(backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBox.compensation.header()))
        vehicleCompensationFmt = self.__getVehicleCompensationString(vehicleCompensatedRewards)
        collectionsCompensationFmt = self.__getCollectionCompensationString(collectionCompensatedRewards)
        compensationFmt = title + self.__SEPARATOR
        if vehicleCompensationFmt:
            compensationFmt += vehicleCompensationFmt + self.__SEPARATOR
        if collectionsCompensationFmt:
            compensationFmt += collectionsCompensationFmt + self.__SEPARATOR
        return self.__SEPARATOR + compensationFmt

    def __getLootboxesAsReceivedRewards(self, allRewards):
        result = []
        for token in allRewards.get('tokens', {}).keys():
            lootBoxID = getLootBoxIDFromToken(token)
            if lootBoxID and allRewards['tokens'][token].get('count', 0) > 0:
                result.append(lootBoxID)

        return result


class LootBoxAutoOpenFormatter(WaitItemsSyncFormatter):
    __MESSAGE_TEMPLATE = 'LootBoxRewardsSysMessage'
    __SEPARATOR = '<br/>'

    def __init__(self, subFormatters=()):
        super(LootBoxAutoOpenFormatter, self).__init__()
        self._achievesFormatter = LootBoxAchievesFormatter()
        self.__subFormatters = subFormatters

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced and message.data:
            openedBoxesIDs = set(message.data.keys())
            for subFormatter in self.__subFormatters:
                subBoxesIDs = subFormatter.getBoxesOfThisGroup(openedBoxesIDs)
                if subBoxesIDs:
                    if subFormatter.isAsync():
                        result = yield subFormatter.format(message)
                    else:
                        result = subFormatter.format(message)
                    if result:
                        messageDataList.extend(result)
                    openedBoxesIDs.difference_update(subBoxesIDs)

            if openedBoxesIDs:
                data = message.data
                rewards = getRewardsForBoxes(message, data.keys())
                openedLootBoxes = {boxID:data[boxID]['count'] for boxID in openedBoxesIDs}
                failedKeys = {}
                usedKeys = {}
                for boxID in openedBoxesIDs:
                    failedKeys.update(data[boxID].get('failedKeys', {}))
                    usedKeys.update(data[boxID].get('usedKeys', {}))

                self.__calculateLootBoxKey(failedKeys, usedKeys)
                self.__formatTokensRewards(rewards, usedKeys)
                header = self.__formHeader(openedLootBoxes)
                infoText = self.__SEPARATOR + backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.autoOpenedLootBox.opened())
                messageData = LootBoxOpenedFormatter().format({'header': header,
                 'infoText': infoText,
                 'rewards': rewards,
                 'openedLootBoxes': openedLootBoxes,
                 'failedKeys': failedKeys,
                 'usedKeys': usedKeys})[0]
                if messageData is not None:
                    messageDataList.append(messageData)
        if messageDataList:
            callback(messageDataList)
            return
        else:
            callback([MessageData(None, None)])
            return

    def __calculateLootBoxKey(self, failedKeys, usedKeys):
        for key in usedKeys.iterkeys():
            usedKeys[key] += failedKeys.get(key, 0)

        for key in failedKeys.iterkeys():
            if key not in usedKeys.keys():
                usedKeys[key] = failedKeys[key]

    def __formatTokensRewards(self, rewards, usedKeys):
        for token in rewards.get('tokens', {}).keys():
            if token.startswith(LOOTBOX_KEY_PREFIX):
                _, keyID = token.split(':')
                count = rewards['tokens'][token].get('count', 0)
                rewardKeyCount = max(0, usedKeys.get(int(keyID), 0) + count)
                rewards['tokens'][token]['count'] = rewardKeyCount

    def __formHeader(self, boxesData):
        allCount = sum([ boxesData[boxID] for boxID in boxesData ])
        headerStr = backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.autoOpenedLootBox.header()) if allCount == 1 else backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.autoOpenedLootBoxes.header())
        return headerStr

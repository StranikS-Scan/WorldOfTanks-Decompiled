# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/messenger/formatters/service_channel.py
import typing
from adisp import adisp_async, adisp_process
from constants import LOOTBOX_TOKEN_PREFIX
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
from gui_lootboxes.gui.bonuses.bonuses_helpers import TOKEN_COMPENSATION_PREFIX
from gui_lootboxes.gui.bonuses.bonuses_helpers import parseCompenstaionToken
if typing.TYPE_CHECKING:
    from typing import List

class LootBoxOpenedFormatter(ServiceChannelFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __MESSAGE_TEMPLATE = 'LootBoxOpenedSysMessage'
    __SEPARATOR = '<br/>'

    def format(self, message, *args):
        allRewards = message.get('rewards')
        boxesData = message.get('boxesData')
        self.__lootboxesAsRewards = self.__getLootboxesAsReceivedRewards(allRewards)
        header = message.get('header', self.__formHeader(boxesData))
        infoText = message.get('infoText', '')
        receivedRewards, vehicleCompensatedRewards, collectionCompensatedRewards = self.__splitRewards(allRewards)
        dateFmt = backport.getDateTimeFormat(time_utils.getServerRegionalTime())
        openedFmt = self.__formOpenedBoxesSection(boxesData)
        receivedRewardsFmt = self.__formReceivedRewardsSection(receivedRewards)
        compensationFmt = self.__formCompensationSection(vehicleCompensatedRewards, collectionCompensatedRewards)
        formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'header': header,
         'infoText': infoText,
         'date': dateFmt,
         'openedBoxes': openedFmt,
         'receivedRewards': receivedRewardsFmt,
         'compensation': compensationFmt})
        settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
        return [MessageData(formatted, settings)]

    def __formHeader(self, boxesData):
        allCount = 0
        for boxID in boxesData:
            if boxID not in self.__lootboxesAsRewards:
                allCount += boxesData[boxID]

        headerStr = backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBox.header()) if allCount == 1 else backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.openedLootBoxes.header())
        return headerStr

    def __formOpenedBoxesSection(self, boxesData):
        openedBoxes = []
        for boxID, count in boxesData.iteritems():
            if self.__lootboxesAsRewards and boxID in self.__lootboxesAsRewards:
                continue
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
            if lootBox is not None:
                openedStr = makeHtmlString('html_templates:lobby/quests/bonuses', 'lootBox', {'name': lootBox.getUserName(),
                 'count': count})
                openedBoxes.append(openedStr)

        return self.__SEPARATOR.join(openedBoxes)

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
            if not token.startswith(LOOTBOX_TOKEN_PREFIX) or allRewards['tokens'][token].get('count', 0) > 0:
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
        return title + self.__SEPARATOR + self.__SEPARATOR + receivedRewardsFmt

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
        compensationFmt = title + self.__SEPARATOR + self.__SEPARATOR
        if vehicleCompensationFmt:
            compensationFmt += vehicleCompensationFmt + self.__SEPARATOR
        if collectionsCompensationFmt:
            compensationFmt += collectionsCompensationFmt + self.__SEPARATOR
        return compensationFmt

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
                boxesData = {boxID:data[boxID]['count'] for boxID in openedBoxesIDs}
                header = self.__formHeader(boxesData)
                infoText = self.__SEPARATOR + backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.autoOpenedLootBox.opened())
                messageData = LootBoxOpenedFormatter().format({'header': header,
                 'infoText': infoText,
                 'rewards': rewards,
                 'boxesData': boxesData})[0]
                if messageData is not None:
                    messageDataList.append(messageData)
        if messageDataList:
            callback(messageDataList)
            return
        else:
            callback([MessageData(None, None)])
            return

    def __formHeader(self, boxesData):
        allCount = sum([ boxesData[boxID] for boxID in boxesData ])
        headerStr = backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.autoOpenedLootBox.header()) if allCount == 1 else backport.text(R.strings.lb_messenger.serviceChannelMessages.lootbox.autoOpenedLootBoxes.header())
        return headerStr

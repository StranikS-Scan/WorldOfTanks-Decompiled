# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/messenger/formatters/token_quest_subformatters.py
from __future__ import absolute_import
from adisp import adisp_async, adisp_process
from gui.shared.gui_items import getItemTypeID
from gui.shared.gui_items.customization.c11n_items import Style
from helpers import time_utils, dependency
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import AsyncTokenQuestsSubFormatter
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from skeletons.gui.customization import ICustomizationService

class HalloweenStarterBundleFormatter(AsyncTokenQuestsSubFormatter):
    __QUEST_PREFIX = 'hw_rent_vehicles'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        yield self._waitForSyncItems()
        callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(cls.__QUEST_PREFIX)


class HalloweenBattlePassPointsFormatter(AsyncTokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'hwBattlePassPointsMessage'
    __BATTLE_PASS_TOKEN_QUEST_PATTERN = 'battlepass_points'

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls.__BATTLE_PASS_TOKEN_QUEST_PATTERN in questID

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            for qID in completedQuestIDs:
                messageData = self.__buildMessage(qID, message)
                if messageData:
                    messageDataList.extend(messageData)

        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return

    def __buildMessage(self, questID, message):
        result = []
        data = message.data or {}
        battlePassPoints = sum(data.get('battlePassPoints', {}).get('vehicles', {}).values())
        if not battlePassPoints:
            return
        operationTime = message.sentTime
        if operationTime:
            fDatetime = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(operationTime))
        else:
            fDatetime = 'N/A'
        formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'at': fDatetime,
         'bpPoints': battlePassPoints})
        settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
        result.append(MessageData(formatted, settings))
        return result


class HalloweenKingRewardFormatter(AsyncTokenQuestsSubFormatter):
    hwArtifactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    c11n = dependency.descriptor(ICustomizationService)
    __MESSAGE_TEMPLATE = 'tokenQuests'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            result = self.__formatSimpleTokenQuests(message, completedQuestIDs, self.getPopUps(message))
            if result is not None:
                messageDataList.extend(result)
        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return

    def __formatSimpleTokenQuests(self, message, questIDs, popUps):
        rewards = getRewardsForQuests(message, questIDs)
        rewards['popUpRecords'] = popUps
        customizationRewards = []
        for item in rewards.get('customizations', []):
            splittedCustType = item.get('custType', '').split(':')
            itemTypeID = getItemTypeID(splittedCustType[0])
            c11nItem = self.c11n.getItemByID(itemTypeID, item['id'])
            if isinstance(c11nItem, Style) and c11nItem.isLockedOnVehicle:
                continue
            customizationRewards.append(item)

        rewards['customizations'] = customizationRewards
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=True)
        if fmt is not None:
            templateParams = {'achieves': fmt}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
            return [MessageData(formatted, settings)]
        else:
            return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        finalArtefact = cls.hwArtifactsCtrl.getFinalArtefact()
        return questID.startswith(finalArtefact.artefactID) if finalArtefact is not None else False

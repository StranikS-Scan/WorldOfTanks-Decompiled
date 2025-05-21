# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/messenger/formatters/token_quest_subformatters.py
from adisp import adisp_async, adisp_process
from helpers import time_utils, dependency
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import AsyncTokenQuestsSubFormatter
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController

class LSStarterBundleFormatter(AsyncTokenQuestsSubFormatter):
    __QUEST_PREFIX = 'ls_rent_vehicles'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        yield self._waitForSyncItems()
        callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(cls.__QUEST_PREFIX)


class LSBattlePassPointsFormatter(AsyncTokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'lsBattlePassPointsMessage'
    __BATTLE_PASS_TOKEN_QUEST_PATTERN = 'ls_battlepass_points'

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
        battlePassPoints = sum(data.get('battlePassPoints', {}).get('vehicles', {}).itervalues())
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


class LSKingRewardFormatter(AsyncTokenQuestsSubFormatter):
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
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
        rewards['customizations'] = [ item for item in rewards.get('customizations', []) if item['id'] not in self.lsArtifactsCtrl.hiddenBonusStyleIDs ]
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
        finalArtefact = cls.lsArtifactsCtrl.getFinalArtefact()
        return questID.startswith(finalArtefact.artefactID) if finalArtefact is not None else False

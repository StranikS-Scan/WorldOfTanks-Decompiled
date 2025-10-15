# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/messenger/formatters/portal_formatters.py
from messenger.formatters.service_channel import WaitItemsSyncFormatter
from messenger.formatters.token_quest_subformatters import TokenQuestsSubFormatter
from messenger.formatters.service_channel import QuestAchievesFormatter
from messenger.formatters.service_channel import _getAchievementsFromQuestData
from messenger.formatters.service_channel_helpers import MessageData
from portal.gui.portal_event_helpers import isPortalProgressionQuest, isPortalLastLevelQuest, isPortalAllVehicleUpgradesQuest, PROGRESSION_QUEST_PREFIX
from adisp import adisp_async, adisp_process
from messenger import g_settings
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController

class PortalProgressionQuestFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):
    __TEMPLATE = 'PortalProgressionSysMessage'
    __portalController = dependency.descriptor(IPortalEventController)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return isPortalProgressionQuest(questID)

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            for questID in _getCompletedQuests(message):
                if not isPortalProgressionQuest(questID):
                    continue
                rewards = _formatRewards(message, questID)
                stage = int(questID[len(PROGRESSION_QUEST_PREFIX):])
                isMaxLevel = self.__portalController.getTotalLevelsCount() == stage
                res = R.strings.portal_messenger.serviceChannelMessages.progression
                body = res.allStagesCompleted.body() if isMaxLevel else res.stageAchieved.body()
                text = backport.text(body, stage=stage, rewards=rewards)
                messageText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': text})
                messageDataList.append(MessageData(messageText, self._getGuiSettings(message.data, self.__TEMPLATE)))

            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return


class PortalLastLevelQuestFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):
    __TEMPLATE = 'PortalProgressionSysMessage'

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return isPortalLastLevelQuest(questID)

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            for questID in _getCompletedQuests(message):
                rewards = _formatRewards(message, questID)
                text = backport.text(R.strings.portal_messenger.serviceChannelMessages.maxLevelCompleted.body(), rewards=rewards)
                messageText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': text})
                messageDataList.append(MessageData(messageText, self._getGuiSettings(message.data, self.__TEMPLATE)))

            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return


class PortalVehicleUpgradeQuestFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):
    __TEMPLATE = 'PortalProgressionSysMessage'

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return isPortalAllVehicleUpgradesQuest(questID)

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            for questID in _getCompletedQuests(message):
                rewards = _formatRewards(message, questID)
                text = backport.text(R.strings.portal_messenger.serviceChannelMessages.vehicleUpgrade.allVehiclesUpgraded.body(), rewards=rewards)
                messageText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': text})
                messageDataList.append(MessageData(messageText, self._getGuiSettings(message.data, self.__TEMPLATE)))

            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return


class PortalQuestAchievesFormatter(QuestAchievesFormatter):

    @classmethod
    def getFormattedAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(PortalQuestAchievesFormatter, cls).getFormattedAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        achievements = _getAchievementsFromQuestData(data)
        if achievements:
            result.extend(achievements)
        return result


def _getCompletedQuests(message):
    return message.data.get('completedQuestIDs', set())


def _formatRewards(message, questID):
    return PortalQuestAchievesFormatter.formatQuestAchieves(message.data.get('detailedRewards', {}).get(questID, {}), asBattleFormatter=False)

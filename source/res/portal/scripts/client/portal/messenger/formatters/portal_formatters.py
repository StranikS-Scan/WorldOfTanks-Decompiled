# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/messenger/formatters/portal_formatters.py
from adisp import adisp_async, adisp_process
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import WaitItemsSyncFormatter, QuestAchievesFormatter, _getAchievementsFromQuestData
from messenger.formatters.service_channel_helpers import MessageData
from messenger.formatters.token_quest_subformatters import TokenQuestsSubFormatter
from portal.gui.portal_event_helpers import isPortalProgressionQuest, isPortalLastLevelQuest, isPortalAllVehicleUpgradesQuest, PROGRESSION_QUEST_PREFIX, ADD_VEHICLES_QUEST_ID_PREFIX
from portal.skeletons.portal_event_controller import IPortalEventController

class PortalQuestFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):
    __TEMPLATE = 'PortalProgressionSysMessage'
    __portalController = dependency.descriptor(IPortalEventController)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return isPortalProgressionQuest(questID) or isPortalLastLevelQuest(questID) or isPortalAllVehicleUpgradesQuest(questID)

    @adisp_async
    @adisp_process
    def format(self, message, callback=None):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            for questID in _getCompletedQuests(message):
                if isPortalProgressionQuest(questID):
                    messageDataList.append(self._formatProgression(message, questID))
                if isPortalLastLevelQuest(questID):
                    messageDataList.append(self._formatLastLevel(message, questID))
                if isPortalAllVehicleUpgradesQuest(questID):
                    messageDataList.append(self._formatVehicleUpgrade(message, questID))

            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return

    def _formatProgression(self, message, questID):
        rewards = _formatRewards(message, questID)
        stage = int(questID[len(PROGRESSION_QUEST_PREFIX):])
        isMaxLevel = self.__portalController.getTotalLevelsCount() == stage
        res = R.strings.portal_messenger.serviceChannelMessages.progression
        body = res.allStagesCompleted.body() if isMaxLevel else res.stageAchieved.body()
        text = backport.text(body, stage=stage, rewards=rewards)
        messageText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': text})
        return MessageData(messageText, self._getGuiSettings(message.data, self.__TEMPLATE))

    def _formatLastLevel(self, message, questID):
        rewards = _formatRewards(message, questID)
        text = backport.text(R.strings.portal_messenger.serviceChannelMessages.maxLevelCompleted.body(), rewards=rewards)
        messageText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': text})
        return MessageData(messageText, self._getGuiSettings(message.data, self.__TEMPLATE))

    def _formatVehicleUpgrade(self, message, questID):
        rewards = _formatRewards(message, questID)
        text = backport.text(R.strings.portal_messenger.serviceChannelMessages.vehicleUpgrade.allVehiclesUpgraded.body(), rewards=rewards)
        messageText = g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': text})
        return MessageData(messageText, self._getGuiSettings(message.data, self.__TEMPLATE))


class PortalQuestAchievesFormatter(QuestAchievesFormatter):

    @classmethod
    def getFormattedAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(PortalQuestAchievesFormatter, cls).getFormattedAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        achievements = _getAchievementsFromQuestData(data)
        if achievements:
            result.extend(achievements)
        return result


class PortalAddEventVehiclesFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(ADD_VEHICLES_QUEST_ID_PREFIX)


def _getCompletedQuests(message):
    return message.data.get('completedQuestIDs', set())


def _formatRewards(message, questID):
    return PortalQuestAchievesFormatter.formatQuestAchieves(message.data.get('detailedRewards', {}).get(questID, {}), asBattleFormatter=False)

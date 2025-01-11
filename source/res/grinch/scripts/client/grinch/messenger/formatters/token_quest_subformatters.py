# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/messenger/formatters/token_quest_subformatters.py
from grinch_progression.gui.impl.lobby.views.quests_helper import PREFIX
from grinch_progression.skeletons.game_controller import IGrinchProgressionController
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import TokenQuestsSubFormatter, SyncTokenQuestsSubFormatter

class GrinchProgressionRewardsBaseFormatter(ServiceChannelFormatter, TokenQuestsSubFormatter):
    __gpController = dependency.descriptor(IGrinchProgressionController)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(PREFIX)

    def _format(self, message, *_):
        messageData = message.data or {}
        completedQuestIDs = self.getQuestOfThisGroup(messageData.get('completedQuestIDs', set()))
        rewardList = []
        for qID in completedQuestIDs:
            reward = getRewardsForQuests(message, qID)
            formattedMessage = self._formatSingleQuestCompletion(reward)
            if formattedMessage is not None:
                rewardList.append(formattedMessage)

        return rewardList

    def _formatSingleQuestCompletion(self, rewards):
        tokensData = rewards.get('tokens', {})
        token = self.__gpController.token
        nyGp = tokensData.get(token, {})
        amount = nyGp.get('count', 0)
        return None if amount == 0 else MessageData(g_settings.msgTemplates.format('GrinchProgressionMissionRewardMessage', ctx={'amount': amount}), self._getGuiSettings(None, key='GrinchProgressionMissionRewardMessage', priorityLevel=NotificationPriorityLevel.MEDIUM))


class GrinchProgressionRewardsSyncFormatter(SyncTokenQuestsSubFormatter, GrinchProgressionRewardsBaseFormatter):

    def format(self, message, *args):
        return self._format(message, *args)

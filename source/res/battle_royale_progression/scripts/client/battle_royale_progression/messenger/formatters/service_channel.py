# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/messenger/formatters/service_channel.py
from battle_royale_progression.notification.decorators import BRProgressionLockButtonDecorator
from gui.impl import backport
from gui.impl.gen import R
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData

class BRProgressionAchievesFormatter(QuestAchievesFormatter):
    _BULLET = u'\u2022 '
    _SEPARATOR = '<br/>' + _BULLET

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(BRProgressionAchievesFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._BULLET + result if result else result


class BRProgressionSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'BattleRoyaleProgressionSystemMessage'

    def __init__(self):
        super(BRProgressionSystemMessageFormatter, self).__init__()
        self._achievesFormatter = BRProgressionAchievesFormatter()

    def format(self, message, *args):
        return self._format(message, args)

    def _format(self, message, *_):
        messageData = message.data or {}
        stages = messageData.get('stages', set())
        messageDataList = []
        for stage in sorted(stages, key=lambda result: result.get('stage', {})):
            messageData = self._formatSingleStageCompletion(message, stage)
            if messageData:
                messageDataList.append(messageData)

        return messageDataList

    def _formatSingleStageCompletion(self, message, stageInfo):
        rewardsData = stageInfo.get('detailedRewards', {})
        if not rewardsData:
            return None
        else:
            serviceMsg = R.strings.battle_royale_progression.serviceChannelMessages
            decorator = BRProgressionLockButtonDecorator
            messageHeader = backport.text(serviceMsg.header())
            stage = stageInfo.get('stage')
            progressionName = backport.text(serviceMsg.progressionName())
            messageBody = backport.text(serviceMsg.body(), stage=str(stage), progressionName=progressionName)
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False)
            return MessageData(g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': messageHeader,
             'body': messageBody,
             'awards': formattedRewards}, data={}), self._getGuiSettings(message, self.__TEMPLATE, decorator=decorator))

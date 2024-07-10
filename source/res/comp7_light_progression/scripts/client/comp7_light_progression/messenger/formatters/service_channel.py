# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/messenger/formatters/service_channel.py
from comp7_light_progression.notification.decorators import Comp7LightProgressionLockButtonDecorator
from gui.impl import backport
from gui.impl.gen import R
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData

class Comp7LightProgressionAchievesFormatter(QuestAchievesFormatter):
    _BULLET = u'\u2022 '
    _SEPARATOR = '<br/>' + _BULLET

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(Comp7LightProgressionAchievesFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._BULLET + result if result else result


class Comp7LightProgressionSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'Comp7LightProgressionSystemMessage'

    def __init__(self):
        super(Comp7LightProgressionSystemMessageFormatter, self).__init__()
        self._achievesFormatter = Comp7LightProgressionAchievesFormatter()

    def format(self, message, *args):
        return self._format(message, args)

    def _format(self, message, *_):
        messageData = message.data or {}
        results = messageData.get('stages', set())
        messageDataList = []
        for result in sorted(results, key=lambda result: result.get('stage', {})):
            messageDataList.append(self._formatSingleStageCompletion(message, result))

        return messageDataList

    def _formatSingleStageCompletion(self, message, stageInfo):
        decorator = Comp7LightProgressionLockButtonDecorator
        messageHeader = backport.text(R.strings.comp7_light_progression.serviceChannelMessages.header())
        stage = stageInfo.get('stage')
        progressionName = backport.text(R.strings.comp7_light_progression.serviceChannelMessages.progressionName())
        messageBody = backport.text(R.strings.comp7_light_progression.serviceChannelMessages.body(), stage=str(stage), progressionName=progressionName)
        rewardsData = stageInfo.get('detailedRewards', {})
        if not rewardsData:
            return None
        else:
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False)
            return MessageData(g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': messageHeader,
             'body': messageBody,
             'awards': formattedRewards}, data={}), self._getGuiSettings(message, self.__TEMPLATE, decorator=decorator))

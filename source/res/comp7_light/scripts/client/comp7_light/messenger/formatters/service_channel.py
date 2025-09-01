# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/messenger/formatters/service_channel.py
from comp7_light.notification.decorators import Comp7LightProgressionLockButtonDecorator
from constants import SCENARIO_RESULT
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel import BattleResultsFormatter, QuestAchievesFormatter, ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData, parseTokenBonusCount
from skeletons.gui.game_control import IComp7LightController
from skeletons.gui.server_events import IEventsCache

class Comp7LightBattleResultsFormatter(BattleResultsFormatter):
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __eventsCache = dependency.descriptor(IEventsCache)
    _battleResultKeys = {SCENARIO_RESULT.WIN: 'comp7LightBattleVictoryResult',
     SCENARIO_RESULT.PARTIAL: 'comp7LightBattleDrawResult',
     SCENARIO_RESULT.LOSE: 'comp7LightBattleDefeatResult'}

    def _prepareFormatData(self, message):
        templateName, ctx = super(Comp7LightBattleResultsFormatter, self)._prepareFormatData(message)
        ctx['progressionPointsStr'] = self.__makeProgressionPointsString(message)
        return (templateName, ctx)

    def __makeProgressionPointsString(self, message):
        progressionPoints = self.__getProgressionTokenBonus(message.data)
        return g_settings.htmlTemplates.format('battleResultComp7LightProgressionPoints', {'progressionPoints': str(progressionPoints)}) if self.__comp7LightController.isProgressionActive() or progressionPoints > 0 else ''

    def __getProgressionTokenBonus(self, battleResults):
        progressionSettings = self.__comp7LightController.getModeSettings().progression
        if not progressionSettings:
            return 0
        completedQuestIDs = battleResults.get('completedQuestIDs', [])
        completedQuests = self.__eventsCache.getAllQuests(filterFunc=lambda q: q.getID() in completedQuestIDs)
        progressionTokenName = progressionSettings['token']
        tokenBonusCount = 0
        for quest in completedQuests.values():
            for tokenBonus in quest.getBonuses('tokens'):
                tokenBonusCount += parseTokenBonusCount(tokenBonus, progressionTokenName)

        return tokenBonusCount


class Comp7LightProgressionAchievesFormatter(QuestAchievesFormatter):
    _BULLET = u'\u2022 '
    _SEPARATOR = '<br/>' + _BULLET

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(Comp7LightProgressionAchievesFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._BULLET + result if result else result


class Comp7LightProgressionSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'comp7LightProgressionSystemMessage'

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
        messageHeader = backport.text(R.strings.comp7_light.serviceChannelMessages.progressionSystem.header())
        stage = stageInfo.get('stage')
        progressionName = backport.text(R.strings.comp7_light.serviceChannelMessages.progressionName())
        messageBody = backport.text(R.strings.comp7_light.serviceChannelMessages.progressionSystem.body(), stage=str(stage), progressionName=progressionName)
        rewardsData = stageInfo.get('detailedRewards', {})
        if not rewardsData:
            return None
        else:
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False)
            return MessageData(g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': messageHeader,
             'body': messageBody,
             'awards': formattedRewards}, data={}), self._getGuiSettings(message, self.__TEMPLATE, decorator=decorator))

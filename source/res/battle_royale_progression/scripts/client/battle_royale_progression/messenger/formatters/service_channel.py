# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/messenger/formatters/service_channel.py
from constants import LOOTBOX_TOKEN_PREFIX
from helpers import dependency
from battle_royale_progression.notification.decorators import BRProgressionLockButtonDecorator
from gui.impl import backport
from gui.impl.gen import R
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData
from skeletons.gui.shared import IItemsCache

class BRProgressionAchievesFormatter(QuestAchievesFormatter):
    __itemsCache = dependency.descriptor(IItemsCache)
    _BULLET = u'\u2022 '
    _SEPARATOR = '<br/>' + _BULLET
    __LOOTBOX_TEMPLATE = 'SHPLootBoxReceived'
    __STPCOIN_TEMPLATE = 'StPCoinReceived'

    @classmethod
    def formatQuestAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        result = super(BRProgressionAchievesFormatter, cls).formatQuestAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        return cls._BULLET + result if result else result

    @classmethod
    def getFormattedAchieves(cls, data, asBattleFormatter, processCustomizations=True, processTokens=True):
        stpcoinsCount = data.get('currencies', {}).pop('stpcoin', {}).get('count', 0)
        result = super(BRProgressionAchievesFormatter, cls).getFormattedAchieves(data, asBattleFormatter, processCustomizations, processTokens)
        if stpcoinsCount:
            stpcoinResult = g_settings.htmlTemplates.format(cls.__STPCOIN_TEMPLATE, {'count': stpcoinsCount})
            idx = 1 if [ t for t in data.get('tokens', {}) if t.startswith(LOOTBOX_TOKEN_PREFIX) ] else 0
            result.insert(idx, stpcoinResult)
        return result

    @classmethod
    def _processTokens(cls, data):
        boxes = []
        for token, tokenData in data.get('tokens', {}).items():
            if token.startswith(LOOTBOX_TOKEN_PREFIX):
                lootBox = cls.__itemsCache.items.tokens.getLootBoxByTokenID(token)
                if lootBox is not None:
                    boxes.append(backport.text(R.strings.battle_royale_progression.serviceChannelMessages.lootBoxesReceived(), boxName=lootBox.getUserName(), count=tokenData.get('count', 0)))

        return g_settings.htmlTemplates.format(cls.__LOOTBOX_TEMPLATE, {'boxes': ', '.join(boxes)}) if boxes else ''


class BRProgressionSystemMessageFormatter(ServiceChannelFormatter):
    __TEMPLATE = 'BattleRoyaleProgressionSystemMessage'

    def __init__(self):
        super(BRProgressionSystemMessageFormatter, self).__init__()
        self._achievesFormatter = BRProgressionAchievesFormatter()

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
        decorator = BRProgressionLockButtonDecorator
        messageHeader = backport.text(R.strings.battle_royale_progression.serviceChannelMessages.header())
        stage = stageInfo.get('stage')
        progressionName = backport.text(R.strings.battle_royale_progression.serviceChannelMessages.progressionName())
        messageBody = backport.text(R.strings.battle_royale_progression.serviceChannelMessages.body(), stage=str(stage), progressionName=progressionName)
        rewardsData = stageInfo.get('detailedRewards', {})
        if not rewardsData:
            return None
        else:
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False)
            return MessageData(g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'header': messageHeader,
             'body': messageBody,
             'awards': formattedRewards}, data={}), self._getGuiSettings(message, self.__TEMPLATE, decorator=decorator))

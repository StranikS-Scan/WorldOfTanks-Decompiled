# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/messenger/formatters/token_quest_subformatters.py
from adisp import adisp_async, adisp_process
from constants import LOOTBOX_TOKEN_PREFIX
from fun_random.gui.feature.fun_constants import FEP_MODE_ITEMS_QUEST_ID, FEP_PROGRESSION_EXECUTOR_QUEST_ID
from fun_random.gui.feature.util.fun_helpers import getProgressionInfoByExecutor
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.impl.lobby.common.lootboxes import FEP_CATEGORY, FunRandomLootBoxTypes
from fun_random.notification.decorators import FunRandomProgressionStageMessageDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.notifications import NotificationPriorityLevel
from helpers.time_utils import ONE_DAY
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter, QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import TokenQuestsSubFormatter, AsyncTokenQuestsSubFormatter, SyncTokenQuestsSubFormatter

class FunProgressionRewardsBaseFormatter(ServiceChannelFormatter, TokenQuestsSubFormatter, FunAssetPacksMixin, FunProgressionWatcher):
    __INFO_TEMPLATE = 'InformationHeaderSysMessage'
    __PROGRESSION_STAGE_TEMPLATE = 'FunRandomProgressionStage'
    __RES_SHORTCUT = R.strings.fun_random.notification

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(FEP_PROGRESSION_EXECUTOR_QUEST_ID)

    def _getAchievesFormatter(self):
        raise NotImplementedError

    def _format(self, message, *_):
        messageData = message.data or {}
        completedQuestIDs = self.getQuestOfThisGroup(messageData.get('completedQuestIDs', set()))
        completedQuestsInfo = {qID:getProgressionInfoByExecutor(qID) for qID in completedQuestIDs}
        messageDataList = []
        for qID in sorted(completedQuestIDs, key=lambda qID: completedQuestsInfo[qID]):
            messageDataList.append(self._formatSingleQuestCompletion(completedQuestsInfo[qID], getRewardsForQuests(message, {qID})))

        return messageDataList

    def _formatProgressionCompletion(self, progression, rewardsFmt):
        resetText = None
        if not progression.state.isLastProgression:
            resetDays = int(progression.resetTimer // ONE_DAY)
            if resetDays > 0:
                resetText = backport.text(self.__RES_SHORTCUT.progressionComplete.resetTimeLeft(), days=resetDays)
            else:
                resetText = backport.text(self.__RES_SHORTCUT.progressionComplete.resetLessDay())
        msgId = self.__RES_SHORTCUT.progressionComplete()
        if progression.hasUnlimitedProgression:
            msgId = self.__RES_SHORTCUT.progressionComplete.infiniteStarted()
        messageText = backport.text(msgId, modeName=self.getModeUserName())
        messageText = text_styles.concatStylesToMultiLine(messageText, rewardsFmt)
        return text_styles.concatStylesToMultiLine(messageText, '', resetText) if resetText else messageText

    @hasActiveProgression(defReturn=MessageData(None, None))
    def _formatSingleQuestCompletion(self, qInfo, rewards):
        pName, pCounter = qInfo
        currProgression = self.getActiveProgression()
        messageHeader = backport.text(self.__RES_SHORTCUT.congratulation())
        rewardsFmt = self._getAchievesFormatter().formatQuestAchieves(rewards, asBattleFormatter=False)
        messageText, template, priority, decorator = (None,
         self.__INFO_TEMPLATE,
         NotificationPriorityLevel.MEDIUM,
         None)
        if rewardsFmt and currProgression.config.name == pName and pCounter in currProgression.config.executors:
            executors = currProgression.config.executors
            if pCounter != executors[-1]:
                stageIndex = executors.index(pCounter) + 1
                template, decorator = self.__PROGRESSION_STAGE_TEMPLATE, FunRandomProgressionStageMessageDecorator
                messageText = backport.text(self.__RES_SHORTCUT.progressionStageComplete(), modeName=self.getModeUserName(), stage=stageIndex)
                messageText = text_styles.concatStylesToMultiLine(messageText, rewardsFmt)
            else:
                messageText = self._formatProgressionCompletion(currProgression, rewardsFmt)
                priority = NotificationPriorityLevel.HIGH
        return MessageData(g_settings.msgTemplates.format(template, {'header': messageHeader,
         'text': messageText}), self._getGuiSettings(None, key=template, priorityLevel=priority, decorator=decorator)) if messageText else MessageData(None, None)


class FunProgressionRewardsAsyncFormatter(AsyncTokenQuestsSubFormatter, FunProgressionRewardsBaseFormatter):

    def __init__(self):
        super(FunProgressionRewardsAsyncFormatter, self).__init__()
        self._achievesFormatter = FunRandomLootBoxFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = self._format(message) if isSynced else []
        callback(messageDataList)

    def _getAchievesFormatter(self):
        return self._achievesFormatter


class FunProgressionRewardsSyncFormatter(SyncTokenQuestsSubFormatter, FunProgressionRewardsBaseFormatter):

    def __init__(self):
        super(FunProgressionRewardsSyncFormatter, self).__init__()
        self._achievesFormatter = FunRandomLootBoxFormatter()

    def format(self, message, *args):
        return self._format(message, *args)

    def _getAchievesFormatter(self):
        return self._achievesFormatter


class FunRandomLootBoxFormatter(QuestAchievesFormatter, FunAssetPacksMixin):

    @classmethod
    def _processTokens(cls, data):
        result = []
        tokensData = data.get('tokens', {})
        sortedTokens = sorted(tokensData.keys(), key=cls._sortTokenFunc)
        for token in sortedTokens:
            if token.startswith(LOOTBOX_TOKEN_PREFIX):
                lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token)
                if lootBox and lootBox.getCategory() == FEP_CATEGORY:
                    lbName = backport.text(cls.getModeLocalsResRoot().lootbox.dyn(lootBox.getType())())
                    result.append(g_settings.htmlTemplates.format('funRandomLootBox', {'text': lbName,
                     'count': tokensData[token].get('count', 1)}))

        return '\n'.join(result)

    @classmethod
    def _sortTokenFunc(cls, tokenId):
        if tokenId.startswith(LOOTBOX_TOKEN_PREFIX):
            lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(tokenId)
            if lootBox and lootBox.getType() in FunRandomLootBoxTypes.ORDERED:
                return FunRandomLootBoxTypes.ORDERED.index(lootBox.getType())


class FunModeItemsQuestAsyncFormatter(AsyncTokenQuestsSubFormatter, FunAssetPacksMixin):
    __INFO_TEMPLATE = 'InformationHeaderSysMessage'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        isEnabledByLUI = self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount() > 0
        messageDataList = self._format(message) if isSynced and isEnabledByLUI else []
        callback(messageDataList)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(FEP_MODE_ITEMS_QUEST_ID)

    def _format(self, message, *_):
        messageData = message.data or {}
        messageDataList = []
        for qID in self.getQuestOfThisGroup(messageData.get('completedQuestIDs', set())):
            messageDataList.append(self._formatModeItemsSingleQuest(getRewardsForQuests(message, {qID})))

        return messageDataList

    def _formatModeItemsSingleQuest(self, rewards):
        template = self.__INFO_TEMPLATE
        messageHeader = self.getModeUserName()
        messageText = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        messageData = g_settings.msgTemplates.format(template, {'header': messageHeader,
         'text': messageText})
        return MessageData(messageData, self._getGuiSettings(None, key=template))

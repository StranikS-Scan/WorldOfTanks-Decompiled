# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/messenger/formatters/token_quest_subformatters.py
from adisp import adisp_async, adisp_process
from fun_random.gui.feature.fun_constants import FEP_PROGRESSION_EXECUTOR_QUEST_ID
from fun_random.gui.feature.util.fun_helpers import getProgressionInfoByExecutor
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.notification.decorators import FunRandomProgressionStageMessageDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.notifications import NotificationPriorityLevel
from helpers.time_utils import ONE_DAY
from messenger import g_settings
from messenger.formatters.service_channel import ServiceChannelFormatter
from messenger.formatters.service_channel_helpers import MessageData, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import TokenQuestsSubFormatter, AsyncTokenQuestsSubFormatter, SyncTokenQuestsSubFormatter

class FunProgressionRewardsBaseFormatter(ServiceChannelFormatter, TokenQuestsSubFormatter, FunProgressionWatcher):
    _INFO_TEMPLATE = 'InformationHeaderSysMessage'
    _PROGRESSION_STAGE_TEMPLATE = 'FunRandomProgressionStage'
    _RES_SHORTCUT = R.strings.fun_random.notification

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
            resetDays = int(progression.condition.resetTimer // ONE_DAY)
            if resetDays > 0:
                resetText = backport.text(self._RES_SHORTCUT.progressionComplete.resetTimeLeft(), days=resetDays)
            else:
                resetText = backport.text(self._RES_SHORTCUT.progressionComplete.resetLessDay())
        messageText = backport.text(self._RES_SHORTCUT.progressionComplete())
        messageText = text_styles.concatStylesToMultiLine(messageText, rewardsFmt)
        return text_styles.concatStylesToMultiLine(messageText, '', resetText) if resetText else messageText

    @hasActiveProgression(defReturn=MessageData(None, None))
    def _formatSingleQuestCompletion(self, qInfo, rewards):
        pName, pCounter = qInfo
        currProgression = self.getActiveProgression()
        messageHeader = backport.text(self._RES_SHORTCUT.congratulation())
        rewardsFmt = self._getAchievesFormatter().formatQuestAchieves(rewards, asBattleFormatter=False)
        messageText, template, priority, decorator = (None,
         self._INFO_TEMPLATE,
         NotificationPriorityLevel.MEDIUM,
         None)
        if rewardsFmt and currProgression.config.name == pName and pCounter in currProgression.config.executors:
            if pCounter != currProgression.config.executors[-1]:
                template, decorator = self._PROGRESSION_STAGE_TEMPLATE, FunRandomProgressionStageMessageDecorator
                messageText = backport.text(self._RES_SHORTCUT.progressionStageComplete(), counter=pCounter)
                messageText = text_styles.concatStylesToMultiLine(messageText, rewardsFmt)
            else:
                messageText = self._formatProgressionCompletion(currProgression, rewardsFmt)
                priority = NotificationPriorityLevel.HIGH
        return MessageData(g_settings.msgTemplates.format(template, {'header': messageHeader,
         'text': messageText}), self._getGuiSettings(None, key=template, priorityLevel=priority, decorator=decorator)) if messageText else MessageData(None, None)


class FunProgressionRewardsAsyncFormatter(AsyncTokenQuestsSubFormatter, FunProgressionRewardsBaseFormatter):

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = self._format(message) if isSynced else []
        callback(messageDataList)

    def _getAchievesFormatter(self):
        return self._achievesFormatter


class FunProgressionRewardsSyncFormatter(SyncTokenQuestsSubFormatter, FunProgressionRewardsBaseFormatter):

    def format(self, message, *args):
        return self._format(message, *args)

    def _getAchievesFormatter(self):
        return self._achievesFormatter

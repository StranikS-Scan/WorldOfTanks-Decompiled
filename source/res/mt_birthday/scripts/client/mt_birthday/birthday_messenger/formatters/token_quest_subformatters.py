# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_messenger/formatters/token_quest_subformatters.py
from adisp import adisp_async, adisp_process
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger import g_settings
from messenger.formatters.token_quest_subformatters import AsyncTokenQuestsSubFormatter
from messenger.formatters.service_channel import QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData
from mt_birthday_common.constants import MT_BIRTHDAY_QUEST_PROGRESSION_ID
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
MAX_LEVEL = 'max'
DEFAULT_LEVEL = 'default'
INFINITY_LEVEL = 'infinity'

class BirthdayLevelUpFormatter(AsyncTokenQuestsSubFormatter):
    __birthdayController = dependency.descriptor(ITanksBirthdayController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            messages = []
            data = message.data or {}
            questIDs = filter(self._isQuestOfThisGroup, data.get('completedQuestIDs', set()))
            messageSettings = self._getGuiSettings(message, self._getTemplateName(), priorityLevel=NotificationPriorityLevel.MEDIUM)
            questsMap = {int(questID.split('_')[-1]):questID for questID in questIDs}
            for level in sorted(questsMap.keys()):
                rewards = QuestAchievesFormatter.formatQuestAchieves(data.get('detailedRewards', {}).get(questsMap[level], {}), asBattleFormatter=False, processTokens=True)
                header = backport.text(R.strings.mt_birthday.notification.levelUp.congrats.header())
                text = backport.text(R.strings.mt_birthday.notification.levelUp.congrats.dyn(self._getLevel(level)).body(), level=level + 1, rewards=rewards)
                if rewards is not None:
                    formatted = g_settings.msgTemplates.format(self._getTemplateName(), ctx={'header': header,
                     'text': text})
                    messages.append(MessageData(formatted, messageSettings))

            callback(messages)
        else:
            callback([MessageData(None, None)])
        return

    def _getTemplateName(self):
        pass

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(MT_BIRTHDAY_QUEST_PROGRESSION_ID)

    @classmethod
    def _getLevel(cls, level):
        if level < cls.__birthdayController.getMaxProgressionLevel():
            return DEFAULT_LEVEL
        return INFINITY_LEVEL if level > cls.__birthdayController.getMaxProgressionLevel() else MAX_LEVEL

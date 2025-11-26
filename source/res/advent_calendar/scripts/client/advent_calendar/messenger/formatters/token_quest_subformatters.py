# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/messenger/formatters/token_quest_subformatters.py
from __future__ import absolute_import
import logging
import re
from adisp import adisp_async, adisp_process
from advent_calendar.gui.feature.constants import ADVENT_CALENDAR_QUEST_PREFIX, ADVENT_CALENDAR_QUEST_POSTFIX, ADVENT_CALENDAR_PROGRESSION_QUEST
from advent_calendar.messenger.formatters.service_channel import AdventCalendarProgressionAchievesFormatter
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from messenger import g_settings
from messenger.formatters.service_channel_helpers import MessageData
from messenger.formatters.token_quest_subformatters import AsyncTokenQuestsSubFormatter
_logger = logging.getLogger(__name__)

class AdventCalendarQuestRewardFormatter(AsyncTokenQuestsSubFormatter):
    __COMPLETED_PROGRESSION_QUEST_TEMPLATE = 'adventCalendarProgressionQuestReward'
    __COMPLETED_LAST_PROGRESSION_QUEST_TEMPLATE = 'adventCalendarProgressionFinishedReward'
    __COMPLETED_QUESTS_TEMPLATE = 'adventCalendarQuestReward'
    __DAY_PATTERN = '{}(\\d+){}'.format(ADVENT_CALENDAR_QUEST_PREFIX, ADVENT_CALENDAR_QUEST_POSTFIX)
    __adventCalendarCtrl = dependency.descriptor(IAdventCalendarController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            messageDataList = self._format(message)
        if messageDataList:
            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return

    def _format(self, message, *args):
        messageDataList = []
        data = message.data or {}
        completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
        for questID in completedQuestIDs:
            detailRewards = data.get('detailedRewards', {}).get(questID)
            templateParams, template = self.__getTemplateData(questID, detailRewards)
            if templateParams and template:
                settings = self._getGuiSettings(message, template)
                formatted = g_settings.msgTemplates.format(template, templateParams)
                messageDataList.append(MessageData(formatted, settings))
            _logger.error('Failed to build advent calendar quest reward system message')

        return messageDataList

    def __getTemplateData(self, questID, detailRewards):
        if self._isAdventDayQuest(questID):
            return self.__handleQuests(questID, detailRewards)
        else:
            return self.__handleProgressionQuests(questID, detailRewards) if questID.startswith(ADVENT_CALENDAR_PROGRESSION_QUEST) else (None, None)

    def __handleProgressionQuests(self, questID, rewards):
        default = (None, None)
        fmt = AdventCalendarProgressionAchievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if fmt is not None:
            allProgressQuests = self.__adventCalendarCtrl.progressionRewardQuestsOrdered
            if not allProgressQuests:
                _logger.error('Advent progression quests are empty')
                return default
            if questID == allProgressQuests[-1].getID():
                return ({'rewards': fmt}, self.__COMPLETED_LAST_PROGRESSION_QUEST_TEMPLATE)
            return ({'rewards': fmt}, self.__COMPLETED_PROGRESSION_QUEST_TEMPLATE)
        else:
            return default

    def __handleQuests(self, questID, rewards):
        default = (None, None)
        fmt = AdventCalendarProgressionAchievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if fmt is not None:
            dayId = self.__getDayIdFromQuest(questID)
            if dayId is not None:
                header = backport.text(R.strings.advent_calendar.notification.door.opened.title(), dayNumber=dayId)
                return ({'rewards': fmt,
                  'header': header}, self.__COMPLETED_QUESTS_TEMPLATE)
        return default

    @classmethod
    def _isAdventDayQuest(cls, questID):
        return questID.startswith(ADVENT_CALENDAR_QUEST_PREFIX) and questID.endswith(ADVENT_CALENDAR_QUEST_POSTFIX)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls._isAdventDayQuest(questID) or questID.startswith(ADVENT_CALENDAR_PROGRESSION_QUEST)

    @classmethod
    def __getDayIdFromQuest(cls, questID):
        match = re.search(cls.__DAY_PATTERN, questID)
        return match.group(1) if match is not None else None

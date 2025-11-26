# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/messenger/__init__.py
from __future__ import absolute_import
from gui.shared.system_factory import registerTokenQuestsSubFormatters
from advent_calendar.messenger.formatters.token_quest_subformatters import AdventCalendarQuestRewardFormatter

def registerAdventCalendarTokenQuestsSubFormatters():
    registerTokenQuestsSubFormatters([AdventCalendarQuestRewardFormatter()])

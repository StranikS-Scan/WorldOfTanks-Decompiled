# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/AdventCalendarPersonality.py
from advent_calendar.gui.Scaleform import registerAdventCalendarScaleform
from advent_calendar.messenger import registerAdventCalendarTokenQuestsSubFormatters
from advent_calendar.notification import registerAdventNotifications
from advent_calendar.skeletons import registerAdventCalendarController

def preInit():
    registerAdventCalendarController()
    registerAdventCalendarScaleform()
    registerAdventCalendarTokenQuestsSubFormatters()
    registerAdventNotifications()


def init():
    pass


def start():
    pass


def fini():
    pass

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/skeletons/__init__.py
from advent_calendar.gui.game_control.advent_calendar_controller import AdventCalendarController
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from gui.shared.system_factory import registerGameControllers

def registerAdventCalendarController():
    registerGameControllers([(IAdventCalendarController, AdventCalendarController, False)])

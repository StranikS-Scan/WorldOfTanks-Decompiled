# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/shared/event_dispatcher.py
from __future__ import absolute_import
import logging
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from helpers import dependency
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(controller=IAdventCalendarController)
def showAdventCalendarMainWindow(controller=None):
    from advent_calendar.gui.impl.lobby.feature.main_view import AdventCalendarMainWindow
    if AdventCalendarMainWindow.getInstances() or not controller.isAvailable():
        _logger.warning('Can not open the AdventMainView. Feature is not active or view is already opened.')
        return
    AdventCalendarMainWindow().load()


def showAdventCalendarIntroWindow(**kwargs):
    from advent_calendar.gui.impl.lobby.feature.intro_view import AdventCalendarIntroWindow
    if not AdventCalendarIntroWindow.getInstances():
        AdventCalendarIntroWindow(**kwargs).load()


def showRewardWindow(**kwargs):
    from advent_calendar.gui.impl.lobby.feature.reward_view import AdventCalendarRewardWindow
    if AdventCalendarRewardWindow.getInstances():
        _logger.warning('Can not open the AdventCalendarRewardWindow. View is already opened.')
        return
    AdventCalendarRewardWindow(**kwargs).load()

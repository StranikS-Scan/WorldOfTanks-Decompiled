# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/AdventCalendarAccountComponent.py
from __future__ import absolute_import
import typing
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from advent_calendar_common import advent_calendar_account_commands
if typing.TYPE_CHECKING:
    from typing import Callable, Optional

class AdventCalendarAccountComponent(BaseAccountExtensionComponent):

    def openAdventCalendarDoor(self, dayID, callback=None):
        proxy = (lambda requestID, resultID, errorStr: callback(resultID, errorStr)) if callback is not None else None
        self.account._doCmdInt(advent_calendar_account_commands.CMD_OPEN_ADVENT_CALENDAR_DOOR, dayID, proxy)
        return

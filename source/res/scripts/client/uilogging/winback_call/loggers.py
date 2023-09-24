# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/winback_call/loggers.py
import typing
from uilogging.base.logger import MetricsLogger
from uilogging.winback_call.constants import FEATURE, WinBackCallLogActions
if typing.TYPE_CHECKING:
    from uilogging.types import ItemType, ParentScreenType

class WinBackCallLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(WinBackCallLogger, self).__init__(FEATURE)

    def handleClickOnce(self, item, parentScreen):
        self.logOnce(action=WinBackCallLogActions.CLICK, item=item, parentScreen=parentScreen)

    def handleClick(self, item, parentScreen):
        self.log(action=WinBackCallLogActions.CLICK, item=item, parentScreen=parentScreen)

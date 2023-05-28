# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/limited_ui/loggers.py
import typing
from uilogging.base.logger import MetricsLogger
from uilogging.limited_ui.constants import FEATURE, LimitedUILogActions
if typing.TYPE_CHECKING:
    from uilogging.types import ItemType, ParentScreenType

class LimitedUILogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(LimitedUILogger, self).__init__(FEATURE)

    def handleClickOnce(self, item, parentScreen):
        self.logOnce(action=LimitedUILogActions.CLICK, item=item, parentScreen=parentScreen)

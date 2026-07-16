# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/uilogging/last_stand/loggers.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
from last_stand.uilogging.last_stand.constants import NarrationLogAction, FEATURE
from uilogging.base.logger import MetricsLogger
if TYPE_CHECKING:
    from uilogging.types import ItemType

class NarrationEventLogger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(NarrationEventLogger, self).__init__(FEATURE)

    def logStartEvent(self, item):
        self.log(NarrationLogAction.START, item)

    def logEndEvent(self, item):
        self.log(NarrationLogAction.END, item)

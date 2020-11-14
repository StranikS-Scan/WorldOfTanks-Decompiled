# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_point_counter.py
from gui.Scaleform.daapi.view.meta.EventPointCounterMeta import EventPointCounterMeta

class EventPointCounter(EventPointCounterMeta):

    def setPointsCount(self, count):
        self.as_updateCountS(count)

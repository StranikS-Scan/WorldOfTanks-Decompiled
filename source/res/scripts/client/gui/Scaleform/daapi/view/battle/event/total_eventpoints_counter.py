# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/total_eventpoints_counter.py
from gui.Scaleform.daapi.view.meta.PveEventPointCounterMeta import PveEventPointCounterMeta

class TotalEventPointsCounter(PveEventPointCounterMeta):

    def setTotalEventPointsCount(self, epCount):
        self.as_updateCountS(epCount)

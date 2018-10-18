# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/current_eventpoints_counter.py
from gui.Scaleform.daapi.view.meta.PveEventPointCurrentMeta import PveEventPointCurrentMeta

class CurrentEventPointsCounter(PveEventPointCurrentMeta):

    def setCurrentEventPointsCount(self, epCount):
        self.as_updateCountS(epCount)

    def showCurrentEventPointsCounter(self, show):
        self.as_showEventPointCurrentS(show)

    def setNickname(self, nickname):
        self.as_setNicknameS(nickname)

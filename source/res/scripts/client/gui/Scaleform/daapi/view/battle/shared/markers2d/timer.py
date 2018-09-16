# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/timer.py
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
import BigWorld

class StunMarkerTimer(PythonTimer):
    __slots__ = ('__animated', '__stunState')

    def __init__(self, viewObject, typeID, totalTime, currentInterval=1.0, animated=True, stunState=0):
        super(StunMarkerTimer, self).__init__(viewObject, typeID, 0, totalTime, 0, interval=currentInterval)
        self.__animated = animated
        self.__stunState = stunState

    def _showView(self, isBubble=True):
        stunMarker = self._viewObject
        stunMarker.showStunMarker(self._typeID, self.__stunState, self.totalTime, self.__animated)

    def _hideView(self):
        stunMarker = self._viewObject
        stunMarker.hideStunMarker(self._typeID, self.__stunState, -1, self.__animated)

    def _setViewSnapshot(self, leftTime):
        leftTime = self.finishTime - BigWorld.serverTime()
        self._viewObject.showStunMarker(self._typeID, self.__stunState, leftTime, False)

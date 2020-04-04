# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/timer.py
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
import BigWorld

class MarkerTimer(PythonTimer):
    __slots__ = ('__animated', '__statusID', '__vehicleID')

    def __init__(self, viewObject, vehicleID, typeID, totalTime, currentInterval=1.0, animated=True, statusID=0):
        super(MarkerTimer, self).__init__(viewObject, typeID, 0, totalTime, 0, interval=currentInterval)
        self.__animated = animated
        self.__statusID = statusID
        self.__vehicleID = vehicleID

    def _showView(self, isBubble=True):
        stunMarker = self._viewObject
        stunMarker.showMarkerTimer(self.__vehicleID, self._typeID, self.__statusID, self.totalTime, self.__animated)

    def _hideView(self):
        stunMarker = self._viewObject
        stunMarker.hideMarkerTimer(self.__vehicleID, self._typeID, self.__statusID, self.__animated)

    def _setViewSnapshot(self, leftTime):
        leftTime = self.finishTime - BigWorld.serverTime()
        self._viewObject.updateMarkerTimer(self._typeID, leftTime, False, self.__statusID)

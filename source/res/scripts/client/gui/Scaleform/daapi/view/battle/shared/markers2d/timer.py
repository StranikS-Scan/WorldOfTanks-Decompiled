# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/timer.py
from gui.Scaleform.daapi.view.battle.shared.timers_common import PythonTimer
import BigWorld

class MarkerTimer(PythonTimer):
    __slots__ = ('__animated', '__statusID', '__vehicleID', '__showCountdown', '__isSourceVehicle')

    def __init__(self, viewObject, vehicleID, typeID, totalTime, currentInterval=1.0, animated=True, statusID=0, showCountdown=True, isSourceVehicle=False):
        super(MarkerTimer, self).__init__(viewObject, typeID, 0, totalTime, 0, interval=currentInterval)
        self.__animated = animated
        self.__statusID = statusID
        self.__vehicleID = vehicleID
        self.__showCountdown = showCountdown
        self.__isSourceVehicle = isSourceVehicle

    def getStatusID(self):
        return self.__statusID

    def _showView(self, isBubble=True):
        marker = self._viewObject
        marker.showMarkerTimer(self.__vehicleID, self._typeID, self.__statusID, self.totalTime, self.__animated, self.__isSourceVehicle)

    def _hideView(self):
        marker = self._viewObject
        marker.hideMarkerTimer(self.__vehicleID, self._typeID, self.__statusID, -1, self.__animated, self.__isSourceVehicle)

    def _setViewSnapshot(self, leftTime):
        if self.__showCountdown:
            leftTime = self.finishTime - BigWorld.serverTime()
            self._viewObject.updateMarkerTimer(self._typeID, leftTime, False, self.__statusID)

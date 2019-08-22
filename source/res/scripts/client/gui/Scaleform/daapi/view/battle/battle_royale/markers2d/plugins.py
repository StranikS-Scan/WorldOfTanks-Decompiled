# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/markers2d/plugins.py
from functools import partial
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import VehicleMarkerPlugin
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID

class RoyalBattleVehicleMarkerPlugin(VehicleMarkerPlugin):
    _MARKER_SHOWING_TIME = 3
    _IMPORTANT_EVENT = (FEEDBACK_EVENT_ID.VEHICLE_HIT,
     FEEDBACK_EVENT_ID.VEHICLE_RICOCHET,
     FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT,
     FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS,
     FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_DAMAGE,
     FEEDBACK_EVENT_ID.VEHICLE_ARMOR_PIERCED)

    def __init__(self, parentObj, clazz=markers.VehicleMarker):
        super(RoyalBattleVehicleMarkerPlugin, self).__init__(parentObj, clazz)
        self.__focusedVehicleIDs = set()
        self.__squadVehicleIDMarkerID = {}
        self.__hideMarkerTimerIDs = {}
        self.__shouldHide = {}
        self.__lastFocusedVehicleID = None
        return

    def fini(self):
        for mCbId in self.__hideMarkerTimerIDs.values():
            BigWorld.cancelCallback(mCbId)

        super(RoyalBattleVehicleMarkerPlugin, self).fini()

    def addVehicleInfo(self, vInfo, arenaDP):
        super(RoyalBattleVehicleMarkerPlugin, self).addVehicleInfo(vInfo, arenaDP)
        self.__updateSquadData((vInfo,), arenaDP)

    def updateVehiclesInfo(self, updated, arenaDP):
        super(RoyalBattleVehicleMarkerPlugin, self).updateVehiclesInfo(updated, arenaDP)
        self.__updateSquadData([ vInfo for _, vInfo in updated ], arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        super(RoyalBattleVehicleMarkerPlugin, self).invalidateVehiclesInfo(arenaDP)
        self.__createSquadData()

    def _getVehicleMarkerID(self, vehicleID):
        return self._markers[vehicleID].getMarkerID()

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if vehicleID in self.__squadVehicleIDMarkerID:
            super(RoyalBattleVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
            return
        else:
            if eventID == FEEDBACK_EVENT_ID.VEHICLE_IN_FOCUS:
                if value:
                    self.__shouldHide[vehicleID] = False
                    self.__lastFocusedVehicleID = vehicleID
                    self.__activateMarker(vehicleID)
                else:
                    self.__shouldHide[self.__lastFocusedVehicleID] = True
                    self.__lastFocusedVehicleID = None
            else:
                if eventID in self._IMPORTANT_EVENT:
                    self.__shouldHide[vehicleID] = True
                    self.__activateMarker(vehicleID)
                super(RoyalBattleVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
            return

    def _setMarkerActive(self, markerID, active):
        if markerID in self.__squadVehicleIDMarkerID.values():
            super(RoyalBattleVehicleMarkerPlugin, self)._setMarkerActive(markerID, active)
            return
        if active:
            focusedMarkerIDs = [ m.getMarkerID() for vehicleID, m in self._markers.iteritems() if vehicleID in self.__focusedVehicleIDs ]
            if markerID in focusedMarkerIDs:
                super(RoyalBattleVehicleMarkerPlugin, self)._setMarkerActive(markerID, True)
        else:
            super(RoyalBattleVehicleMarkerPlugin, self)._setMarkerActive(markerID, False)

    def _createMarkerWithMatrix(self, symbol, matrixProvider=None, active=True):
        return super(RoyalBattleVehicleMarkerPlugin, self)._createMarkerWithMatrix(symbol, matrixProvider, False)

    def __activateMarker(self, vehicleID):
        self.__focusedVehicleIDs.add(vehicleID)
        if vehicleID not in self.__hideMarkerTimerIDs:
            self._setMarkerActive(self._getVehicleMarkerID(vehicleID), True)
        else:
            BigWorld.cancelCallback(self.__hideMarkerTimerIDs[vehicleID])
        self.__hideMarkerTimerIDs[vehicleID] = BigWorld.callback(self._MARKER_SHOWING_TIME, partial(self.__hideMarker, vehicleID))

    def __hideMarker(self, vehicleID):
        if self.__shouldHide.get(vehicleID, False):
            self._setMarkerActive(self._getVehicleMarkerID(vehicleID), False)
            self.__focusedVehicleIDs.remove(vehicleID)
            del self.__hideMarkerTimerIDs[vehicleID]
        else:
            self.__activateMarker(vehicleID)

    def __createSquadData(self):
        self.__squadVehicleIDMarkerID.clear()
        arenaDP = self.sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if vInfo.vehicleID == self._playerVehicleID or vInfo.isObserver():
                continue
            marker = self._markers.get(vInfo.vehicleID)
            if marker is None:
                continue
            if arenaDP.isSquadMan(vInfo.vehicleID):
                markerId = marker.getMarkerID()
                self.__squadVehicleIDMarkerID[vInfo.vehicleID] = markerId
                self._setMarkerActive(markerId, True)

        return

    def __updateSquadData(self, updatedVehicles, arenaDP):
        for vInfo in updatedVehicles:
            if vInfo.vehicleID == self._playerVehicleID or vInfo.isObserver():
                continue
            marker = self._markers.get(vInfo.vehicleID)
            if marker is None:
                continue
            isSquadMan = arenaDP.isSquadMan(vInfo.vehicleID)
            isAdded = vInfo.vehicleID in self.__squadVehicleIDMarkerID
            if isSquadMan and not isAdded:
                markerId = marker.getMarkerID()
                self.__squadVehicleIDMarkerID[vInfo.vehicleID] = markerId
                self._setMarkerActive(markerId, True)

        return

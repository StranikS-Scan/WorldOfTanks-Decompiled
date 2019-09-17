# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/markers2d.py
from collections import defaultdict
from copy import deepcopy
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import VehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control.battle_constants import MARKER_HIT_STATE
from constants import ARENA_PERIOD
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_EVENT_RACE_VEHICLE_MARKER = 'FestRaceVehicleMarkerUI'
EVENT_RACE_MARKER_ALIAS = 'EventRaceVehicleMarkerPlugin'
_MAX_CAPTURE_POINTS = 100
_DEFAULT_SERVER_POSITION = 127
MARKER_HIT_STATE_NO_BLOCK = deepcopy(MARKER_HIT_STATE)
del MARKER_HIT_STATE_NO_BLOCK[FEEDBACK_EVENT_ID.VEHICLE_HIT]

class EventRaceVehicleMarkerPlugin(VehicleMarkerPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__vehiclesInsideCP', '__enemies', '__arenaPeriod', '__positions')

    def __init__(self, parentObj, clazz=markers.VehicleMarker):
        super(EventRaceVehicleMarkerPlugin, self).__init__(parentObj, clazz)
        self.__arenaPeriod = -1
        self.__vehiclesInsideCP = set()
        self.__enemies = set()
        self.__positions = defaultdict(int)

    def init(self, *args):
        super(EventRaceVehicleMarkerPlugin, self).init(*args)
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        self.__arenaPeriod = arena.period
        if arena is not None:
            arena.onVehicleDropTeamBasePointsOnHit += self.__vehicleDropCapturePoints
            arena.onVehicleLeftTeamBase += self.__vehicleLeftTeamBase
            if self.__arenaPeriod < ARENA_PERIOD.BATTLE:
                arena.onPeriodChange += self.__onArenaPeriodChange
        ctrl = self.sessionProvider.dynamic.eventRepair
        if ctrl is not None:
            ctrl.onOtherRepaired += self.__onRepair
        ctrl = self.sessionProvider.dynamic.eventRacePosition
        if ctrl is not None:
            ctrl.onRacePositionsUpdate += self.__updateAndShowPositions
            ctrl.onRaceFinished += self.__hidePosition
        ctrl = self.sessionProvider.dynamic.vehicleCapturePoints
        if ctrl is not None:
            ctrl.onVehiclePointsChanged += self.__updateVehicleCapturePoints
        return

    def fini(self):
        ctrl = self.sessionProvider.dynamic.vehicleCapturePoints
        if ctrl is not None:
            ctrl.onVehiclePointsChanged -= self.__updateVehicleCapturePoints
        ctrl = self.sessionProvider.dynamic.eventRacePosition
        if ctrl is not None:
            ctrl.onRacePositionsUpdate -= self.__updateAndShowPositions
            ctrl.onRacePositionsUpdate -= self.__updatePositions
            ctrl.onRaceFinished -= self.__hidePosition
        ctrl = self.sessionProvider.dynamic.eventRepair
        if ctrl is not None:
            ctrl.onOtherRepaired -= self.__onRepair
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onVehicleDropTeamBasePointsOnHit -= self.__vehicleDropCapturePoints
            arena.onVehicleLeftTeamBase -= self.__vehicleLeftTeamBase
            arena.onPeriodChange -= self.__onArenaPeriodChange
        self.__vehiclesInsideCP = set()
        self.__enemies = set()
        super(EventRaceVehicleMarkerPlugin, self).fini()
        return

    def _createMarkerWithMatrix(self, _, matrixProvider=None, active=True):
        return self._parentObj.createMarker(_EVENT_RACE_VEHICLE_MARKER, matrixProvider=matrixProvider, active=active)

    def _setMarkerInitialState(self, marker, team, accountDBID=0):
        super(EventRaceVehicleMarkerPlugin, self)._setMarkerInitialState(marker, team, accountDBID)
        vehicleID = marker.getVehicleID()
        if BigWorld.player().team != team:
            self.__enemies.add(vehicleID)
        vehicle = BigWorld.entities.get(vehicleID, None)
        if vehicle is not None:
            if vehicle.raceFinishTime:
                self._invokeMarker(marker.getMarkerID(), 'showPosition', False)
            elif BigWorld.player().arena.arenaInfo is not None:
                position = next((pos for pos, vid in BigWorld.player().arena.arenaInfo.raceList if vid == vehicleID and pos != _DEFAULT_SERVER_POSITION), None)
                if position is not None:
                    self.__positions[vehicleID] = position
                    self._invokeMarker(marker.getMarkerID(), 'setPosition', position)
                if self.__arenaPeriod == ARENA_PERIOD.BATTLE:
                    self._invokeMarker(marker.getMarkerID(), 'showPosition', True)
        self._invokeMarker(marker.getMarkerID(), 'showCapturePoints', False)
        self._invokeMarker(marker.getMarkerID(), 'update')
        return

    def _hideVehicleMarker(self, vehicleID):
        self.__vehiclesInsideCP.discard(vehicleID)
        super(EventRaceVehicleMarkerPlugin, self)._hideVehicleMarker(vehicleID)

    @property
    def _hitStates(self):
        return MARKER_HIT_STATE_NO_BLOCK

    def __onRepair(self, vehicleID, amount, repaired):
        if repaired:
            marker = self._markers[vehicleID]
            self._invokeMarker(marker.getMarkerID(), 'setRepair', amount)

    def __vehicleDropCapturePoints(self, vehicleID):
        if vehicleID in self.__enemies:
            marker = self._markers[vehicleID]
            self._invokeMarker(marker.getMarkerID(), 'resetCapturedPoints')

    def __vehicleLeftTeamBase(self, vehicleID):
        if vehicleID in self.__enemies:
            marker = self._markers[vehicleID]
            self._invokeMarker(marker.getMarkerID(), 'showCapturePoints', False)
            self.__vehiclesInsideCP.discard(vehicleID)

    def __updateVehicleCapturePoints(self, vehicleID, points, prev):
        if vehicleID in self.__enemies and (points != 0 or prev == 0):
            marker = self._markers[vehicleID]
            self._invokeMarker(marker.getMarkerID(), 'setCapturedPoints', min(points, _MAX_CAPTURE_POINTS))
            if vehicleID not in self.__vehiclesInsideCP:
                self._invokeMarker(marker.getMarkerID(), 'showCapturePoints', True)
                self._invokeMarker(marker.getMarkerID(), 'update')
                self.__vehiclesInsideCP.add(vehicleID)

    def __hidePosition(self, vehicleID, raceFinishTime):
        if vehicleID != BigWorld.player().playerVehicleID and raceFinishTime:
            marker = self._markers[vehicleID]
            self._invokeMarker(marker.getMarkerID(), 'showPosition', False)
            self._invokeMarker(marker.getMarkerID(), 'update')

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        self.__arenaPeriod = period
        if period == ARENA_PERIOD.BATTLE:
            arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
            if arena is not None:
                arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __updatePositions(self, raceList):
        for pos, entityID in raceList:
            if entityID != BigWorld.player().playerVehicleID and pos != self.__positions[entityID]:
                self.__positions[entityID] = pos
                marker = self._markers[entityID]
                self._invokeMarker(marker.getMarkerID(), 'setPosition', pos)

    def __updateAndShowPositions(self, raceList):
        if self.__arenaPeriod == ARENA_PERIOD.BATTLE:
            isDataReal = True
            for pos, entityID in raceList:
                isPosReal = pos != _DEFAULT_SERVER_POSITION
                isDataReal = isDataReal and isPosReal
                if entityID != BigWorld.player().playerVehicleID and isPosReal:
                    marker = self._markers[entityID]
                    self.__positions[entityID] = pos
                    self._invokeMarker(marker.getMarkerID(), 'setPosition', pos)
                    self._invokeMarker(marker.getMarkerID(), 'showPosition', True)
                    self._invokeMarker(marker.getMarkerID(), 'update')

            if isDataReal:
                ctrl = self.sessionProvider.dynamic.eventRacePosition
                if ctrl is not None:
                    ctrl.onRacePositionsUpdate -= self.__updateAndShowPositions
                    ctrl.onRacePositionsUpdate += self.__updatePositions
        else:
            self.__updatePositions(raceList)
        return


class EventRaceMarkersManager(MarkersManager):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventRaceMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = EventRaceVehicleMarkerPlugin
        return setup

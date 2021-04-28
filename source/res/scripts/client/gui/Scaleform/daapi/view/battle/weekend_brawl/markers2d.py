# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/markers2d.py
import logging
from Math import Vector3, Vector4, Vector2
from gui.battle_control.battle_constants import UNDEFINED_VEHICLE_ID, VEHICLE_VIEW_STATE
from gui.battle_control.controllers.points_of_interest_ctrl import IPointOfInterestListener
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import PointOfInterestEvent
from weekend_brawl_common import POIActivityStatus, EMPTY_POI_ID
_logger = logging.getLogger(__name__)
_POI_MARKER_TYPE = 'BrawlInterestPointMarkerUI'
_MARKER_POSITION_ADJUSTMENT = Vector3(0.0, 12.0, 0.0)
_BOUNDS_MIN_SCALE = Vector2(1.0, 1.0)
_EMPTY_MARKER_BOUNDS = Vector4(30, 30, 30, 30)
_EMPTY_MARKER_INNER_BOUNDS = Vector4(17, 17, 18, 18)
_MARKER_MIN_SCALE = 40
_NEAR_MARKER_CULL_DISTANCE = 1800

def _isActive(state):
    return state == POIActivityStatus.ACTIVE


class WeekendBrawlMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(WeekendBrawlMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['pointOfInterest'] = PointOfInterestPlugin
        return setup


class PointOfInterestPlugin(plugins.MarkerPlugin, IPointOfInterestListener):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(PointOfInterestPlugin, self).__init__(parentObj)
        self.__markers = {}

    def start(self):
        super(PointOfInterestPlugin, self).start()
        self.__addListeners()
        pointsOfInterestCtrl = self.sessionProvider.dynamic.pointsOfInterest
        if pointsOfInterestCtrl is not None:
            pointsOfInterestCtrl.addPlugin(self)
        self.__restart()
        return

    def stop(self):
        pointsOfInterestCtrl = self.sessionProvider.dynamic.pointsOfInterest
        if pointsOfInterestCtrl is not None:
            pointsOfInterestCtrl.removePlugin(self)
        self.__clearMarkers()
        self.__removeListeners()
        super(PointOfInterestPlugin, self).stop()
        return

    def updateState(self, pointID, newState, startTime, vehicleID=UNDEFINED_VEHICLE_ID):
        markerID = self.__markers.get(pointID)
        if markerID is not None:
            self._invokeMarker(markerID, 'setActive', _isActive(newState))
        return

    def __restart(self):
        self.__clearMarkers()
        pointsOfInterestCtrl = self.sessionProvider.dynamic.pointsOfInterest
        for pointID, position, state in pointsOfInterestCtrl.getPointsOfInterest():
            self.__addPointOfInterest(pointID, position, state)

    def __addPointOfInterest(self, pointID, position, state):
        markerID = self._createMarkerWithPosition(_POI_MARKER_TYPE, position + _MARKER_POSITION_ADJUSTMENT)
        if markerID is None:
            return
        else:
            self._setMarkerRenderInfo(markerID, minScale=_MARKER_MIN_SCALE, offset=_EMPTY_MARKER_BOUNDS, innerOffset=_EMPTY_MARKER_INNER_BOUNDS, cullDistance=_NEAR_MARKER_CULL_DISTANCE, boundsMinScale=_BOUNDS_MIN_SCALE)
            self._setMarkerActive(markerID, _isActive(state))
            self.__markers[pointID] = markerID
            self._setMarkerSticky(markerID, False)
            return

    def __clearMarkers(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()

    def __addListeners(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        g_eventBus.addListener(PointOfInterestEvent.ENTER_INTO_POINT, self.__onEnterIntoPoint, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(PointOfInterestEvent.LEAVE_POINT, self.__onLeavePoint, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __removeListeners(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        g_eventBus.removeListener(PointOfInterestEvent.ENTER_INTO_POINT, self.__onEnterIntoPoint, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(PointOfInterestEvent.LEAVE_POINT, self.__onLeavePoint, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def __onEnterIntoPoint(self, event):
        ctx = event.ctx
        self.__changeVisible(ctx.poiID, isVisible=False)

    def __onLeavePoint(self, event):
        ctx = event.ctx
        self.__changeVisible(ctx.poiID, isVisible=True)

    def __onVehicleStateUpdated(self, state, value):
        ctrl = self.sessionProvider.shared.vehicleState
        if not ctrl.isInPostmortem:
            return
        if state == VEHICLE_VIEW_STATE.POINT_OF_INTEREST:
            pointID = value.poiID
            if pointID != EMPTY_POI_ID:
                self.__changeVisible(pointID, isVisible=False)
                pointIDs = self.__markers.iterkeys()
                if not pointIDs:
                    return
                invisiblePoints = set(pointIDs)
                invisiblePoints.discard(pointID)
                if invisiblePoints:
                    self.__showMarkers(list(invisiblePoints))
            else:
                allPointIDs = self.__markers.iterkeys()
                self.__showMarkers(list(allPointIDs))

    def __changeVisible(self, pointID, isVisible):
        markerID = self.__markers.get(pointID)
        if markerID is not None:
            self._setMarkerActive(markerID, isVisible)
        return

    def __showMarkers(self, pointIDs):
        pointsOfInterestCtrl = self.sessionProvider.dynamic.pointsOfInterest
        for pointID, markerID in self.__markers.iteritems():
            if pointID in pointIDs:
                state = pointsOfInterestCtrl.getPointStatus(pointID)
                self._invokeMarker(markerID, 'setActive', _isActive(state))
                self._setMarkerActive(markerID, True)

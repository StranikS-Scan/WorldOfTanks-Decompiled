# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/shared/markers/markers2d.py
import logging
import BigWorld
import Math
import typing
from portal.gui.battle_control.controllers.portal_gui_controllers import getPortalBattleMarkersController
from portal.gui.Scaleform.daapi.view.battle.shared.markers.mixins import PortalAreaMarkerListener
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from portal_constants import PORTAL_BATTLE_CTRL_ID, PORTAL_GUI_MARKERS_2D
from chat_commands_consts import getUniqueTeamOrControlPointID
from helpers import time_utils
from gui.impl import backport
from gui.impl.gen import R
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from portal.gui.battle_control.controllers.markers.portal_markers_ctrl import PortalMarkersController

class Portal2DAreaMarkersPlugin(plugins.MarkerPlugin, PortalAreaMarkerListener):
    _MARKER_MIN_SCALE = 34
    _MARKER_BOUNDS = Math.Vector4(30, 30, 90, -15)
    _MARKER_INNER_BOUNDS = Math.Vector4(15, 15, 70, -35)
    _MARKER_BOUNDS_MIN_SCALE = Math.Vector2(0.5, 0.5)

    def __init__(self, parentObj):
        super(Portal2DAreaMarkersPlugin, self).__init__(parentObj)
        self.__markers = {}

    def start(self):
        super(Portal2DAreaMarkersPlugin, self).start()
        portalAreaMarkersController = getPortalBattleMarkersController(PORTAL_BATTLE_CTRL_ID.PORTAL_MARKERS_CTRL)
        if portalAreaMarkersController:
            for areaMarker, markerPos in portalAreaMarkersController.getZoneMarkers().itervalues():
                self.__addAreaMarker(areaMarker, markerPos, areaMarker.marker2DEntryID)

        self.startListen()

    def stop(self):
        self.stopListen()
        self.__destroyMarkers()
        super(Portal2DAreaMarkersPlugin, self).stop()

    def _onMarkerToZoneAdded(self, areaMarker, markerPos):
        self.__addAreaMarker(areaMarker, markerPos, areaMarker.marker2DEntryID)

    def _onMarkerFromZoneRemoved(self, areaMarker):
        self.__removeAreaMarker(areaMarker)

    def _onAreaMarkerProgressChanged(self, areaMarker, progress=None, restTime=None, maxHP=None, currentHP=None):
        self.__updateAreaMarkerProgress(areaMarker, progress, restTime, maxHP, currentHP)

    def __addAreaMarker(self, areaMarker, markerPos, markerEntryID):
        if not markerEntryID:
            _logger.info('2D marker is empty for areaMarker %d', areaMarker.id)
            return
        matrix = Math.Matrix()
        matrix.setTranslate(markerPos)
        self.__markers[areaMarker.id] = markerID = self._createMarkerWithMatrix(symbol=markerEntryID, matrixProvider=matrix)
        self._setMarkerRenderInfo(markerID, self._MARKER_MIN_SCALE, self._MARKER_BOUNDS, self._MARKER_INNER_BOUNDS, areaMarker.cullDistance, self._MARKER_BOUNDS_MIN_SCALE)

    def __removeAreaMarker(self, areaMarker):
        markerID = self.__markers.pop(areaMarker.id, None)
        if markerID is not None:
            self._destroyMarker(markerID)
        return

    def __updateAreaMarkerProgress(self, areaMarker, progress=None, restTime=None, maxHP=None, currentHP=None):
        areaMarkerID = areaMarker.id
        if areaMarkerID in self.__markers:
            markerID = self.__markers[areaMarkerID]
            if restTime is not None:
                timeStr = time_utils.getTimeLeftFormat(restTime)
                self._invokeMarker(markerID, 'setCountdown', timeStr)
            elif progress is not None:
                self._invokeMarker(markerID, 'setProgress', progress)
            elif maxHP is not None:
                self._invokeMarker(markerID, 'setVehicleInfo', 'portal', 'portal', backport.text(R.strings.portal_hud_widget.portalHP.title()), 0, '', '', '', '', int(maxHP), 'enemy', False, 0, '')
            elif currentHP is not None:
                self._invokeMarker(markerID, 'setHealth', currentHP)
        else:
            _logger.error('areaMarker not found, id: %d', areaMarkerID)
        return

    def __destroyMarkers(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()


class PortalControlPointsPlugin(plugins.MarkerPlugin):
    _BASE_MARKER_MIN_SCALE = 34.0
    _BASE_MARKER_CULL_DISTANCE = 9999
    _BASE_INNER_MARKER_BOUNDS = Math.Vector4(17, 17, 18, 18)
    _BASE_MARKER_BOUNDS = Math.Vector4(30, 30, 30, 30)
    _BASE_MARKER_BOUND_MIN_SCALE = Math.Vector2(0.5, 0.5)
    _BASE_MARKER_HEIGHT = 40

    def __init__(self, parentObj):
        super(PortalControlPointsPlugin, self).__init__(parentObj)
        self.__markers = {}

    def start(self):
        super(PortalControlPointsPlugin, self).start()
        self._restart()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate += self.__onBasePointsUpdate
        return

    def stop(self):
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate -= self.__onBasePointsUpdate
        self.__removeExistingMarkers()
        super(PortalControlPointsPlugin, self).stop()
        return

    def _restart(self):
        self.__removeExistingMarkers()
        self.__addTeamBasePosition()

    def __onBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        uid = getUniqueTeamOrControlPointID(team, baseID)
        markerID = self.__markers.get(uid)
        if markerID is None:
            _logger.error('No marker with id: %d', uid)
            return
        else:
            self._invokeMarker(markerID, 'setProgress', points)
            return

    def __getTerrainHeightAt(self, spaceID, x, z):
        collisionWithTerrain = BigWorld.collideSegment(spaceID, Math.Vector3(x, 1000.0, z), Math.Vector3(x, -1000.0, z), 128)
        return collisionWithTerrain.closestPoint if collisionWithTerrain is not None else (x, 0, z)

    def __removeExistingMarkers(self):
        for markerKey in self.__markers.iterkeys():
            self._destroyMarker(self.__markers[markerKey])

        self.__markers.clear()

    def __addTeamBasePosition(self):
        positions = self.sessionProvider.arenaVisitor.type.getTeamBasePositionsIterator()
        for team, position, number in positions:
            number = 1 if number == 0 else number
            uid = getUniqueTeamOrControlPointID(team, number)
            self.__addBaseMarker(position, uid)

    def __addBaseMarker(self, position, baseOrControlPointID):
        position = self.__getTerrainHeightAt(BigWorld.player().spaceID, position[0], position[2])
        position[1] += self._BASE_MARKER_HEIGHT
        markerID = self._createMarkerWithPosition(PORTAL_GUI_MARKERS_2D.BASE_MARKER, position)
        if markerID < 0:
            return
        self._setMarkerRenderInfo(markerID, self._BASE_MARKER_MIN_SCALE, self._BASE_MARKER_BOUNDS, self._BASE_INNER_MARKER_BOUNDS, self._BASE_MARKER_CULL_DISTANCE, self._BASE_MARKER_BOUND_MIN_SCALE)
        self.__markers[baseOrControlPointID] = markerID

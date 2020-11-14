# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StaticDeathZone.py
import functools
import random
import enum
import BigWorld
from Math import Vector3, Vector4, Matrix
from items import vehicles
from helpers import dependency
from PlayerEvents import g_playerEvents
from gui.shared import g_eventBus
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_DEBUG_DEV
from gui.shared.gui_items.marker_items import MarkerItem
_BORDER_COLOR = (0.8, 0.0, 0.0, 0.0)
_TIME_TO_STOP_FIRE_ON_LEAVE_ZONE = 5.0

class _DrawType(enum.IntEnum):
    NORMAL = 0
    STRIPES = 1


class StaticDeathZone(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StaticDeathZone, self).__init__()
        self._borders = _BordersHelper()
        self._borderVisuals = []
        self._borderDrawType = _DrawType.NORMAL
        self._warningIsVisible = False
        self.__callbackOnLeaveDeathZone = None
        self.__functionOnLeaveDeathZone = None
        self.__marker = None
        g_eventBus.addListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onAvatarReady += self._onAvatarReady
        return

    def onEnterWorld(self, prereqs):
        self._borders.init(self.position, self.deathzone_size)
        arenaBorderCtrl = self.sessionProvider.shared.arenaBorder
        if arenaBorderCtrl:
            self._updateBorderDrawType(arenaBorderCtrl.getDrawType())
        if self.isActive:
            self._activateDeathZone()

    def onLeaveWorld(self):
        if self.__callbackOnLeaveDeathZone is not None:
            BigWorld.cancelCallback(self.__callbackOnLeaveDeathZone)
            self.__callbackOnLeaveDeathZone = None
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        g_eventBus.removeListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self._removeBorders()
        self._removeMarker()
        return

    def onEntityEnteredInZone(self, entityID):
        player = BigWorld.player()
        if player.playerVehicleID == entityID and self.__marker is not None:
            self.__marker.setVisible(False)
        return

    def onEntityLeftZone(self, entityID):
        player = BigWorld.player()
        if player.playerVehicleID == entityID and player.vehicle.health > 0 and self.__marker is not None:
            self.__marker.setVisible(True)
        return

    def onDeathZoneNotification(self, show, entityID, timeToStrike, waveDuration):
        player = BigWorld.player()
        if player.playerVehicleID == entityID:
            deathzonesCtrl = self.sessionProvider.shared.deathzones
            if deathzonesCtrl:
                deathzonesCtrl.updateDeathZoneWarningNotification(self.zoneId, show, timeToStrike, waveDuration)
            if not show:
                self.__setCallbackOnLeaveDeathZone()

    def onDeathZoneDamage(self, vehicleId, vfx):
        self._playDamageEffect(vehicleId, vfx)

    def _playDamageEffect(self, vehicleId, vfx):
        effects = vehicles.g_cache.getVehicleEffect(vfx)
        if effects:
            effects = random.choice(effects)
            for vehicle in BigWorld.player().vehicles:
                if vehicle.id == vehicleId:
                    self.__functionOnLeaveDeathZone = functools.partial(self._onLeaveDeathZone, vehicle.appearance.playEffectWithStopCallback(effects))

        else:
            LOG_DEBUG_DEV('There are no effects ', vfx)

    def set_isActive(self, _):
        if self.isActive:
            self._activateDeathZone()
        else:
            self._deactivateDeathZone()

    def getClosestPoint(self, point):
        return self._borders.getClosestPoint(point)

    def getCorners(self):
        return self._borders.rect

    def _removeBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.removeBorder(spaceID, self.zoneIndex)

    def _activateDeathZone(self):
        g_playerEvents.onStaticDeathZoneActivated(self)
        self._drawBorders()
        self._createMarker()

    def _deactivateDeathZone(self):
        g_playerEvents.onStaticDeathZoneDeactivated(self.zoneId)
        self._hideBorders()
        self._removeMarker()

    def _drawBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBorderBounds(spaceID, self.zoneIndex, self.position, self._borders.bounds)
            BigWorld.ArenaBorderHelper.setBorderColor(spaceID, self.zoneIndex, _BORDER_COLOR)
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self.zoneIndex, True)

    def _hideBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self.zoneIndex, False)

    def _createMarker(self):
        if self.__marker is None:
            self.__marker = _DeathZoneMarkerHandler(self)
        return

    def _removeMarker(self):
        if self.__marker:
            self.__marker.destroy()
            self.__marker = None
        return

    def _onAvatarReady(self):
        if self.isActive:
            self._activateDeathZone()
            vehicleUnderFire = self._getVehicleUnderFire()
            if vehicleUnderFire is not None:
                timeToStrike = vehicleUnderFire['nextStrikeTime']
                if timeToStrike > 0:
                    deathzonesCtrl = self.sessionProvider.shared.deathzones
                    if deathzonesCtrl:
                        deathzonesCtrl.updateDeathZoneWarningNotification(self.zoneId, True, timeToStrike, vehicleUnderFire['waveDuration'])
                    self._warningIsVisible = True
        return

    def _getVehicleUnderFire(self):
        playerVehicleId = BigWorld.player().playerVehicleID
        for vehicleUnderFire in self.vehiclesUnderFire:
            if vehicleUnderFire['vehicleId'] == playerVehicleId:
                return vehicleUnderFire

        return None

    @property
    def _spaceID(self):
        player = BigWorld.player()
        return player.spaceID if player and player.spaceID else None

    def _updateBorderDrawType(self, arenaDrawType):
        self._borderDrawType = _DrawType.STRIPES if arenaDrawType == _DrawType.NORMAL else _DrawType.NORMAL
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBordersDrawType(spaceID, self.zoneIndex, self._borderDrawType)

    def _onArenaBorderTypeChanged(self, event):
        self._updateBorderDrawType(event.ctx['drawType'])

    def _onLeaveDeathZone(self, callback):
        self.__callbackOnLeaveDeathZone = None
        player = BigWorld.player()
        if not player or not callback:
            return
        else:
            playerPosition = player.getOwnVehiclePosition()
            closestPointOnDeathZone = self.getClosestPoint(playerPosition)
            distanceSquared = (closestPointOnDeathZone - playerPosition).lengthSquared
            if distanceSquared >= 0.0:
                callback()
            return

    def __setCallbackOnLeaveDeathZone(self):
        if self.__functionOnLeaveDeathZone is not None:
            if self.__callbackOnLeaveDeathZone is not None:
                BigWorld.cancelCallback(self.__callbackOnLeaveDeathZone)
            self.__callbackOnLeaveDeathZone = BigWorld.callback(_TIME_TO_STOP_FIRE_ON_LEAVE_ZONE, self.__functionOnLeaveDeathZone)
        return


class _BordersHelper(object):

    def __init__(self):
        self._bounds = Vector4(0, 0, 0, 0)
        self._min = Vector3(0, 0, 0)
        self._max = Vector3(0, 0, 0)

    def init(self, center, size):
        self._bounds = Vector4(-size.x / 2, -size.z / 2, size.x / 2, size.z / 2)
        self._min = Vector3(center.x + self._bounds[0], center.y, center.z + self._bounds[3])
        self._max = Vector3(center.x + self._bounds[2], center.y, center.z + self._bounds[1])

    def getClosestPoint(self, point):
        x = min(max(point[0], self._min.x), self._max.x)
        y = min(max(point[2], self._max.z), self._min.z)
        return Vector3(x, point.y, y)

    @property
    def rect(self):
        return (self._min, self._max)

    @property
    def bounds(self):
        return self._bounds


class _DeathZoneMarkerHandler(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, zone):
        self._zone = zone
        self._matrix = None
        self._markerId = None
        areaMarkerCtrl = self.sessionProvider.shared.areaMarker
        if areaMarkerCtrl:
            self._matrix = Matrix()
            marker = areaMarkerCtrl.createMarker(self._matrix, MarkerItem.DEATHZONE)
            self._markerId = areaMarkerCtrl.addMarker(marker)
            areaMarkerCtrl.onTickUpdate += self._tickUpdate
        return

    def destroy(self):
        areaMarkerCtrl = self.sessionProvider.shared.areaMarker
        if areaMarkerCtrl and self._markerId is not None:
            areaMarkerCtrl.onTickUpdate -= self._tickUpdate
            areaMarkerCtrl.removeMarker(self._markerId)
        self._zone = None
        self._updateTI = None
        self._matrix = None
        self._markerId = None
        return

    def setVisible(self, visible):
        areaMarkerCtrl = self.sessionProvider.shared.areaMarker
        if areaMarkerCtrl and self._markerId is not None:
            if visible:
                areaMarkerCtrl.showMarkersById(self._markerId)
            else:
                areaMarkerCtrl.hideMarkersById(self._markerId)
        return

    def _tickUpdate(self):
        player = BigWorld.player()
        if player and self._matrix is not None:
            self._matrix.setTranslate(self._zone.getClosestPoint(player.getOwnVehiclePosition()))
        return

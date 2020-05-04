# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DeathZone.py
import functools
import random
import cPickle
import BigWorld
from Math import Vector3, Vector4
from items import vehicles
from helpers import dependency
from PlayerEvents import g_playerEvents
from gui.shared import g_eventBus
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from skeletons.gui.battle_session import IBattleSessionProvider
_BORDER_COLOR = (0.8, 0.0, 0.0, 0.0)
_TIME_TO_STOP_FIRE_ON_LEAVE_ZONE = 5.0

class _DRAW_TYPE(object):
    NORMAL = 0
    STRIPES = 1


class DeathZone(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(DeathZone, self).__init__()
        self._borders = None
        self._borderVisuals = []
        self._playerInDeathZone = False
        self._borderDrawType = _DRAW_TYPE.NORMAL
        self._warningIsVisible = False
        self.__callbackOnLeaveDeathZone = None
        self.__functionOnLeaveDeathZone = None
        g_eventBus.addListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onAvatarReady += self._onAvatarReady
        return

    def onEnterWorld(self, prereqs):
        self._borders = _BordersHelper(self.deathzone_position, self.deathzone_size)
        arenaBorderCtrl = self.sessionProvider.shared.arenaBorder
        if arenaBorderCtrl:
            self._updateBorderDrawType(arenaBorderCtrl.getDrawType())

    def onLeaveWorld(self):
        if self.__callbackOnLeaveDeathZone is not None:
            BigWorld.cancelCallback(self.__callbackOnLeaveDeathZone)
            self.__callbackOnLeaveDeathZone = None
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        g_eventBus.removeListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self._removeBorders()
        return

    def onDeathZoneNotification(self, notificationData):
        data = cPickle.loads(notificationData)
        player = BigWorld.player()
        if player.playerVehicleID == data['vehicleID']:
            self._playerInDeathZone = data.get('show', False)
            player.updateDeathZoneWarningNotification(self._playerInDeathZone, data['timeToStrike'], self._warningIsVisible)
            self._warningIsVisible = self._playerInDeathZone
            if not self._playerInDeathZone:
                self.__setCallbackOnLeaveDeathZone()

    def onDeathZoneDamage(self, damageData):
        data = cPickle.loads(damageData)
        effects = vehicles.g_cache.getVehicleEffect(data['vfx'])
        if effects:
            effects = random.choice(effects)
            for vehicle in BigWorld.player().vehicles:
                if vehicle.id == data['vehicleID']:
                    self.__functionOnLeaveDeathZone = functools.partial(self._onLeaveDeathZone, vehicle.appearance.playEffectWithStopCallback(effects))

    def set_isActive(self, _):
        if self.isActive:
            g_playerEvents.onDeathZoneActivated(self)
            self._drawBorders()
        else:
            g_playerEvents.onDeathZoneDeactivated(self.zoneId)
            self._hideBorders()

    def getClosestPoint(self, point):
        x = max(point[0], self._borders.left)
        x = min(x, self._borders.right)
        y = max(point[2], self._borders.bottom)
        y = min(y, self._borders.top)
        return Vector3(x, point[1], y)

    def getCorners(self):
        return self._borders.rect

    @property
    def isPlayerInDeathZone(self):
        return self._playerInDeathZone

    def _removeBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.removeBorder(spaceID, self.zoneIndex)

    def _drawBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBorderBounds(spaceID, self.zoneIndex, self.deathzone_position, self._borders.bounds)
            BigWorld.ArenaBorderHelper.setBorderColor(spaceID, self.zoneIndex, _BORDER_COLOR)
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self.zoneIndex, True)

    def _hideBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self.zoneIndex, False)

    def _onAvatarReady(self):
        if self.isActive:
            g_playerEvents.onDeathZoneActivated(self)
            self._drawBorders()
            timeToStrike = self._getTimeToNextStrike()
            if timeToStrike > 0:
                BigWorld.player().updateDeathZoneWarningNotification(True, timeToStrike, self._warningIsVisible)
                self._warningIsVisible = True

    def _getTimeToNextStrike(self):
        playerVehicleId = BigWorld.player().playerVehicleID
        for vehicleUnderFire in self.vehiclesUnderFire:
            if vehicleUnderFire['vehicleId'] == playerVehicleId:
                return vehicleUnderFire['nextStrikeTime']

    @property
    def _spaceID(self):
        player = BigWorld.player()
        return player.spaceID if player and player.spaceID else None

    def _updateBorderDrawType(self, arenaDrawType):
        self._borderDrawType = _DRAW_TYPE.STRIPES if arenaDrawType == _DRAW_TYPE.NORMAL else _DRAW_TYPE.NORMAL
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

    def __init__(self, center, size):
        self._half_x = size[0] / 2
        self._half_y = size[1] / 2
        center_x, center_y, center_z = center
        self.left = center_x - self._half_x
        self.right = center_x + self._half_x
        self.top = center_z + self._half_y
        self.bottom = center_z - self._half_y
        self._bottom_right = Vector3(self.right, center_y, self.bottom)
        self._top_left = Vector3(self.left, center_y, self.top)

    @property
    def rect(self):
        return (self._top_left, self._bottom_right)

    @property
    def bounds(self):
        return Vector4(-self._half_x, -self._half_y, self._half_x, self._half_y)

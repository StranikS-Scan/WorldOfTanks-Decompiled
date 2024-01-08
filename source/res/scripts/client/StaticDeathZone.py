# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StaticDeathZone.py
import functools
import random
import BigWorld
import Math
import Event
from items import vehicles
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_DEBUG_DEV
from gui.shared.gui_items.marker_items import MarkerItem
from shared_utils import nextTick
_TIME_TO_STOP_FIRE_ON_LEAVE_ZONE = 5.0

class StaticDeathZone(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StaticDeathZone, self).__init__()
        self._warningIsVisible = False
        self.__callbackOnLeaveDeathZone = None
        self.__functionOnLeaveDeathZone = None
        self._marker = None
        self._onActiveChanged = Event.Event()
        self._vehiclesInZone = set()
        return

    @property
    def visual(self):
        return getattr(self, 'clientVisualComp', None)

    @property
    def onActiveChanged(self):
        return self._onActiveChanged

    @property
    def isAvatarReady(self):
        return BigWorld.player().userSeesWorld()

    def onEnterWorld(self, prereqs):
        if self.isAvatarReady:
            nextTick(self._onAvatarReady)()
        else:
            g_playerEvents.onAvatarReady += self._onAvatarReady

    def onLeaveWorld(self):
        self._removeMarker()
        if self.__callbackOnLeaveDeathZone is not None:
            BigWorld.cancelCallback(self.__callbackOnLeaveDeathZone)
            self.__callbackOnLeaveDeathZone = None
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        return

    def getClosestPoint(self, pos, searchRadius):
        return self.position if not self.visual else self.visual.getClosestPoint(pos, searchRadius)

    def onEntityEnteredInZone(self, entityID):
        self._vehiclesInZone.add(entityID)

    def onEntityLeftZone(self, entityID):
        self._vehiclesInZone.discard(entityID)

    def hasVehicle(self, vehicleID):
        return vehicleID in self._vehiclesInZone

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
        self._onActiveChanged(self.isActive)
        if self.isActive:
            self._createMarker()
        else:
            self._removeMarker()

    def _onAvatarReady(self):
        if self.isActive:
            self._createMarker()
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

    def _onLeaveDeathZone(self, callback):
        self.__callbackOnLeaveDeathZone = None
        if not callback:
            return
        else:
            callback()
            return

    def _createMarker(self):
        if self._marker is None and self.isAvatarReady:
            self._marker = _DeathZoneMarkerHandler(self)
        return

    def _removeMarker(self):
        if self._marker:
            self._marker.destroy()
            self._marker = None
        return

    def __setCallbackOnLeaveDeathZone(self):
        if self.__functionOnLeaveDeathZone is not None:
            if self.__callbackOnLeaveDeathZone is not None:
                BigWorld.cancelCallback(self.__callbackOnLeaveDeathZone)
            self.__callbackOnLeaveDeathZone = BigWorld.callback(_TIME_TO_STOP_FIRE_ON_LEAVE_ZONE, self.__functionOnLeaveDeathZone)
        return


class _DeathZoneMarkerHandler(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    SEARCH_RADIUS_EXTENSION = 2.0

    def __init__(self, zone):
        self._zone = zone
        self._matrix = None
        self._markerId = None
        self._searchRadius = 0.0
        areaMarkerCtrl = self.sessionProvider.shared.areaMarker
        if areaMarkerCtrl:
            self._matrix = Math.Matrix()
            marker = areaMarkerCtrl.createMarker(self._matrix, MarkerItem.STATIC_DEATH_ZONE_PROXIMITY)
            self._searchRadius = marker.disappearingRadius + self.SEARCH_RADIUS_EXTENSION
            self._markerId = areaMarkerCtrl.addMarker(marker)
            areaMarkerCtrl.onTickUpdate += self._tickUpdate
        return

    def destroy(self):
        areaMarkerCtrl = self.sessionProvider.shared.areaMarker
        if areaMarkerCtrl and self._markerId is not None:
            areaMarkerCtrl.onTickUpdate -= self._tickUpdate
            areaMarkerCtrl.removeMarker(self._markerId)
        self._zone = None
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
        if not player or self._matrix is None:
            return
        else:
            vehicle = player.getVehicleAttached()
            isVisible = vehicle is not None and not self._zone.hasVehicle(vehicle.id) and vehicle.health > 0
            self.setVisible(isVisible)
            if not isVisible:
                return
            vehiclePos = vehicle.position
            markerPos = self._zone.getClosestPoint(vehiclePos, self._searchRadius)
            if not markerPos:
                markerPos = vehiclePos
                markerPos.y = markerPos.y + self._searchRadius * 2.0
            self._matrix.setTranslate(markerPos)
            return

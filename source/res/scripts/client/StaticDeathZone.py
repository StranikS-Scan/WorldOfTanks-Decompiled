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
from shared_utils import nextTick
from constants import DEATH_ZONE_MASK_PATTERN
_TIME_TO_STOP_FIRE_ON_LEAVE_ZONE = 5.0

class StaticDeathZone(BigWorld.Entity):
    onVehicleEntered = Event.Event()
    onVehicleLeft = Event.Event()
    onDamage = Event.Event()
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StaticDeathZone, self).__init__()
        self._warningIsVisible = False
        self.__callbackOnLeaveDeathZone = None
        self.__functionOnLeaveDeathZone = None
        self._marker = None
        self._onActiveChanged = Event.Event()
        self.onMaskAdded = Event.Event()
        return

    @property
    def visual(self):
        return getattr(self, 'clientVisualComp', None)

    @property
    def masks(self):
        masks = []
        for idx in range(0, self.maskingPolygonsCount):
            comp = self.dynamicComponents.get(DEATH_ZONE_MASK_PATTERN + str(idx))
            if comp is not None:
                masks.append(comp)

        return masks

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

    def onDynamicComponentCreated(self, component):
        if component.keyName.startswith(DEATH_ZONE_MASK_PATTERN):
            self.onMaskAdded(component.udoGuid)

    def onLeaveWorld(self):
        self._removeMarker()
        if self.__callbackOnLeaveDeathZone is not None:
            BigWorld.cancelCallback(self.__callbackOnLeaveDeathZone)
            self.__callbackOnLeaveDeathZone = None
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        if BigWorld.player():
            BigWorld.player().onAvatarVehicleChanged -= self._onAvatarVehicleChanged
        return

    def getClosestPoint(self, pos, searchRadius):
        if not self.visual:
            return self.position
        else:
            distances = [self.visual.getClosestPoint(pos, searchRadius)]
            distances.extend([ mask.getClosestPoint(pos, searchRadius) for mask in self.masks ])
            distances = sorted([ value for value in distances if value is not None ], key=lambda value: value[1])
            return distances[0][0] if distances else None

    def onEntityEnteredInZone(self, entityID):
        if self._marker is not None:
            self._marker.onVehicleEnteredZone(entityID)
        if self.isActive:
            StaticDeathZone.onVehicleEntered(self.zoneId, entityID)
        return

    def onEntityLeftZone(self, entityID):
        if self._marker is not None:
            self._marker.onVehicleLeftZone(entityID)
        if self.isActive:
            StaticDeathZone.onVehicleLeft(self.zoneId, entityID)
        return

    def onDeathZoneNotification(self, show, entityID, timeToStrike, waveDuration):
        player = BigWorld.player()
        if player.vehicle and player.vehicle.id == entityID:
            deathzonesCtrl = self.sessionProvider.shared.deathzones
            if deathzonesCtrl:
                deathzonesCtrl.updateDeathZoneWarningNotification(self.zoneId, show, timeToStrike, waveDuration)
            if not show:
                self.__setCallbackOnLeaveDeathZone()

    def onDeathZoneDamage(self, vehicleId, vfx):
        self._playDamageEffect(vehicleId, vfx)
        StaticDeathZone.onDamage(self.zoneId, vehicleId)

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
        BigWorld.player().onAvatarVehicleChanged += self._onAvatarVehicleChanged
        if self.isActive:
            self._createMarker()
            self._updateVehicleUnderFire()

    def _onAvatarVehicleChanged(self):
        self._updateVehicleUnderFire()

    def _updateVehicleUnderFire(self):
        deathzonesCtrl = self.sessionProvider.shared.deathzones
        if not deathzonesCtrl:
            return
        else:
            vehicleUnderFire = self._getVehicleUnderFire()
            timeToStrike = vehicleUnderFire['nextStrikeTime'] if vehicleUnderFire is not None else 0
            visible = timeToStrike > 0
            waveDuration = vehicleUnderFire['waveDuration'] if visible else 0
            deathzonesCtrl.updateDeathZoneWarningNotification(self.zoneId, visible, timeToStrike, waveDuration)
            self._warningIsVisible = visible
            return

    def _getVehicleUnderFire(self):
        vehicle = BigWorld.player().vehicle if BigWorld.player().vehicle else None
        if not vehicle:
            return
        else:
            for vehicleUnderFire in self.vehiclesUnderFire:
                if vehicleUnderFire['vehicleId'] == vehicle.id:
                    return vehicleUnderFire

            return

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
        self._vehiclesInZone = set()
        areaMarkerCtrl = self.sessionProvider.shared.areaMarker
        if areaMarkerCtrl:
            self._matrix = Math.Matrix()
            marker = areaMarkerCtrl.createMarker(self._matrix, self._zone.proximityMarkerStyle)
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

    def onVehicleEnteredZone(self, vehID):
        self._vehiclesInZone.add(vehID)

    def onVehicleLeftZone(self, vehID):
        self._vehiclesInZone.discard(vehID)

    def _tickUpdate(self):
        player = BigWorld.player()
        if not player or self._matrix is None:
            return
        else:
            vehicle = player.getVehicleAttached()
            isVisible = vehicle is not None and vehicle.id not in self._vehiclesInZone and vehicle.health > 0
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

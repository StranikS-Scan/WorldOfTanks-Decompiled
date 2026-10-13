# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWDeathZone.py
from __future__ import absolute_import, division
import BigWorld
import Event
from shared_utils import nextTick
from PlayerEvents import g_playerEvents
from LimitedVisibilityEntity import LimitedVisibilityEntity
from StaticDeathZone import DeathZoneMarkerHandler
from halloween_dyn_object_cache import getModel
_TICK_UPDATE_TIME = 0

class HWDeathZone(LimitedVisibilityEntity):
    onResizeDeathZone = Event.Event()

    def __init__(self):
        super(HWDeathZone, self).__init__()
        self.onActiveChanged = Event.Event()
        self.onMaskAdded = Event.Event()
        self._tickTimerID = None
        self._marker = None
        self._vehiclesInside = set(self.vehiclesInside)
        self._serverTime = self.requestedTransform.begin
        self._position = self.serverTransform.position
        self._zoneSize = self.serverTransform.size
        self._rotation = self.serverTransform.rotation
        self._transformPosPerSec = 0
        self._transformSizePerSec = 0
        self._transformRotationPerSec = 0
        self._transform()
        return

    def onEnterWorld(self, prereqs):
        if self.isAvatarReady:
            nextTick(self._onAvatarReady)()
        else:
            g_playerEvents.onAvatarReady += self._onAvatarReady

    def onLeaveWorld(self):
        self._removeMarker()
        g_playerEvents.onAvatarReady -= self._onAvatarReady
        self._clearTickTimer()

    def _onAvatarReady(self):
        if self.isActive:
            self._transform()
            self._createMarker()
            self._resize(self._position, self._zoneSize, self._rotation, True)

    @property
    def position(self):
        return self._position

    @property
    def zoneSize(self):
        return self._zoneSize

    @property
    def rotation(self):
        return self._rotation

    @property
    def visual(self):
        return getattr(self, 'clientVisualComp', None)

    def set_isActive(self, _):
        self.onActiveChanged(self.isActive)
        if self.isActive:
            self._createMarker()
        else:
            self._removeMarker()

    def set_requestedTransform(self, _):
        self._transform(True)

    def set_vehiclesInside(self, _):
        newVehiclesInside = set(self.vehiclesInside)
        if self._marker:
            for vehId in self._vehiclesInside - newVehiclesInside:
                self._marker.onVehicleLeftZone(vehId)

            for vehId in newVehiclesInside - self._vehiclesInside:
                self._marker.onVehicleEnteredZone(vehId)

        self._vehiclesInside = newVehiclesInside

    @property
    def udoGuid(self):
        return None

    @property
    def masks(self):
        return [self]

    @property
    def polygonCenter(self):
        return self._position

    @property
    def isAvatarReady(self):
        return BigWorld.player().userSeesWorld()

    def getDimensions(self):
        if not self.visual:
            return self._zoneSize
        polygon = self.visual.getPolygon()
        x, z = zip(*polygon)
        return (max(x) - min(x), 0, max(z) - min(z))

    def getClosestPoint(self, pos, searchRadius):
        return self.position if not self.visual else self.visual.getClosestPointInverted(pos, searchRadius)[0]

    def getBorderModel(self, borderID):
        return getModel(borderID)

    def _transform(self, requested=False):
        if self.requestedTransform.begin > 0 and self.requestedTransform.until > 0:
            if requested:
                self._serverTime = BigWorld.serverTime()
            else:
                self._serverTime = self.requestedTransform.begin
            duration = self.requestedTransform.until - self._serverTime
            self._transformPosPerSec = (self.requestedTransform.position - self._position) / duration
            self._transformSizePerSec = (self.requestedTransform.size - self._zoneSize) / duration
            self._transformRotationPerSec = (self.requestedTransform.rotation - self._rotation) / duration
            self._tick()
        elif not self.requestedTransform.begin and not self.requestedTransform.until:
            self._resize(self.serverTransform.position, self.serverTransform.size, self.serverTransform.rotation)

    def _resize(self, position, zoneSize, rotation, force=False):
        if not force and self._position == position and self._zoneSize == zoneSize and self._rotation == rotation:
            return
        self._position = position
        self._zoneSize = zoneSize
        self._rotation = rotation
        if self.visual:
            self.visual.resize(position, zoneSize, rotation)
        self.onResizeDeathZone(self)

    def _createMarker(self):
        if self._marker is None and self.isAvatarReady:
            self._marker = DeathZoneMarkerHandler(self)
            for vehId in self.vehiclesInside:
                self._marker.onVehicleEnteredZone(vehId)

        return

    def _removeMarker(self):
        if self._marker:
            self._marker.destroy()
            self._marker = None
        return

    def _tick(self):
        self._clearTickTimer()
        st = BigWorld.serverTime()
        if st >= self.requestedTransform.until:
            position = self.requestedTransform.position
            size = self.requestedTransform.size
            rotation = self.requestedTransform.rotation
        else:
            position = self._position + (st - self._serverTime) * self._transformPosPerSec
            size = self._zoneSize + (st - self._serverTime) * self._transformSizePerSec
            rotation = self._rotation + (st - self._serverTime) * self._transformRotationPerSec
            self._tickTimerID = BigWorld.callback(_TICK_UPDATE_TIME, self._tick)
        self._resize(position, size, rotation)
        self._serverTime = st

    def _clearTickTimer(self):
        if self._tickTimerID:
            BigWorld.cancelCallback(self._tickTimerID)
            self._tickTimerID = None
        return

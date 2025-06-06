# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/artillery/plugins.py
import logging
import BattleReplay
from constants import ArtilleryZoneType
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from Math import Vector4, Vector2
from helpers.time_utils import MS_IN_SECOND
_logger = logging.getLogger(__name__)
_SECTOR_BASES_BOUNDS_MIN_SCALE = Vector2(1.0, 1.0)
_MEDIUM_MARKER_MIN_SCALE = 100
_EMPTY_MARKER_BOUNDS = Vector4(0.0, 0.0, 0.0, 0.0)
_EMPTY_MARKER_INNER_BOUNDS = Vector4(0.0, 0.0, 0.0, 0.0)
_MAX_CULL_DISTANCE = 1000000.0
_SMALL_MARKER_MIN_SCALE = 40
_NEAR_MARKER_CULL_DISTANCE = 300
_TIMER_MIN_DELTA_MS = 100

class ArtilleryTimeZonePlugin(plugins.MarkerPlugin):
    __slots__ = ('__markers', '__leftTimeInReplay')

    def __init__(self, parentObj):
        super(ArtilleryTimeZonePlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__leftTimeInReplay = {}

    def init(self):
        super(ArtilleryTimeZonePlugin, self).init()
        artilleryTimeZoneComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'artilleryTimeZoneComponent', None)
        if artilleryTimeZoneComponent is not None:
            artilleryTimeZoneComponent.onTimeZoneAdded += self._onTimeZoneAdded
            artilleryTimeZoneComponent.onTimeZoneRemoved += self._onTimeZoneRemoved
            if BattleReplay.isPlaying():
                artilleryTimeZoneComponent.onTimeZoneTimerUpdated += self._onTimeZoneTimerUpdated
        return

    def fini(self):
        artilleryTimeZoneComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'artilleryTimeZoneComponent', None)
        if artilleryTimeZoneComponent is not None:
            artilleryTimeZoneComponent.onTimeZoneAdded -= self._onTimeZoneAdded
            artilleryTimeZoneComponent.onTimeZoneRemoved -= self._onTimeZoneRemoved
            artilleryTimeZoneComponent.onTimeZoneTimerUpdated -= self._onTimeZoneTimerUpdated
        super(ArtilleryTimeZonePlugin, self).fini()
        return

    def stop(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()
        self.__leftTimeInReplay.clear()
        super(ArtilleryTimeZonePlugin, self).stop()

    def _onTimeZoneAdded(self, shotId, startTime, duration, pos, radius, zoneType):
        marker = settings.MARKER_SYMBOL_NAME.EXPLOSION_ZONE_MARKER if zoneType in (ArtilleryZoneType.EXPLOSION, ArtilleryZoneType.FRIENDLY) else settings.MARKER_SYMBOL_NAME.ARTILLERY_TARGET_MARKER
        handle = self._createMarkerWithPosition(marker, pos + settings.MARKER_POSITION_ADJUSTMENT)
        if handle is None:
            return
        else:
            self._setMarkerActive(handle, True)
            self._setMarkerSticky(handle, True)
            self._setMarkerRenderInfo(handle, _SMALL_MARKER_MIN_SCALE, _EMPTY_MARKER_BOUNDS, _EMPTY_MARKER_INNER_BOUNDS, _NEAR_MARKER_CULL_DISTANCE, _SECTOR_BASES_BOUNDS_MIN_SCALE)
            self.__markers[shotId] = handle
            leftTime = duration * MS_IN_SECOND
            self.__leftTimeInReplay[shotId] = leftTime
            self._invokeMarker(handle, 'updateData', zoneType == ArtilleryZoneType.FRIENDLY, leftTime, BattleReplay.isPlaying())
            return

    def _onTimeZoneTimerUpdated(self, shotId, timeLeft):
        handle = self.__markers.get(shotId)
        if handle is None or timeLeft < 0:
            return
        else:
            timeLeft = round(timeLeft * MS_IN_SECOND, 1)
            if self.__leftTimeInReplay[shotId] - timeLeft >= _TIMER_MIN_DELTA_MS:
                self.__leftTimeInReplay[shotId] = timeLeft
                self._invokeMarker(handle, 'updateTextInReplay', timeLeft)
            return

    def _onTimeZoneRemoved(self, shotId):
        if shotId in self.__markers:
            self._destroyMarker(self.__markers[shotId])
            self.__markers.pop(shotId)
            self.__leftTimeInReplay.pop(shotId)

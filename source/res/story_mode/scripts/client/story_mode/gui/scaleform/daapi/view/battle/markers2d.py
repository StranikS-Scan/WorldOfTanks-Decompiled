# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/markers2d.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from helpers import dependency
from story_mode.skeletons.voiceover_controller import IVoiceoverManager
_MARKER_CRITICAL_HIT_STATES = {FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT,
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_DAMAGE,
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS,
 FEEDBACK_EVENT_ID.VEHICLE_CRITICAL_HIT_CHASSIS_PIERCED}

class StoryModeMarkersManager(MarkersManager):
    __slots__ = ()

    def _setupPlugins(self, arenaVisitor):
        setup = super(StoryModeMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = StoryModeVehicleMarkerPlugin
        return setup

    @property
    def _isMarkerHoveringEnabled(self):
        return False


class StoryModeVehicleMarkerPlugin(VehicleMarkerPlugin):
    __slots__ = ()
    _voiceoverManager = dependency.descriptor(IVoiceoverManager)

    def start(self):
        super(StoryModeVehicleMarkerPlugin, self).start()
        self._hiddenEvents = _MARKER_CRITICAL_HIT_STATES
        self._voiceoverManager.onStarted += self._voiceoverHandler
        self._voiceoverManager.onStopped += self._voiceoverHandler
        if self._voiceoverManager.isPlaying:
            self._voiceoverHandler()

    def stop(self):
        self._voiceoverManager.onStarted -= self._voiceoverHandler
        self._voiceoverManager.onStopped -= self._voiceoverHandler
        super(StoryModeVehicleMarkerPlugin, self).stop()

    def _voiceoverHandler(self):
        ctx = self._voiceoverManager.currentCtx
        if ctx is None:
            return
        else:
            vehicleId = ctx.get('vehicleId', None)
            if not vehicleId:
                return
            if vehicleId not in self._markers:
                return
            marker = self._markers[vehicleId]
            markerId = marker.getMarkerID()
            flag = self._voiceoverManager.isPlaying
            if marker.setSpeaking(flag):
                self._invokeMarker(markerId, 'setSpeaking', flag)
            return

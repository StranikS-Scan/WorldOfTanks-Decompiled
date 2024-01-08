# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/FLStealthRadarComponent.py
import BigWorld
from PlayerEvents import g_playerEvents
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from frontline import invalidateVehicleMarkerState, isAvatarReady
from vehicle_systems.stricted_loading import makeCallbackWeak

class FLStealthRadarComponent(BigWorld.DynamicScriptComponent):
    _CALLBACK_DELAY = 0.5

    def __init__(self):
        super(FLStealthRadarComponent, self).__init__()
        if isAvatarReady():
            self.__invalidateStealthRadarState()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def set_stealthRadar(self, _=None):
        self.__invalidateStealthRadarState()

    def onLeaveWorld(self):
        pass

    def __onAvatarReady(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        BigWorld.callback(self._CALLBACK_DELAY, makeCallbackWeak(self.__invalidateStealthRadarState))

    def __invalidateStealthRadarState(self):
        invalidateVehicleMarkerState(self.entity, self.stealthRadar, self.stealthRadar, VEHICLE_VIEW_STATE.STEALTH_RADAR, 'invalidateStealthRadar')

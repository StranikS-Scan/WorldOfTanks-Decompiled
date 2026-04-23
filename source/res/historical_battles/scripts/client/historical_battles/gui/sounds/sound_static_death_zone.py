# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_static_death_zone.py
import SoundGroups
from gui.battle_control.battle_constants import TIMER_VIEW_STATE, VEHICLE_VIEW_STATE
from gui.battle_control.controllers.sound_ctrls.common import VehicleStateSoundPlayer
from historical_battles.gui.sounds.sound_constants import HBStaticDeathZoneEvents

class HBStaticDeathZoneSound(VehicleStateSoundPlayer):

    def __init__(self):
        super(HBStaticDeathZoneSound, self)._subscribe()
        self.__isInZone = None
        return

    def destroy(self):
        self.__stopEvent()
        super(HBStaticDeathZoneSound, self).destroy()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DEATHZONE:
            zoneLevel = value.level
            if zoneLevel is None:
                vehicle = self._sessionProvider.shared.vehicleState.getControllingVehicle()
                isAlive = vehicle is not None and vehicle.isAlive()
                zoneLevel = TIMER_VIEW_STATE.CRITICAL if isAlive else None
            if zoneLevel != self.__isInZone:
                self.__stopEvent()
                if zoneLevel and zoneLevel != TIMER_VIEW_STATE.CRITICAL:
                    SoundGroups.g_instance.playSound2D(HBStaticDeathZoneEvents.START_TIMER)
                self.__isInZone = zoneLevel
        return

    def __stopEvent(self):
        if self.__isInZone is not None:
            SoundGroups.g_instance.playSound2D(HBStaticDeathZoneEvents.STOP_TIMER)
            self.__isInZone = None
        return

    def _onSwitchViewPoint(self):
        self.__stopEvent()

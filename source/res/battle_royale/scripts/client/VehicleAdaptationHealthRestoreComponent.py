# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleAdaptationHealthRestoreComponent.py
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent

class VehicleAdaptationHealthRestoreComponent(VehicleAbilityBaseComponent):
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.ADAPTATION_HEALTH_RESTORE
    __MARKER_ID = BATTLE_MARKER_STATES.ADAPTATION_HEALTH_RESTORE_STATE

    def __init__(self):
        super(VehicleAdaptationHealthRestoreComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def _onAvatarReady(self):
        self.set_finishTime()
        self.set_restoreHealth()

    def set_restoreHealth(self, _=None):
        data = self._getTimerData()
        data['restoreHealth'] = self.restoreHealth
        self._updateTimer(data)

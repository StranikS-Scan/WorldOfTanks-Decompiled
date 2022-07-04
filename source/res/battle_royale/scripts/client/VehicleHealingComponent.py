# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleHealingComponent.py
import BigWorld
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent

class VehicleHealingComponent(VehicleAbilityBaseComponent):
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.HEALING
    __MARKER_ID = BATTLE_MARKER_STATES.HEALING_STATE

    def __init__(self):
        self._isDestroying = False
        super(VehicleHealingComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def set_isInactivation(self, prev):
        self._updateVisuals()

    def _updateTimer(self, data):
        data.update({'isInactivation': self.isInactivation,
         'isSourceVehicle': self.getIsSourceVehicle()})
        super(VehicleHealingComponent, self)._updateTimer(data)

    def _updateMarker(self, data, isHide=False):
        data.update({'isSourceVehicle': self.getIsSourceVehicle()})
        super(VehicleHealingComponent, self)._updateMarker(data, isHide)

    def getIsSourceVehicle(self):
        return self.entity.id == BigWorld.player().getObservedVehicleID()

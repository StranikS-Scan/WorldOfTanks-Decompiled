# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleShotPassionComponent.py
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from battle_royale.gui.constants import BattleRoyaleEquipments
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent

class VehicleShotPassionComponent(VehicleAbilityBaseComponent):
    EQUIPMENT_NAME = BattleRoyaleEquipments.SHOT_PASSION
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.SHOT_PASSION
    __MARKER_ID = BATTLE_MARKER_STATES.SHOT_PASSION_STATE

    def __init__(self):
        super(VehicleShotPassionComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def set_stage(self, prev):
        data = {'duration': self._getDuration()}
        self._updateTimer(data)

    def getInfo(self):
        data = {'duration': self._getDuration(),
         'stage': self.stage}
        return data

    def _updateTimer(self, data):
        data['stage'] = self.stage
        super(VehicleShotPassionComponent, self)._updateTimer(data)
        self._guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.EQUIPMENT_NAME, self.entity.id, data)

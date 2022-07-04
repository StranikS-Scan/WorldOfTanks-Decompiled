# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleBerserkerComponent.py
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent

class VehicleBerserkerComponent(VehicleAbilityBaseComponent):
    __EQUIPMENT_NAME = BattleRoyaleEquipments.BERSERKER
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.BERSERKER
    __MARKER_ID = BATTLE_MARKER_STATES.BERSERKER_STATE

    def __init__(self):
        self.__id = id(self)
        super(VehicleBerserkerComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def _updateTimer(self, data):
        data['tickInterval'] = self.tickInterval
        super(VehicleBerserkerComponent, self)._updateTimer(data)
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.__EQUIPMENT_NAME, self.entity.id, data)

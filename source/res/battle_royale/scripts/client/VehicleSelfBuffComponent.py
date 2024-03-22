# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleSelfBuffComponent.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent

class VehicleSelfBuffComponent(VehicleAbilityBaseComponent):
    EQUIPMENT_NAME = BattleRoyaleEquipments.SELF_BUFF
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.INSPIRE
    __MARKER_ID = BATTLE_MARKER_STATES.INSPIRING_STATE

    def __init__(self):
        super(VehicleSelfBuffComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def _updateTimer(self, data):
        duration = self._getDuration()
        isHide = self.entity.id != BigWorld.player().getObservedVehicleID() or duration == 0
        data['endTime'] = 0.0 if isHide else self.finishTime
        data['isInactivation'] = None if isHide else duration > 0
        data['isSourceVehicle'] = True
        super(VehicleSelfBuffComponent, self)._updateTimer(data)
        return

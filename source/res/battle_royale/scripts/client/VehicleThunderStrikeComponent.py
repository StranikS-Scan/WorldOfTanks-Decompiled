# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleThunderStrikeComponent.py
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent

class VehicleThunderStrikeComponent(VehicleAbilityBaseComponent):
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.THUNDER_STRIKE
    __MARKER_ID = BATTLE_MARKER_STATES.THUNDER_STRIKE_STATE

    def __init__(self):
        self.__id = id(self)
        super(VehicleThunderStrikeComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def _updateTimer(self, data):
        data['id'] = self.__id
        super(VehicleThunderStrikeComponent, self)._updateTimer(data)

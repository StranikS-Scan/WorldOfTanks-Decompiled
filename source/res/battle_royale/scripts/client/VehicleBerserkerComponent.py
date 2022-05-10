# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleBerserkerComponent.py
from collections import namedtuple
import BigWorld
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
BerserkerInfo = namedtuple('BerserkerInfo', ('endTime', 'tickInterval'))

class VehicleBerserkerComponent(BigWorld.DynamicScriptComponent):
    __EQUIPMENT_NAME = BattleRoyaleEquipments.BERSERKER

    def __init__(self, *args):
        super(VehicleBerserkerComponent, self).__init__()
        self.__updateState(BerserkerInfo(self.endTime, self.tickInterval))
        self.entity.guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData

    def set_endTime(self, prev):
        self.__updateState(BerserkerInfo(self.endTime, self.tickInterval))

    def onDestroy(self):
        self.entity.guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData
        self.__updateState(BerserkerInfo(0.0, 0.0))

    def __updateState(self, abilityInfo):
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.__EQUIPMENT_NAME, self.entity.id, abilityInfo)
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BERSERKER, abilityInfo)

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__updateState(BerserkerInfo(self.endTime, self.tickInterval))

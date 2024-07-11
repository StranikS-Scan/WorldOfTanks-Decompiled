# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/RacesVehicleLoot.py
import BigWorld
from races_common.races_constants import RacesAbilityMap
from constants import LootAction
from debug_utils import LOG_DEBUG_DEV, LOG_ERROR
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from items import vehicles

class RacesVehicleLoot(BigWorld.DynamicScriptComponent):

    def __invalidateState(self, action, lootTypeID, time):
        LOG_DEBUG_DEV('__invalidateState', lootTypeID, action, time)
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.LOOT, (lootTypeID, action, time))
        vehicle = self.entity
        lootData = self.lootData
        eqName = RacesAbilityMap[lootTypeID]
        cache = vehicles.g_cache
        equipmentID = cache.equipmentIDs().get(eqName)
        if equipmentID is None:
            LOG_ERROR('RacesVehicleLoot: equipment not found')
            return
        else:
            equipment = cache.equipments()[equipmentID]
            for index, data in enumerate(lootData):
                if lootTypeID == data['lootTypeID']:
                    quantity = data['quantity']
                    if quantity >= 1:
                        abilityComponent = vehicle.dynamicComponents.get(eqName)
                        if not abilityComponent:
                            continue
                        stage = abilityComponent.equipmentState['stage']
                        endTime = abilityComponent.equipmentState['endTime']
                        timeRemaining = max(endTime - BigWorld.serverTime(), 0.0)
                        totalTime = abilityComponent.equipmentState['totalTime']
                        LOG_DEBUG_DEV('__invalidateState custom', 'stage: ', stage, 'remainingTime: ', timeRemaining, 'totalTime: ', totalTime, 'quantity: ', quantity)
                        self.entity.guiSessionProvider.shared.equipments.setEquipment(equipment.compactDescr, quantity, stage, timeRemaining, totalTime)
                    break

            return

    def onDestroy(self):
        pass

    def setSlice_lootData(self, changePath, oldValue):
        if len(self.lootData) < len(oldValue):
            return
        startIndex, endIndex = changePath[-1]
        changes = self.lootData[startIndex:endIndex]
        for change in changes:
            self.__invalidateState(LootAction.PICKUP_SUCCEEDED, change['lootTypeID'], 0)

    def set_lootData(self, prev):
        for data in self.lootData:
            if prev['lootTypeID'] == data['lootTypeID']:
                if prev['quantity'] < data['quantity']:
                    self.__invalidateState(LootAction.PICKUP_SUCCEEDED, prev['lootTypeID'], 0)
                    return
                return

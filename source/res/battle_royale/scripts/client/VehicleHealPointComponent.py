# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleHealPointComponent.py
from collections import namedtuple
import BigWorld
from battle_royale.gui.constants import BattleRoyaleEquipments
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
HealPointInfo = namedtuple('HealPointInfo', 'endTime')

class VehicleHealPointComponent(BigWorld.DynamicScriptComponent):
    __dynamicObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)
    __EQUIPMENT_NAME = BattleRoyaleEquipments.HEAL_POINT

    def __init__(self, *args):
        super(VehicleHealPointComponent, self).__init__()
        self.__onUpdated()
        effectSettings = self.__getEffectSettings()
        if effectSettings is not None:
            self.entity.appearance.showTerrainCircle(self.radius, effectSettings)
        self.entity.guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData
        return

    def set_endTime(self, prev):
        self.__onUpdated()

    def onDestroy(self):
        self.__onUpdated(HealPointInfo(0.0))
        self.entity.appearance.hideTerrainCircle()
        self.entity.guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData

    def __onUpdated(self, info=None):
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.__EQUIPMENT_NAME, self.entity.id, info or HealPointInfo(self.endTime))

    def __getEffectSettings(self):
        dynamicObjects = self.__dynamicObjectsCache.getConfig(BigWorld.player().arenaGuiType)
        if dynamicObjects is None:
            return
        else:
            isAlly = self.entity.guiSessionProvider.getArenaDP().isAllyTeam(self.entity.publicInfo['team'])
            return dynamicObjects.getHealPointEffect().get('ally' if isAlly else 'enemy')

    def __onUpdateObservedVehicleData(self, vehicleID, *args):
        effectSettings = self.__getEffectSettings()
        if effectSettings is not None:
            self.entity.appearance.hideTerrainCircle()
            self.entity.appearance.showTerrainCircle(self.radius, effectSettings)
        return

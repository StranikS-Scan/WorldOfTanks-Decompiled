# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleHealPointComponent.py
from collections import namedtuple
import BigWorld
from battle_royale.gui.constants import BattleRoyaleEquipments
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from Event import EventsSubscriber
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
        self.__es = EventsSubscriber()
        gsp = self.entity.guiSessionProvider
        self.__es.subscribeToEvent(gsp.onUpdateObservedVehicleData, self.__onUpdateObservedVehicleData)
        self.__es.subscribeToEvent(gsp.dynamic.progression.onVehicleUpgradeFinished, self.__onVehicleUpgradeFinished)
        return

    def set_endTime(self, prev):
        self.__onUpdated()

    def onDestroy(self):
        self.__onUpdated(HealPointInfo(0.0))
        self.entity.appearance.hideTerrainCircle()
        self.__es.unsubscribeFromAllEvents()

    def onLeaveWorld(self, *args):
        self.__es.unsubscribeFromAllEvents()

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

    def __onVehicleUpgradeFinished(self, vehicleID):
        if self.entity.id != vehicleID:
            return
        else:
            effectSettings = self.__getEffectSettings()
            if effectSettings is not None:
                self.entity.appearance.hideTerrainCircle()
                self.entity.appearance.showTerrainCircle(self.radius, effectSettings)
            return

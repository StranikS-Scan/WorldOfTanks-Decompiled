# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleUnionStrength.py
import CGF
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from vehicle_systems.model_assembler import loadAppearancePrefab

class WTVehicleUnionStrength(DynamicScriptComponent):

    def __init__(self):
        super(WTVehicleUnionStrength, self).__init__()
        self.__prefabPath = None
        self.__prefabGO = None
        return

    def onDestroy(self):
        self.__removePrefab()
        super(WTVehicleUnionStrength, self).onDestroy()

    def set_isHealActive(self, prev):
        if prev != self.isHealActive:
            self.__updateVisualEffects()

    def _onAvatarReady(self):
        self.set_isHealActive(None)
        return

    def __updateVisualEffects(self):
        if self.isHealActive:
            self.__loadPrefab()
        else:
            self.__removePrefab()

    def __loadPrefab(self):
        if not self.__prefabPath:
            self.__prefabPath = self.__getPrefabPath()
        appearance = self.entity.appearance
        if appearance or appearance.isConstructed:
            loadAppearancePrefab(self.__prefabPath, appearance, self.__onPrefabLoaded)

    def __onPrefabLoaded(self, go):
        if not self.isHealActive:
            CGF.removeGameObject(go)
            return
        self.__prefabGO = go

    def __removePrefab(self):
        if self.__prefabGO and self.__prefabGO.isValid():
            CGF.removeGameObject(self.__prefabGO)
            self.__prefabGO = None
        return

    def __getPrefabPath(self):
        equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        vehicleName = self.entity.typeDescriptor.type.name
        return equipment.hunterEffects.get(vehicleName)

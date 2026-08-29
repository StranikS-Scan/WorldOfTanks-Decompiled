# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleGroupRepair.py
import CGF
import functools
import GenericComponents
import Math
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent

class WTVehicleGroupRepair(DynamicScriptComponent):

    def onActivate(self, duration):
        equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        CGF.loadGameObjectIntoHierarchy(equipment.usagePrefab, self.entity.entityGameObject, Math.Vector3(0, 0, 0), functools.partial(self.__onEffectLoaded, duration))

    def __onEffectLoaded(self, duration, go):
        go.createComponent(GenericComponents.RemoveGoDelayedComponent, duration)

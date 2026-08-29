# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/VehicleWTAbilitiesManagerComponent.py
from script_component.DynamicScriptComponent import DynamicScriptComponent
from Event import Event, EventManager

class VehicleWTAbilitiesManagerComponent(DynamicScriptComponent):

    def __init__(self):
        super(VehicleWTAbilitiesManagerComponent, self).__init__()
        self.__eventMgr = EventManager()
        self.onEquipmentCharged = Event(self.__eventMgr)
        self.onEquipmentLocked = Event(self.__eventMgr)

    def onDestroy(self):
        if self.__eventMgr is not None:
            self.__eventMgr.clear()
            self.__eventMgr = None
        super(VehicleWTAbilitiesManagerComponent, self).onDestroy()
        return

    def set_equipmentCDs(self, prev):
        pass

    def set_chargeEquipmentValues(self, prev):
        if self.chargeEquipmentValues != prev:
            self.onEquipmentCharged(self.chargeEquipmentValues)

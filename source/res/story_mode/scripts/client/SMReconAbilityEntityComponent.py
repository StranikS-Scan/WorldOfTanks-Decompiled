# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMReconAbilityEntityComponent.py
import typing
from Event import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent

class SMReconAbilityEntityComponent(DynamicScriptComponent):
    onSMReconEntityCreated = Event()
    onSMReconAbilitySpottedVehicles = Event()

    def __init__(self):
        super(SMReconAbilityEntityComponent, self).__init__()
        self.onSMReconEntityCreated(self.entity.id)

    def set_spottedVehiclesIDs(self, prevValues):
        if any((vehId not in set(prevValues) for vehId in self.spottedVehiclesIDs)):
            self.onSMReconAbilitySpottedVehicles(self.spottedVehiclesIDs)

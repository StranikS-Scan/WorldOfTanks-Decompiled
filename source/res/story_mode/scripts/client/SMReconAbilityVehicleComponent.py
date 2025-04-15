# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMReconAbilityVehicleComponent.py
import typing
from Event import Event
from gui.impl.gen import R
from script_component.DynamicScriptComponent import DynamicScriptComponent
from story_mode_common.story_mode_constants import RECON_ABILITY, EQUIPMENT_STAGES as STAGES
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.equipment_ctrl import _EquipmentItem

class SMReconAbilityVehicleComponent(DynamicScriptComponent):
    _EQUIPMENT_NAME = RECON_ABILITY
    onSMReconAbilityActivated = Event()

    def __init__(self):
        super(SMReconAbilityVehicleComponent, self).__init__()
        self.entity.guiSessionProvider.shared.equipments.onEquipmentUpdated += self._onEquipmentUpdated

    def onDestroy(self):
        super(SMReconAbilityVehicleComponent, self).onDestroy()
        self.entity.guiSessionProvider.shared.equipments.onEquipmentUpdated -= self._onEquipmentUpdated

    def _onEquipmentUpdated(self, _, item):
        itemDescriptor = item.getDescriptor()
        isReconAbility = itemDescriptor.name == self._EQUIPMENT_NAME
        if isReconAbility:
            if item.getStage() == STAGES.ACTIVATING:
                self.onSMReconAbilityActivated(True)
            if item.getStage() == STAGES.COOLDOWN and item.getPrevStage() == STAGES.DEACTIVATING:
                self.onSMReconAbilityActivated(False)
            equipmentInfo = {}
            if item.getStage() in (STAGES.ACTIVATING, STAGES.DEACTIVATING):
                res = R.strings.ingame_gui.abilities.recon
                equipmentInfo = {'totalTime': item.getTotalTime(),
                 'finishTime': 0,
                 'text': res.stopVehicle() if item.getStage() == STAGES.ACTIVATING else res.startVehicle()}
            self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self._EQUIPMENT_NAME, self.entity.id, equipmentInfo)

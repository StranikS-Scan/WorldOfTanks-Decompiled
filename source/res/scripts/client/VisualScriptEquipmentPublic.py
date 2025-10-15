# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VisualScriptEquipmentPublic.py
from constants import EQUIPMENT_STAGES as STAGES
from VisualScriptEquipment import VisualScriptEquipment
from helpers.fixed_dict import getVisualScriptEquipmentPublicState

class VisualScriptEquipmentPublic(VisualScriptEquipment):

    def _onAvatarReady(self):
        super(VisualScriptEquipmentPublic, self)._onAvatarReady()
        self.set_equipmentStatePublic()

    def set_equipmentStatePublic(self, _=None):
        if self._context is None:
            return
        else:
            if not self.entity.isMyVehicle:
                state = getVisualScriptEquipmentPublicState(self.equipmentStatePublic)
                getattr(self._context, STAGES.toString(state.stage))()
            return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehicleModifiersComponent.py
from __future__ import absolute_import
import BigWorld
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID

class HWVehicleModifiersComponent(DynamicScriptComponent):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _onAvatarReady(self):
        self.set_modifiers(self.modifiers)

    def set_modifiers(self, _):
        hwBattleGuiCtrl = self._guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)
        vehicleID = getattr(BigWorld.player(), 'playerVehicleID', None)
        isOwnVehicle = vehicleID == self.entity.id
        if hwBattleGuiCtrl and isOwnVehicle:
            hwBattleGuiCtrl.onUpdateVehicleModifiers(self.entity)
        return

    def calc(self, key, value, filter_=None, defaultFactor=1.0):
        modifier = self.modifiers.get((key, filter_))
        if not modifier:
            modifier = self.modifiers.get((key, None))
        if not modifier:
            return value
        else:
            value = value * (modifier['factor'] + defaultFactor) + modifier['amount']
            return max(min(value, modifier['maxLimit']), modifier['minLimit'])

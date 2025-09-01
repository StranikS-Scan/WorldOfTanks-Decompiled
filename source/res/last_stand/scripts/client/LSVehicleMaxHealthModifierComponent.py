# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSVehicleMaxHealthModifierComponent.py
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent

class LSVehicleMaxHealthModifierComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def set_maxHealth(self, _):
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.LS_MAX_HEALTH, self.entity.maxHealth, self.entity.id)
        self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HEALTH, self.entity.health, self.entity.id)

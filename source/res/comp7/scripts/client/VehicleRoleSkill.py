# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/VehicleRoleSkill.py
from helpers import fixed_dict
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehicleRoleSkill(DynamicScriptComponent):

    def set_roleEquipmentState(self, prev):
        if self._isAvatarReady:
            self.__updateRoleEquipmentState(prev)

    def _onAvatarReady(self):
        self.__updateRoleEquipmentState()

    def __updateRoleEquipmentState(self, previousState=None):
        from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
        ctx = {'state': fixed_dict.getRoleEquipmentState(self.roleEquipmentState),
         'previousState': fixed_dict.getRoleEquipmentState(previousState) if previousState is not None else None}
        g_eventBus.handleEvent(events.RoleSkillEvent(events.RoleSkillEvent.STATE_CHANGED, ctx), scope=EVENT_BUS_SCOPE.BATTLE)
        return

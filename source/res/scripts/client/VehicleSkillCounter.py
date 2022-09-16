# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleSkillCounter.py
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehicleSkillCounter(DynamicScriptComponent):

    def set_counterValue(self, prev):
        if self._isAvatarReady:
            self.__updateCounter()

    def _onAvatarReady(self):
        self.__updateCounter()

    def __updateCounter(self):
        from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(events.RoleSkillEvent(events.RoleSkillEvent.COUNTER_CHANGED, {'value': self.counterValue}), scope=EVENT_BUS_SCOPE.BATTLE)

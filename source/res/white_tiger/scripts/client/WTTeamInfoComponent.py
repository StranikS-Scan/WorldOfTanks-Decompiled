# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTTeamInfoComponent.py
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import HasCtxEvent
from script_component.DynamicScriptComponent import DynamicScriptComponent

class WTCloneInfoEvent(HasCtxEvent):
    CLONE_VEHICLE_INFOS_UPDATED = 'wt/cloneVehicleIDsUpdated'


class WTTeamInfoComponent(DynamicScriptComponent):

    def set_cloneVehicleInfos(self, prev):
        g_eventBus.handleEvent(WTCloneInfoEvent(WTCloneInfoEvent.CLONE_VEHICLE_INFOS_UPDATED, ctx={'cloneVehicleInfo': self.cloneVehicleInfos}), scope=EVENT_BUS_SCOPE.BATTLE)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehicleRoleComponent.py
import BigWorld
import Event
from helpers import dependency
from historical_battles_common.hb_constants import VehicleRole
from skeletons.gui.battle_session import IBattleSessionProvider

class HBVehicleRoleComponent(BigWorld.DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    onRoleUpdated = Event.Event()

    def __init__(self):
        super(HBVehicleRoleComponent, self).__init__()
        self._vehicleRole = VehicleRole(self.role)
        self.onRoleUpdated(self)

    def set_unlockPercent(self, prev):
        from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
        g_eventBus.handleEvent(events.HBRoleSkillEvents(events.HBRoleSkillEvents.UNLOCK_PROGRESS_CHANGED, {'value': self.unlockPercent / 100.0,
         'roleAbilityId': self.roleAbilityId}), scope=EVENT_BUS_SCOPE.BATTLE)

    @property
    def vehicleRole(self):
        return self._vehicleRole

    def getRoleIconName(self):
        vehInfo = self._sessionProvider.getArenaDP().getVehicleInfo(self.entity.id)
        return self.vehicleRole.name if self.vehicleRole.hasUniqueIcon() else '{}_{}'.format(vehInfo.vehicleType.classTag, self.vehicleRole.name)

    def set_role(self, prev):
        self._vehicleRole = VehicleRole(self.role)
        self.onRoleUpdated(self)

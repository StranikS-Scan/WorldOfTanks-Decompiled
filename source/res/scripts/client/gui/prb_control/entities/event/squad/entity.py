# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.shared.gui_items.Vehicle import VEHICLE_FOOTBALL_ROLES

class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()


class EventBattleSquadEntity(SquadEntity):

    def __init__(self):
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(EventBattleSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self.invalidateVehicleStates()

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(EventBattleSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self.invalidateVehicleStates()

    def getQueueType(self):
        return QUEUE_TYPE.EVENT_BATTLES

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.SQUAD, PREBATTLE_ACTION_NAME.RANDOM):
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(EventBattleSquadEntity, self).doSelectAction(action)

    def hasSlotForRole(self, role):
        _, unit = self.getUnit()
        unitVehicles = unit.getVehicles()
        for _, vInfos in unitVehicles.iteritems():
            for vInfo in vInfos:
                vehicle = self.itemsCache.items.getItemByCD(vInfo.vehTypeCompDescr)
                if vehicle.getFootballRole() == role:
                    return False

        return True

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)

    def _vehicleStateCondition(self, v):
        if not v.isFootball:
            return False
        availableRoles = [ role for role in VEHICLE_FOOTBALL_ROLES if self.hasSlotForRole(role) ]
        return False if v.getFootballRole() not in availableRoles else super(EventBattleSquadEntity, self)._vehicleStateCondition(v)

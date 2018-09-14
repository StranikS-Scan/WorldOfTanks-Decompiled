# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/squad/entity.py
import account_helpers
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL, PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.items import SelectResult
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from .actions_handler import BalancedSquadActionsHandler, RandomSquadActionsHandler
from .actions_validator import BalancedSquadActionsValidator, RandomSquadActionsValidator

class BalancedSquadDynamicRosterSettings(DynamicRosterSettings):
    """
    Dynamic roster settings for balanced squad
    """

    def __init__(self, unit, lowerBound=0, upperBound=0):
        self._lowerBound = lowerBound
        self._upperBound = upperBound
        super(BalancedSquadDynamicRosterSettings, self).__init__(unit)

    def _extractSettings(self, unit):
        kwargs = super(BalancedSquadDynamicRosterSettings, self)._extractSettings(unit)
        accountDbID = account_helpers.getAccountDatabaseID()
        if kwargs and unit.getCommanderDBID() != accountDbID:
            vehicles = unit.getMemberVehicles(unit.getCommanderDBID())
            if not vehicles:
                unitVehicles = unit.getVehicles()
                for accDbID, vInfos in unitVehicles.iteritems():
                    if accDbID != accountDbID:
                        vehicles.extend(vInfos)

            minLevel, maxLevel = self._getVehicleLevels(vehicles)
            kwargs['minLevel'] = minLevel
            kwargs['maxLevel'] = maxLevel
        return kwargs

    def _getVehicleLevels(self, vehicles):
        if vehicles:
            levels = set([ vehInfo.vehLevel for vehInfo in vehicles ])
            minLevel = max(MIN_VEHICLE_LEVEL, min(levels) + self._lowerBound)
            maxLevel = min(MAX_VEHICLE_LEVEL, max(levels) + self._upperBound)
        else:
            minLevel = MIN_VEHICLE_LEVEL
            maxLevel = MAX_VEHICLE_LEVEL
        return (minLevel, maxLevel)


class RandomSquadEntryPoint(SquadEntryPoint):
    """
    Random squad entry point
    """

    def __init__(self, accountsToInvite=None):
        super(RandomSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANDOM, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquad()


class RandomSquadEntity(SquadEntity):
    """
    Random squad entity class
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        super(RandomSquadEntity, self).__init__(FUNCTIONAL_FLAG.RANDOM, PREBATTLE_TYPE.SQUAD)

    def init(self, ctx=None):
        rv = super(RandomSquadEntity, self).init(ctx)
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.eventsCache.onSyncCompleted += self._onEventsSyncCompleted
        if self._isBalancedSquad:
            g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        return rv

    def fini(self, ctx=None, woEvents=False):
        self.eventsCache.onSyncCompleted -= self._onEventsSyncCompleted
        if self._isBalancedSquad:
            g_clientUpdateManager.removeObjectCallbacks(self, force=True)
            self._isBalancedSquad = False
            self.invalidateVehicleStates()
        return super(RandomSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getQueueType(self):
        return QUEUE_TYPE.RANDOMS

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        if name == PREBATTLE_ACTION_NAME.RANDOM:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(RandomSquadEntity, self).doSelectAction(action)

    def isBalancedSquadEnabled(self):
        """
        Is balanced squad enabled on server side
        """
        return self.eventsCache.isBalancedSquadEnabled()

    def getSquadLevelBounds(self):
        """
        Get balanced squad levels bounds
        """
        return self.eventsCache.getBalancedSquadBounds()

    def _createRosterSettings(self):
        if self._isBalancedSquad:
            _, unit = self.getUnit()
            lowerBound, upperBound = self.getSquadLevelBounds()
            return BalancedSquadDynamicRosterSettings(unit=unit, lowerBound=lowerBound, upperBound=upperBound)
        return super(RandomSquadEntity, self)._createRosterSettings()

    def _createActionsHandler(self):
        return BalancedSquadActionsHandler(self) if self.isBalancedSquadEnabled() else RandomSquadActionsHandler(self)

    def _createActionsValidator(self):
        return BalancedSquadActionsValidator(self) if self.isBalancedSquadEnabled() else RandomSquadActionsValidator(self)

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(RandomSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(RandomSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(RandomSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if self._isBalancedSquad and playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(RandomSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if self._isBalancedSquad and playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def _vehicleStateCondition(self, v):
        return v.level in self._rosterSettings.getLevelsRange() if self._isBalancedSquad else super(RandomSquadEntity, self)._vehicleStateCondition(v)

    def _onEventsSyncCompleted(self):
        """
        Listener for events cache update
        """
        enabled = self.isBalancedSquadEnabled()
        if enabled != self._isBalancedSquad:
            if enabled:
                g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
            else:
                g_clientUpdateManager.removeObjectCallbacks(self, force=True)
            self._isBalancedSquad = enabled
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onInventoryVehiclesUpdated(self, diff):
        """
        Listener for inventory vehicles update
        """
        self.invalidateVehicleStates()

    def _onUnitMemberVehiclesChanged(self, accoundDbID):
        """
        Routine that holds additional logic related to vehicles list change
        for player
        """
        if self._isBalancedSquad and accoundDbID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

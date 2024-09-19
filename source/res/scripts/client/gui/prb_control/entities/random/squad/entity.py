# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/squad/entity.py
import account_helpers
from constants import MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL, PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.base.squad.components import RestrictedSquadDataProvider
from gui.prb_control.entities.base.squad.mixins import RestrictedRoleTagMixin
from gui.prb_control.entities.random.squad.actions_handler import RandomSquadActionsHandler, BalancedSquadActionsHandler
from gui.prb_control.entities.random.squad.actions_validator import VehTypeForbiddenSquadActionsValidator, VehTypeForbiddenBalancedSquadActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class BalancedSquadDynamicRosterSettings(DynamicRosterSettings):

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

    def __init__(self, accountsToInvite=None):
        super(RandomSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANDOM, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquad()


class RandomSquadEntity(SquadEntity, RestrictedRoleTagMixin):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._isBalancedSquad = False
        self.__restrictedSquadRestrictedDataProvider = RestrictedSquadDataProvider()
        self._mmData = 0
        self.__watcher = None
        super(RandomSquadEntity, self).__init__(FUNCTIONAL_FLAG.RANDOM, PREBATTLE_TYPE.SQUAD)
        return

    def init(self, ctx=None):
        self.initRestrictedRoleDataProvider(self)
        self.__restrictedSquadRestrictedDataProvider.init(self)
        rv = super(RandomSquadEntity, self).init(ctx)
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.invalidateVehicleStates()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = BaseVehiclesWatcher()
        self.__watcher.start()
        return rv

    def fini(self, ctx=None, woEvents=False):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self._isBalancedSquad = False
        self._isUseSquadRestrictedValidateRule = False
        self.invalidateVehicleStates()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.finiRestrictedRoleDataProvider()
        self.__restrictedSquadRestrictedDataProvider.fini()
        return super(RandomSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getQueueType(self):
        return QUEUE_TYPE.RANDOMS

    def doAction(self, action=None):
        self._mmData = 0 if action is None else action.mmData
        super(RandomSquadEntity, self).doAction(action)
        return

    def doBattleQueue(self, ctx, callback=None):
        ctx.mmData = self._mmData
        self._mmData = 0
        super(RandomSquadEntity, self).doBattleQueue(ctx, callback)

    def isBalancedSquadEnabled(self):
        return self.eventsCache.isBalancedSquadEnabled()

    def getSquadLevelBounds(self):
        return self.eventsCache.getBalancedSquadBounds()

    @property
    def squadRestrictions(self):
        return self.lobbyContext.getServerSettings().getSquadRestrictions()

    def hasSlotForSquadRestricted(self):
        return self.__restrictedSquadRestrictedDataProvider.hasSlotForVehicle('')

    def getMaxSquadRestrictedCount(self):
        return self.__restrictedSquadRestrictedDataProvider.getMaxPossibleVehicles(None)

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

    def _createRosterSettings(self):
        if self._isBalancedSquad:
            _, unit = self.getUnit(safe=True)
            lowerBound, upperBound = self.getSquadLevelBounds()
            return BalancedSquadDynamicRosterSettings(unit=unit, lowerBound=lowerBound, upperBound=upperBound)
        return super(RandomSquadEntity, self)._createRosterSettings()

    def _createActionsHandler(self):
        return BalancedSquadActionsHandler(self) if self.isBalancedSquadEnabled() else RandomSquadActionsHandler(self)

    def _createActionsValidator(self):
        return VehTypeForbiddenBalancedSquadActionsValidator(self) if self.isBalancedSquadEnabled() else VehTypeForbiddenSquadActionsValidator(self)

    def _vehicleStateCondition(self, v):
        if self._isBalancedSquad:
            if v.level not in self._rosterSettings.getLevelsRange():
                return False
        if self.isRoleRestrictionValid():
            return self.isTagVehicleAvailable(v.tags)
        return self.__restrictedSquadRestrictedDataProvider.isTagVehicleAvailable(v.tags) if self._isUseSquadRestrictedValidateRule and v.isSquadRestricted else super(RandomSquadEntity, self)._vehicleStateCondition(v)

    def _onServerSettingChanged(self, *args, **kwargs):
        balancedEnabled = self.isBalancedSquadEnabled()
        self.invalidateVehicleStates()
        self._isBalancedSquad = balancedEnabled
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def _onUnitMemberVehiclesChanged(self, accountDBID):
        self.invalidateVehicleStates()
        if self._isBalancedSquad and accountDBID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/prb_control/entities/squad/entity.py
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.base.squad.components import RestrictedSPGDataProvider, RestrictedScoutDataProvider
from gui.prb_control.entities.random.squad.entity import BalancedSquadDynamicRosterSettings
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from versus_ai.gui.versus_ai_gui_constants import FUNCTIONAL_FLAG
from versus_ai.gui.prb_control.entities.pre_queue.vehicles_watcher import VersusAIVehiclesWatcher
from versus_ai.gui.prb_control.entities.squad.actions_validator import VersusAISquadActionsValidator

class VersusAISquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(VersusAISquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.VERSUS_AI, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquadByPrbType(PREBATTLE_TYPE.VERSUS_AI)


class VersusAISquadEntity(SquadEntity):
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._isBalancedSquad = False
        self.__restrictedSPGDataProvider = RestrictedSPGDataProvider()
        self.__restrictedScoutDataProvider = RestrictedScoutDataProvider()
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.VERSUS_AI)()
        super(VersusAISquadEntity, self).__init__(FUNCTIONAL_FLAG.VERSUS_AI, PREBATTLE_TYPE.VERSUS_AI)
        return

    def setReserve(self, ctx, callback=None):
        pass

    def init(self, ctx=None):
        self.__restrictedSPGDataProvider.init(self)
        self.__restrictedScoutDataProvider.init(self)
        self.storage.release()
        versusAISquadEntity = super(VersusAISquadEntity, self).init(ctx)
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__eventsCache.onSyncCompleted += self.__onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onInventoryVehiclesUpdated})
        self.__watcher = VersusAIVehiclesWatcher()
        self.__watcher.start()
        self.invalidateVehicleStates()
        return versusAISquadEntity

    def fini(self, ctx=None, woEvents=False):
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__eventsCache.onSyncCompleted -= self.__onServerSettingChanged
        self._isBalancedSquad = False
        self.invalidateVehicleStates()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.__restrictedSPGDataProvider.fini()
        self.__restrictedScoutDataProvider.fini()
        return super(VersusAISquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(VersusAISquadEntity, self).leave(ctx, callback)

    def isBalancedSquadEnabled(self):
        return self.__eventsCache.isBalancedSquadEnabled()

    def getMaxSPGCount(self):
        return self.__restrictedSPGDataProvider.getMaxPossibleVehicles()

    def getCurrentSPGCount(self):
        return self.__restrictedSPGDataProvider.getCurrentVehiclesCount()

    def hasSlotForSPG(self):
        return self.__restrictedSPGDataProvider.hasSlotForVehicle()

    def hasSlotForScout(self):
        return self.__restrictedScoutDataProvider.hasSlotForVehicle()

    def getMaxScoutCount(self):
        return self.__restrictedScoutDataProvider.getMaxPossibleVehicles()

    def getCurrentScoutCount(self):
        return self.__restrictedScoutDataProvider.getCurrentVehiclesCount()

    def getMaxScoutLevels(self):
        return self.__restrictedScoutDataProvider.getRestrictionLevels()

    def getSquadLevelBounds(self):
        return self.__eventsCache.getBalancedSquadBounds()

    def _createActionsValidator(self):
        return VersusAISquadActionsValidator(self)

    def getQueueType(self):
        return QUEUE_TYPE.VERSUS_AI

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(VersusAISquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self.__onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(VersusAISquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self.__onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(VersusAISquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if self._isBalancedSquad and playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(VersusAISquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if self._isBalancedSquad and playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def __onServerSettingChanged(self, *args, **kwargs):
        self.invalidateVehicleStates()
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def __onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def __onUnitMemberVehiclesChanged(self, accoundDbID):
        self.invalidateVehicleStates()
        if self._isBalancedSquad and accoundDbID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def _vehicleStateCondition(self, v):
        if self._isBalancedSquad:
            if v.level not in self._rosterSettings.getLevelsRange():
                return False
        if v.type == VEHICLE_CLASS_NAME.SPG:
            return self.__restrictedSPGDataProvider.isTagVehicleAvailable()
        return self.__restrictedScoutDataProvider.isTagVehicleAvailable() if v.isScout and v.level in self.getMaxScoutLevels() else super(VersusAISquadEntity, self)._vehicleStateCondition(v)

    def _createRosterSettings(self):
        if self._isBalancedSquad:
            _, unit = self.getUnit(safe=True)
            lowerBound, upperBound = self.getSquadLevelBounds()
            return BalancedSquadDynamicRosterSettings(unit=unit, lowerBound=lowerBound, upperBound=upperBound)
        return super(VersusAISquadEntity, self)._createRosterSettings()

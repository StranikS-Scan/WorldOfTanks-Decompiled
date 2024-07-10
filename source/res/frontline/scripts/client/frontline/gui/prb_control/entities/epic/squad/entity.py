# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/prb_control/entities/epic/squad/entity.py
from frontline.gui.prb_control.entities.epic.pre_queue.vehicles_watcher import EpicVehiclesWatcher
from frontline.gui.prb_control.entities.epic.squad.actions_validator import EpicSquadActionsValidator
from frontline.gui.prb_control.entities.epic.squad.components import EpicRestrictedRoleTagDataProvider
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.base.squad.mixins import RestrictedRoleTagMixin
from gui.prb_control.entities.random.squad.actions_handler import BalancedSquadActionsHandler
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class EpicSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EpicSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EPIC, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.EPIC, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEpicSquad()


class EpicSquadEntity(SquadEntity, RestrictedRoleTagMixin):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._isBalancedSquad = False
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.EPIC)()
        super(EpicSquadEntity, self).__init__(FUNCTIONAL_FLAG.EPIC, PREBATTLE_TYPE.EPIC)
        return

    def init(self, ctx=None):
        self.initRestrictedRoleDataProvider(self)
        self.storage.release()
        epicSquadEntity = super(EpicSquadEntity, self).init(ctx)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = EpicVehiclesWatcher()
        self.__watcher.start()
        return epicSquadEntity

    def fini(self, ctx=None, woEvents=False):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.invalidateVehicleStates()
        self.finiRestrictedRoleDataProvider()
        return super(EpicSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(EpicSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.EPIC

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.SQUAD,)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(EpicSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(EpicSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(EpicSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(EpicSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    @property
    def squadRestrictions(self):
        return self.lobbyContext.getServerSettings().epicBattles.squadRestrictions

    @classmethod
    def _createRestrictedRoleTagDataProvider(cls):
        return EpicRestrictedRoleTagDataProvider()

    def _createActionsHandler(self):
        return BalancedSquadActionsHandler(self)

    def _createActionsValidator(self):
        return EpicSquadActionsValidator(self)

    def _vehicleStateCondition(self, v):
        return self.isTagVehicleAvailable(v.tags) if self.isRoleRestrictionValid() else super(EpicSquadEntity, self)._vehicleStateCondition(v)

    def _onServerSettingChanged(self, *args, **kwargs):
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def _onUnitMemberVehiclesChanged(self, accountDBID):
        self.invalidateVehicleStates()
        if accountDBID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

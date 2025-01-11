# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prb_control/entities/squad/entity.py
import account_helpers
from grinch.gui.prb_control.entities.squad.actions_validator import GrinchSquadActionsValidator
from grinch.gui.prb_control.entities.squad.vehicles_watcher import GrinchVehiclesWatcher
from grinch.gui.prb_control.entities.squad.scheduler import GrinchSquadScheduler
from grinch.overrides.hangar_override import showHangar
from grinch.skeletons.battle_controller import IGrinchController
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.base.squad.mixins import RestrictedRoleTagMixin
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from grinch.gui.grinch_gui_constants import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, SELECTOR_BATTLE_TYPES
from grinch_common.grinch_constants import PREBATTLE_TYPE, QUEUE_TYPE

class GrinchSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(GrinchSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.GRINCH, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquadByQueueType(QUEUE_TYPE.GRINCH)


class GrinchSquadEntity(SquadEntity, RestrictedRoleTagMixin):
    grinchCtrl = dependency.descriptor(IGrinchController)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(GrinchSquadEntity, self).__init__(FUNCTIONAL_FLAG.GRINCH, PREBATTLE_TYPE.GRINCH)
        self._mmData = 0
        self.__watcher = None
        return

    @property
    def squadRestrictions(self):
        return self.grinchCtrl.getSquadConfig()

    def setReserve(self, ctx, callback=None):
        pass

    def loadHangar(self):
        showHangar()

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.initRestrictedRoleDataProvider(self)
        rv = super(GrinchSquadEntity, self).init(ctx)
        self.storage.queueType = self.getQueueType()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.invalidateVehicleStates()
        if not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.GRINCH):
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.GRINCH)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = GrinchVehiclesWatcher()
        self.__watcher.start()
        return rv

    def fini(self, ctx=None, woEvents=False):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.invalidateVehicleStates()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        self.finiRestrictedRoleDataProvider()
        return super(GrinchSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getConfirmDialogMeta(self, ctx):
        return None if not self.grinchCtrl.isEnabled() else super(GrinchSquadEntity, self).getConfirmDialogMeta(ctx)

    def getQueueType(self):
        return QUEUE_TYPE.GRINCH

    def doSelectAction(self, action):
        name = action.actionName
        if name == (PREBATTLE_ACTION_NAME.GRINCH, PREBATTLE_ACTION_NAME.GRINCH_SQUAD):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(GrinchSquadEntity, self).doSelectAction(action)

    def doAction(self, action=None):
        self._mmData = 0 if action is None else action.mmData
        super(GrinchSquadEntity, self).doAction(action)
        return

    def doBattleQueue(self, ctx, callback=None):
        ctx.mmData = self._mmData
        self._mmData = 0
        super(GrinchSquadEntity, self).doBattleQueue(ctx, callback)

    def canInvite(self, prbType):
        return self.grinchCtrl.isAvailable()

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(GrinchSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(GrinchSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(GrinchSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(GrinchSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def _onServerSettingChanged(self, *args, **kwargs):
        self.invalidateVehicleStates()
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def _onUnitMemberVehiclesChanged(self, accoundDbID):
        self.invalidateVehicleStates()
        if accoundDbID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def _createActionsValidator(self):
        return GrinchSquadActionsValidator(self)

    def _createScheduler(self):
        return GrinchSquadScheduler(self)

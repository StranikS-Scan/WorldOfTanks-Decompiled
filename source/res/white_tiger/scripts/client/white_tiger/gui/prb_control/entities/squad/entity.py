# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/entity.py
import account_helpers
from white_tiger.gui.prb_control.entities.squad.actions_validator import WhiteTigerSquadActionsValidator
from white_tiger.gui.prb_control.entities.squad.scheduler import WhiteTigerSquadScheduler
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
from white_tiger.gui.prb_control.entities.vehicles_watcher import WhiteTigerVehiclesWatcher
from white_tiger.gui.prb_control.entities.vehicle_switcher import WhiteTigerVehicleSwitcher
from white_tiger.gui.white_tiger_gui_constants import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, SELECTOR_BATTLE_TYPES
from white_tiger_common.wt_constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.impl.gen import R
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from frameworks.wulf import WindowLayer
from wg_async import wg_await, wg_async
from gui.impl.pub.dialog_window import DialogButtons

class WhiteTigerSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(WhiteTigerSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquadByQueueType(QUEUE_TYPE.WHITE_TIGER)


class WhiteTigerSquadEntity(SquadEntity, RestrictedRoleTagMixin, WhiteTigerVehicleSwitcher):
    wtCtrl = dependency.descriptor(IWhiteTigerController)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(WhiteTigerSquadEntity, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, PREBATTLE_TYPE.WHITE_TIGER)
        self._mmData = 0
        self.__watcher = None
        return

    @property
    def squadRestrictions(self):
        return self.wtCtrl.getSquadConfig()

    def setReserve(self, ctx, callback=None):
        pass

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.initRestrictedRoleDataProvider(self)
        rv = super(WhiteTigerSquadEntity, self).init(ctx)
        self.storage.queueType = self.getQueueType()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.invalidateVehicleStates()
        self.startSwitcher()
        if not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.WHITE_TIGER):
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.WHITE_TIGER)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = WhiteTigerVehiclesWatcher()
        self.__watcher.start()
        return rv

    def fini(self, ctx=None, woEvents=False):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.invalidateVehicleStates()
        self.stopSwitcher()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        self.finiRestrictedRoleDataProvider()
        return super(WhiteTigerSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getConfirmDialogMeta(self, ctx):
        return None if not self.wtCtrl.isEnabled() else self.__createUnitLeaveMeta(ctx, self.canSwitch(ctx))

    def showDialog(self, builder, callback, parent=None):
        self.__showBuilderDialog(builder, callback)

    def getQueueType(self):
        return QUEUE_TYPE.WHITE_TIGER

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            squadEntryPoint = WhiteTigerSquadEntryPoint(action.accountsToInvite)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True, squadEntryPoint)
        else:
            return SelectResult(True, None) if name == PREBATTLE_ACTION_NAME.WHITE_TIGER else super(WhiteTigerSquadEntity, self).doSelectAction(action)

    def doAction(self, action=None):
        self._mmData = 0 if action is None else action.mmData
        super(WhiteTigerSquadEntity, self).doAction(action)
        return

    def doBattleQueue(self, ctx, callback=None):
        ctx.mmData = self._mmData
        self._mmData = 0
        super(WhiteTigerSquadEntity, self).doBattleQueue(ctx, callback)

    def canInvite(self, prbType):
        return self.wtCtrl.isAvailable()

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(WhiteTigerSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(WhiteTigerSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(WhiteTigerSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(WhiteTigerSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.WHITE_TIGER, PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD)

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
        return WhiteTigerSquadActionsValidator(self)

    def _createScheduler(self):
        return WhiteTigerSquadScheduler(self)

    def __createUnitLeaveMeta(self, unlockCtx, isSwitching=False):
        isWTEntityCtx = unlockCtx.getEntityType() == PREBATTLE_TYPE.WHITE_TIGER
        return self.__getLeaveSquadBuilder(R.strings.dialogs.squad.leave) if (unlockCtx.hasFlags(FUNCTIONAL_FLAG.SWITCH) or isSwitching) and not isWTEntityCtx or unlockCtx.hasFlags(FUNCTIONAL_FLAG.EXIT) and isWTEntityCtx else self.__getLeaveSquadBuilder(R.strings.dialogs.squad.goToAnother)

    def __getLeaveSquadBuilder(self, key):
        builder = ResDialogBuilder()
        builder.setMessagesAndButtons(key, buttons=key)
        builder.setLayer(WindowLayer.OVERLAY)
        builder.setIcon(R.images.white_tiger.gui.maps.icons.progression.widget.full_main_wt(), backgrounds=[R.images.gui.maps.uiKit.dialogs.highlights.green()])
        return builder

    @wg_async
    def __showBuilderDialog(self, builder, callback):
        from gui.impl.dialogs import dialogs
        result = yield wg_await(dialogs.show(builder.build()))
        if callback is not None:
            callback(result.result == DialogButtons.SUBMIT)
        return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
import account_helpers
from wg_async import wg_await, wg_async
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from constants import PREBATTLE_TYPE, QUEUE_TYPE, VEHICLE_CLASS_INDICES
from gui.prb_control.entities.event.pre_queue.vehicles_watcher import EventBattleVehiclesWatcher
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator, EventBattleBalanceSquadActionsValidator
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler, EventBattleBalancedSquadActionsHandler
from gui.prb_control.entities.random.squad.entity import BalancedSquadDynamicRosterSettings
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.shared.utils.decorators import ReprInjector
from gui.prb_control import settings as prb_settings
from gui.prb_control.entities.event.squad.scheduler import EventSquadScheduler
from gui.prb_control.storages import RECENT_ARENA_STORAGE, storage_getter
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.impl.dialogs.gf_builders import ResDialogBuilder
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.gen import R

@ReprInjector.withParent()
class EventSquadSettingsCtx(SquadSettingsCtx):
    __slots__ = ('_keepCurrentView',)

    def __init__(self, waitingID='', accountsToInvite=None, keepCurrentView=False):
        super(EventSquadSettingsCtx, self).__init__(PREBATTLE_TYPE.EVENT, waitingID, prb_settings.FUNCTIONAL_FLAG.UNDEFINED, accountsToInvite, False)
        self._keepCurrentView = keepCurrentView

    def getKeepCurrentView(self):
        return self._keepCurrentView


class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT | FUNCTIONAL_FLAG.LOAD_PAGE, accountsToInvite)
        self._keepCurrentView = False

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()

    def setKeepCurrentView(self, keepCurrentView):
        self._keepCurrentView = keepCurrentView

    def makeDefCtx(self):
        return EventSquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=self._accountsToInvite, keepCurrentView=self._keepCurrentView)


class EventBattleSquadEntity(SquadEntity):
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._isBalancedSquad = False
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)
        self._isUseSPGValidateRule = True
        self._maxSpgCount = False
        self.__watcher = None
        return

    @property
    def getCurrentQueueType(self):
        return self.__eventBattlesCtrl.getCurrentQueueType()

    @storage_getter(RECENT_ARENA_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        rv = super(EventBattleSquadEntity, self).init(ctx)
        self.storage.queueType = self.getCurrentQueueType
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        self._maxSpgCount = self.getMaxSPGCount()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.invalidateVehicleStates()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = EventBattleVehiclesWatcher()
        self.__watcher.start()
        self.__eventBattlesCtrl.updateAccountSettings()
        if ctx is not None:
            initCtx = ctx.getInitCtx()
            fromEventSquad = isinstance(initCtx, EventSquadSettingsCtx)
            if not fromEventSquad or not initCtx.getKeepCurrentView():
                if self.getPlayerInfo().isReady and self.getFlags().isInQueue():
                    g_eventDispatcher.loadBattleQueue()
                else:
                    g_eventDispatcher.loadHangar()
        return rv

    def fini(self, ctx=None, woEvents=False):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self._isBalancedSquad = False
        self._isUseSPGValidateRule = False
        self.invalidateVehicleStates()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(EventBattleSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        super(EventBattleSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return self.getCurrentQueueType

    def isBalancedSquadEnabled(self):
        return self.eventsCache.isBalancedSquadEnabled()

    def getSquadLevelBounds(self):
        return self.eventsCache.getBalancedSquadBounds(tags='halloween')

    def hasSlotForSPG(self):
        accountDbID = account_helpers.getAccountDatabaseID()
        return self.getMaxSPGCount() > 0 and (self.getCurrentSPGCount() < self.getMaxSPGCount() or self.isCommander(accountDbID))

    def getCurrentSPGCount(self):
        enableSPGCount = 0
        _, unit = self.getUnit(safe=True)
        if unit is None:
            return enableSPGCount
        else:
            unitVehicles = unit.getVehicles()
            for _, vInfos in unitVehicles.iteritems():
                for vInfo in vInfos:
                    if vInfo.vehClassIdx == VEHICLE_CLASS_INDICES['SPG']:
                        enableSPGCount += 1

            return enableSPGCount

    def getMaxSPGCount(self):
        return self.lobbyContext.getServerSettings().getMaxSPGinSquads()

    def getCommanderQueueType(self):
        _, unit = self.getUnit(safe=True)
        if not unit:
            return None
        else:
            players = unit.getPlayers()
            playersVehicles = unit.getVehicles()
            for dbID in players.iterkeys():
                if not self.isCommander(dbID):
                    continue
                if dbID not in playersVehicles:
                    return None
                commanderVehs = playersVehicles[dbID]
                if not commanderVehs:
                    return None
                vehType = vehicles.getVehicleType(commanderVehs[0].vehTypeCompDescr)
                if vehType.isWheeledVehicle:
                    return QUEUE_TYPE.EVENT_BATTLES_2
                return QUEUE_TYPE.EVENT_BATTLES

            return None

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(EventBattleSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehls):
        super(EventBattleSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehls)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(EventBattleSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if self._isBalancedSquad and playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(EventBattleSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if self._isBalancedSquad and playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def _createRosterSettings(self):
        if self._isBalancedSquad:
            _, unit = self.getUnit(safe=True)
            lowerBound, upperBound = self.getSquadLevelBounds()
            return BalancedSquadDynamicRosterSettings(unit=unit, lowerBound=lowerBound, upperBound=upperBound)
        return super(EventBattleSquadEntity, self)._createRosterSettings()

    def getConfirmDialogMeta(self, ctx):
        progressCtrl = self.__eventBattlesCtrl.getHWProgressCtrl()
        if not self.__eventBattlesCtrl.isEnabled() or not progressCtrl or progressCtrl.isPostPhase():
            builder = self.__getLeaveSquadBuilder(R.strings.hw_dialogs.squad.leave.disabledEvent)
            self.__showBuilderDialog(builder, None)
            return
        elif self.hasLockedState():
            return self.__getLeaveSquadBuilder(R.strings.hw_dialogs.squad.leaveDisabled)
        else:
            return None if self.isCommander() and len(self.getPlayers()) == 1 else self.createUnitLeaveMeta(ctx, self.canSwitch(ctx))

    def createUnitLeaveMeta(self, unlockCtx, isSwitching=False):
        isEventEntityCtx = unlockCtx.getEntityType() == PREBATTLE_TYPE.EVENT
        return self.__getLeaveSquadBuilder(R.strings.hw_dialogs.squad.leave) if (unlockCtx.hasFlags(FUNCTIONAL_FLAG.SWITCH) or isSwitching) and not isEventEntityCtx or unlockCtx.hasFlags(FUNCTIONAL_FLAG.EXIT) and isEventEntityCtx else self.__getLeaveSquadBuilder(R.strings.hw_dialogs.squad.goToAnother)

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.EVENT_SQUAD, PREBATTLE_ACTION_NAME.EVENT_BATTLE)

    def showDialog(self, builder, callback):
        self.__showBuilderDialog(builder, callback)

    @wg_async
    def __showBuilderDialog(self, builder, callback):
        from gui.impl.dialogs import dialogs
        result = yield wg_await(dialogs.show(builder.build()))
        if callback is not None:
            callback(result.result == DialogButtons.SUBMIT)
        return

    def __getLeaveSquadBuilder(self, key):
        builder = ResDialogBuilder()
        builder.setMessagesAndButtons(key, buttons=key)
        builder.setIcon(R.images.halloween.gui.maps.icons.platoon.logo_180(), backgrounds=[R.images.gui.maps.uiKit.dialogs.highlights.green()])
        return builder

    def _createActionsValidator(self):
        return EventBattleBalanceSquadActionsValidator(self) if self.isBalancedSquadEnabled() else EventBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return EventBattleBalancedSquadActionsHandler(self) if self.isBalancedSquadEnabled() else EventBattleSquadActionsHandler(self)

    def _createScheduler(self):
        return EventSquadScheduler(self)

    def _vehicleStateCondition(self, v):
        result = True
        if v.level not in self.__eventBattlesCtrl.getModeSettings().levels:
            return result
        if self._isBalancedSquad:
            result = v.level in self._rosterSettings.getLevelsRange()
            if not result:
                return False
        accountDbID = account_helpers.getAccountDatabaseID()
        if not self.isCommander(accountDbID):
            commanderQueueType = self.getCommanderQueueType()
            if commanderQueueType and (commanderQueueType == QUEUE_TYPE.EVENT_BATTLES and v.isWheeledTech or commanderQueueType == QUEUE_TYPE.EVENT_BATTLES_2 and not v.isWheeledTech):
                return False
        if self._isUseSPGValidateRule and v.type == VEHICLE_CLASS_NAME.SPG:
            isHaveSPG = False
            spgDifferenceCount = self.getMaxSPGCount() - self.getCurrentSPGCount()
            if self.getMaxSPGCount() == 0:
                return False
            elif self.isCommander(accountDbID):
                return result
            elif spgDifferenceCount == 0:
                _, _ = self.getUnit()
                vInfos = self.getVehiclesInfo()
                for vInfo in vInfos:
                    if vInfo.vehClassIdx == VEHICLE_CLASS_INDICES['SPG']:
                        isHaveSPG = True

                if isHaveSPG:
                    return result
                return False
            elif spgDifferenceCount > 0:
                return result
            else:
                return False
        return super(EventBattleSquadEntity, self)._vehicleStateCondition(v)

    def _onServerSettingChanged(self, *args, **kwargs):
        balancedEnabled = self.isBalancedSquadEnabled()
        spgForbiddenChanged = self.getMaxSPGCount() != self._maxSpgCount
        if spgForbiddenChanged:
            self.invalidateVehicleStates()
        self._isBalancedSquad = balancedEnabled
        self._maxSpgCount = self.getMaxSPGCount()
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def _onUnitMemberVehiclesChanged(self, accoundDbID):
        self.invalidateVehicleStates()
        if self._isBalancedSquad and accoundDbID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def __showDialog(self, ctx):
        DialogsInterface.showDialog(rally_dialog_meta.createLeaveInfoMeta(ctx, 'eventDisabled'), lambda _: None)

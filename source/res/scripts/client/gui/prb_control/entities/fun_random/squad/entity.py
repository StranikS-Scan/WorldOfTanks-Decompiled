# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/squad/entity.py
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.squad.components import RestrictedSPGDataProvider
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.fun_random.pre_queue.vehicles_watcher import FunRandomVehiclesWatcher
from gui.prb_control.entities.fun_random.squad.action_handler import FunRandomSquadActionsHandler
from gui.prb_control.entities.fun_random.squad.actions_validator import FunRandomActionsValidator
from gui.prb_control.entities.fun_random.squad.scheduler import FunRandomSquadScheduler
from gui.prb_control.entities.random.squad.entity import BalancedSquadDynamicRosterSettings
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, Vehicle
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class FunRandomSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(FunRandomSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.FUN_RANDOM, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.FUN_RANDOM, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createFunRandomSquad()


class FunRandomSquadEntity(SquadEntity):
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __funRandomController = dependency.descriptor(IFunRandomController)

    def __init__(self):
        self.storage = prequeue_storage_getter(QUEUE_TYPE.FUN_RANDOM)()
        self._isBalancedSquad = False
        self._isUseSPGValidateRule = True
        self.__watcher = None
        self.__restrictedSPGDataProvider = RestrictedSPGDataProvider()
        super(FunRandomSquadEntity, self).__init__(FUNCTIONAL_FLAG.FUN_RANDOM, PREBATTLE_TYPE.FUN_RANDOM)
        return

    def init(self, ctx=None):
        self.storage.release()
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        self.__restrictedSPGDataProvider.init(self)
        funRandomSquadEntity = super(FunRandomSquadEntity, self).init(ctx)
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.__watcher = FunRandomVehiclesWatcher()
        self.__watcher.start()
        self.invalidateVehicleStates()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.__eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        return funRandomSquadEntity

    def fini(self, ctx=None, woEvents=False):
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__eventsCache.onSyncCompleted -= self._onServerSettingChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.__restrictedSPGDataProvider.fini()
        self._isUseSPGValidateRule = False
        self.invalidateVehicleStates()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(FunRandomSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def isBalancedSquadEnabled(self):
        return self.__eventsCache.isBalancedSquadEnabled()

    def hasSlotForSPG(self):
        return self.__restrictedSPGDataProvider.hasSlotForVehicleClass()

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__funRandomController.isBattlesPossible() else super(FunRandomSquadEntity, self).getConfirmDialogMeta(ctx)

    def getCurrentSPGCount(self):
        return self.__restrictedSPGDataProvider.getCurrentVheiclesOfClassCount()

    def getQueueType(self):
        return QUEUE_TYPE.FUN_RANDOM

    def getMaxSPGCount(self):
        return self.__restrictedSPGDataProvider.getMaxVehiclesOfClass()

    def getSquadLevelBounds(self):
        return self.__eventsCache.getBalancedSquadBounds()

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.FUN_RANDOM_SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True, None)
        else:
            return super(FunRandomSquadEntity, self).doSelectAction(action)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(FunRandomSquadEntity, self).leave(ctx, callback)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(FunRandomSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(FunRandomSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(FunRandomSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(FunRandomSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def _createActionsHandler(self):
        return FunRandomSquadActionsHandler(self)

    def _createActionsValidator(self):
        return FunRandomActionsValidator(self)

    def _createRosterSettings(self):
        if self._isBalancedSquad:
            _, unit = self.getUnit(safe=True)
            lowerBound, upperBound = self.getSquadLevelBounds()
            return BalancedSquadDynamicRosterSettings(unit=unit, lowerBound=lowerBound, upperBound=upperBound)
        return super(FunRandomSquadEntity, self)._createRosterSettings()

    def _createScheduler(self):
        return FunRandomSquadScheduler(self)

    def _onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def _onServerSettingChanged(self, *args, **kwargs):
        self.invalidateVehicleStates()
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onUnitMemberVehiclesChanged(self, accoundDbID):
        self.invalidateVehicleStates()
        if accoundDbID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def _vehicleStateCondition(self, v):
        if v.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            return True
        if self._isBalancedSquad:
            result = v.level in self._rosterSettings.getLevelsRange()
            if not result:
                return False
        return self.__restrictedSPGDataProvider.isVehcleOfClassAvailable() if self._isUseSPGValidateRule and v.type == VEHICLE_CLASS_NAME.SPG else super(FunRandomSquadEntity, self)._vehicleStateCondition(v)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/squad/entity.py
import logging
import typing
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from fun_random_common.fun_constants import FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID
from fun_random.gui.feature.util.fun_helpers import notifyCaller
from fun_random.gui.fun_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, REQUEST_TYPE
from fun_random.gui.prb_control.entities.pre_queue.vehicles_watcher import FunRandomVehiclesWatcher
from fun_random.gui.prb_control.entities.squad.actions_validator import FunRandomActionsValidator
from fun_random.gui.prb_control.entities.squad.ctx import FunSquadSettingsCtx, FunSquadChangeSubModeCtx
from fun_random.gui.prb_control.entities.squad.scheduler import FunRandomSquadScheduler
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.squad.components import RestrictedSPGDataProvider, RestrictedScoutDataProvider
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.random.squad.actions_handler import BalancedSquadActionsHandler
from gui.prb_control.entities.random.squad.entity import BalancedSquadDynamicRosterSettings
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, Vehicle
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from UnitBase import UNIT_ERROR, CLIENT_UNIT_CMD
_logger = logging.getLogger(__name__)

class FunRandomSquadEntryPoint(SquadEntryPoint):
    __funRandomController = dependency.descriptor(IFunRandomController)

    def __init__(self, accountsToInvite=None):
        super(FunRandomSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.FUN_RANDOM, accountsToInvite)
        self.__desiredSubModeID = UNKNOWN_EVENT_ID

    def setExtData(self, extData):
        self.__desiredSubModeID = extData.get(FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID)

    def makeDefCtx(self):
        return FunSquadSettingsCtx(self.__desiredSubModeID, accountsToInvite=self._accountsToInvite)

    def select(self, ctx, callback=None):
        desiredSubModeID = self.__desiredSubModeID
        desiredSubMode = self.__funRandomController.subModesHolder.getSubMode(desiredSubModeID)
        if not self.__funRandomController.isEnabled():
            _logger.warning('Trying to create fun random squad when FEP feature is disabled.')
            self.__abortSelection(UNIT_ERROR.OFF_SEASON, callback)
        elif desiredSubModeID == UNKNOWN_EVENT_ID or desiredSubMode is None:
            _logger.error('Trying to create fun random squad of invalid fun random sub mode %s.', desiredSubModeID)
            self.__abortSelection(UNIT_ERROR.BAD_PARAMS, callback)
        elif not desiredSubMode.isAvailable():
            _logger.debug('Trying to create fun random squad of unavailable fun random sub mode %s.', desiredSubModeID)
            self.__abortSelection(UNIT_ERROR.SORTIES_FORBIDDEN, callback)
        else:
            super(FunRandomSquadEntryPoint, self).select(ctx, callback)
        return

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createFunRandomSquad(ctx.getDesiredSubModeID())

    def __abortSelection(self, reason, callback=None):
        self.__desiredSubModeID = UNKNOWN_EVENT_ID
        self.__funRandomController.subModesHolder.setDesiredSubModeID(UNKNOWN_EVENT_ID)
        notifyCaller(callback, False)
        g_prbCtrlEvents.onUnitCreationFailure(reason)


class FunRandomSquadEntity(SquadEntity):
    __eventsCache = dependency.descriptor(IEventsCache)
    __funRandomController = dependency.descriptor(IFunRandomController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._isBalancedSquad = False
        self._isUseSPGValidateRule = True
        self._isUseScoutValidateRule = True
        self.__watcher = None
        self.__restrictedSPGDataProvider = RestrictedSPGDataProvider()
        self.__restrictedScoutDataProvider = RestrictedScoutDataProvider()
        super(FunRandomSquadEntity, self).__init__(FUNCTIONAL_FLAG.FUN_RANDOM, PREBATTLE_TYPE.FUN_RANDOM)
        return

    def init(self, ctx=None):
        self._isBalancedSquad = self.isBalancedSquadEnabled()
        self.__restrictedSPGDataProvider.init(self)
        self.__restrictedScoutDataProvider.init(self)
        self.__funRandomController.subModesHolder.setDesiredSubModeID(self.__getUnitSubModeID(), trustedSource=True)
        funRandomSquadEntity = super(FunRandomSquadEntity, self).init(ctx)
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.__watcher = FunRandomVehiclesWatcher()
        self.__watcher.start()
        self.invalidateVehicleStates()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__eventsCache.onSyncCompleted += self.__onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onInventoryVehiclesUpdated})
        return funRandomSquadEntity

    def fini(self, ctx=None, woEvents=False):
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__eventsCache.onSyncCompleted -= self.__onServerSettingChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__restrictedScoutDataProvider.fini()
        self.__restrictedSPGDataProvider.fini()
        self._isUseScoutValidateRule = False
        self._isUseSPGValidateRule = False
        self.invalidateVehicleStates()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(FunRandomSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def isBalancedSquadEnabled(self):
        return self.__eventsCache.isBalancedSquadEnabled()

    def hasSlotForScout(self):
        return self.__restrictedScoutDataProvider.hasSlotForVehicle()

    def hasSlotForSPG(self):
        return self.__restrictedSPGDataProvider.hasSlotForVehicle()

    def getConfirmDialogMeta(self, ctx):
        desiredSubMode = self.__funRandomController.subModesHolder.getDesiredSubMode()
        return None if desiredSubMode is None or not desiredSubMode.isAvailable() else super(FunRandomSquadEntity, self).getConfirmDialogMeta(ctx)

    def getCurrentSPGCount(self):
        return self.__restrictedSPGDataProvider.getCurrentVehiclesCount()

    def getCurrentScoutCount(self):
        return self.__restrictedScoutDataProvider.getCurrentVehiclesCount()

    def getQueueType(self):
        return QUEUE_TYPE.FUN_RANDOM

    def getMaxScoutCount(self):
        return self.__restrictedScoutDataProvider.getMaxPossibleVehicles()

    def getMaxScoutLevels(self):
        return self.__restrictedScoutDataProvider.getRestrictionLevels()

    def getMaxSPGCount(self):
        return self.__restrictedSPGDataProvider.getMaxPossibleVehicles()

    def getSquadLevelBounds(self):
        return self.__eventsCache.getBalancedSquadBounds()

    def setReserve(self, ctx, callback=None):
        pass

    def changeFunSubMode(self, ctx, callback=None):
        if not self._isInCoolDown(REQUEST_TYPE.CHANGE_FUN_SUB_MODE, coolDown=ctx.getCooldown()):
            self._requestsProcessor.doRequest(ctx, 'doCustomUnitCmd', CLIENT_UNIT_CMD.CHANGE_FUN_EVENT_ID, uint64Arg=ctx.getDesiredSubModeID(), callback=callback)
            self._cooldown.process(REQUEST_TYPE.CHANGE_FUN_SUB_MODE, coolDown=ctx.getCooldown())
        else:
            notifyCaller(callback, False)

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.FUN_RANDOM:
            return self.__doSubModeSelectAction(action)
        elif action.actionName in (PREBATTLE_ACTION_NAME.FUN_RANDOM_SQUAD, PREBATTLE_ACTION_NAME.SQUAD):
            g_eventDispatcher.showUnitWindow(self._prbType)
            self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True, None)
        else:
            return super(FunRandomSquadEntity, self).doSelectAction(action)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.__funRandomController.subModesHolder.setDesiredSubModeID(UNKNOWN_EVENT_ID)
        super(FunRandomSquadEntity, self).leave(ctx, callback)

    def unit_onUnitExtraChanged(self, extras):
        super(FunRandomSquadEntity, self).unit_onUnitExtraChanged(extras)
        self.__notifySubModeSwitching(self.__getUnitSubModeID())
        self.__funRandomController.subModesHolder.setDesiredSubModeID(self.__getUnitSubModeID(), trustedSource=True)
        self.invalidateVehicleStates()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(FunRandomSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(FunRandomSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(FunRandomSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self.__onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(FunRandomSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self.__onUnitMemberVehiclesChanged(dbID)

    def _getRequestHandlers(self):
        handlers = super(FunRandomSquadEntity, self)._getRequestHandlers()
        handlers[REQUEST_TYPE.CHANGE_FUN_SUB_MODE] = self.changeFunSubMode
        return handlers

    def _createActionsHandler(self):
        return BalancedSquadActionsHandler(self)

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

    def _vehicleStateCondition(self, v):
        if v.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            return True
        if self._isBalancedSquad:
            result = v.level in self._rosterSettings.getLevelsRange()
            if not result:
                return False
        if self._isUseScoutValidateRule and v.isScout and v.level in self.getMaxScoutLevels():
            return self.__restrictedScoutDataProvider.isTagVehicleAvailable()
        return self.__restrictedSPGDataProvider.isTagVehicleAvailable() if self._isUseSPGValidateRule and v.type == VEHICLE_CLASS_NAME.SPG else super(FunRandomSquadEntity, self)._vehicleStateCondition(v)

    def __getUnitSubModeID(self):
        extraData = self.getExtra()
        return extraData.funEventID if extraData else UNKNOWN_EVENT_ID

    def __doSubModeSelectAction(self, action):
        desiredSubModeID = action.extData.get(FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID)
        if desiredSubModeID == self.__getUnitSubModeID():
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True, None)
        elif self.isCommander():
            g_eventDispatcher.showUnitWindow(self._prbType)
            self.request(FunSquadChangeSubModeCtx(desiredSubModeID))
            return SelectResult(True, None)
        else:
            return super(FunRandomSquadEntity, self).doSelectAction(action)

    def __notifySubModeSwitching(self, subModeID):
        if not self.isCommander() and subModeID != self.__funRandomController.subModesHolder.getDesiredSubModeID():
            self._scheduler.notifySubModeSwitching(subModeID)

    def __onInventoryVehiclesUpdated(self, _):
        self.invalidateVehicleStates()

    def __onServerSettingChanged(self, *_, **__):
        self.invalidateVehicleStates()
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def __onUnitMemberVehiclesChanged(self, accountDBID):
        self.invalidateVehicleStates()
        if accountDBID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

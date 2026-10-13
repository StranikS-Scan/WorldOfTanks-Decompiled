# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/squad/entity.py
import typing
import AccountUnitAPI
import account_helpers
from debug_utils import LOG_ERROR
from helpers import dependency
from UnitBase import UNIT_ROLE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from portal.gui.portal_gui_constants import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, REQUEST_TYPE
from portal.gui.prb_control.entities.pre_queue.scheduler import PortalBattleScheduler
from portal.gui.prb_control.entities.squad.vehicles_watcher import PortalVehiclesWatcher
from portal.gui.prb_control.entities.squad.actions_validator import PortalSquadActionsValidator
from portal.gui.prb_control.entities.squad.actions_handler import PortalSquadActionsHandler
from portal.gui.prb_control.entities.squad.request_processor import PortalUnitRequestProcessor
from portal.gui.prb_control.entities.squad.ctx import SetUnitBattleLevelCtx
from portal.skeletons.portal_event_controller import IPortalEventController
from portal_common.portal_constants import PREBATTLE_TYPE, QUEUE_TYPE, CLIENT_UNIT_CMD
if typing.TYPE_CHECKING:
    from typing import Optional, Callable

class PortalEntryPoint(SquadEntryPoint):
    __portalEventController = dependency.descriptor(IPortalEventController)

    def __init__(self, accountsToInvite=None):
        super(PortalEntryPoint, self).__init__(FUNCTIONAL_FLAG.PORTAL, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquadByQueueType(QUEUE_TYPE.PORTAL, modeExtrasStr=self.__buildModeExtraParams())

    def __buildModeExtraParams(self):
        battleLevel = self.__portalEventController.battleLevel
        maxAvailableBattleLevel = self.__portalEventController.maxComplexityLevel
        return AccountUnitAPI.dumpExtras({'battleLevel': battleLevel,
         'maxAvailableBattleLevel': maxAvailableBattleLevel})


class PortalSquadEntity(SquadEntity):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __portalEventController = dependency.descriptor(IPortalEventController)

    def __init__(self):
        super(PortalSquadEntity, self).__init__(FUNCTIONAL_FLAG.PORTAL, PREBATTLE_TYPE.PORTAL)
        self._mmData = 0
        self.__watcher = None
        return

    def setReserve(self, ctx, callback=None):
        pass

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.queueType = self.getQueueType()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.invalidateVehicleStates()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = PortalVehiclesWatcher()
        self.__watcher.start()
        self.__portalEventController.onPortalSquadStateChanged(True, self.isCommander())
        return super(PortalSquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        self.__portalEventController.onPortalSquadStateChanged(False, self.isCommander())
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.invalidateVehicleStates()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(PortalSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getQueueType(self):
        return QUEUE_TYPE.PORTAL

    def doAction(self, action=None):
        self._mmData = 0 if action is None else action.mmData
        super(PortalSquadEntity, self).doAction(action)
        return

    def doBattleQueue(self, ctx, callback=None):
        ctx.mmData = self._mmData
        self._mmData = 0
        super(PortalSquadEntity, self).doBattleQueue(ctx, callback)

    def canInvite(self, prbType):
        return self.__portalEventController.isAvailable()

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__portalEventController.isEnabled() else super(PortalSquadEntity, self).getConfirmDialogMeta(ctx)

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(PortalSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(PortalSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(PortalSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()
            diff = prevRoleFlags ^ nextRoleFlags
            isCreatorChanged = diff & UNIT_ROLE.CREATOR > 0
            if isCreatorChanged:
                self.__portalEventController.onPortalSquadStateChanged(True, self.isCommander())

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(PortalSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def setBattleLevel(self, battleLevel):
        pInfo = self.getPlayerInfo()
        if not pInfo.isCommander():
            return
        ctx = SetUnitBattleLevelCtx(battleLevel, waitingID='prebattle/change_settings')
        self.__setBattleLevel(ctx)

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.PORTAL_BATTLE, PREBATTLE_ACTION_NAME.PORTAL_BATTLE_SQUAD)

    def _createActionsHandler(self):
        return PortalSquadActionsHandler(self)

    def _createActionsValidator(self):
        return PortalSquadActionsValidator(self)

    def _createScheduler(self):
        return PortalBattleScheduler(self)

    def _createRequestProcessor(self):
        return PortalUnitRequestProcessor(self)

    def _doStartBattleRequest(self, ctx, flags, callback):
        self._requestsProcessor.doRequest(ctx, 'startBattle', startBattleUnitCmd=CLIENT_UNIT_CMD.START_UNIT_PORTAL_BATTLE, vehInvID=ctx.selectVehInvID, gameplaysMask=ctx.getGamePlayMask(), arenaTypeID=ctx.getDemoArenaTypeID(), callback=callback, stopAutoSearch=flags.isInSearch())

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

    def __onUnitPortalPlayerInfoChanged(self, playerID, playerData):
        self._actionsHandler.setPortalPlayerInfoChanged()

    def __setBattleLevel(self, ctx, callback=None):
        if self._isInCoolDown(REQUEST_TYPE.PORTAL_SET_BATTLE_LEVEL, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change battle level', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'doUnitCmd', CLIENT_UNIT_CMD.SET_PORTAL_UNIT_BATTLE_LEVEL, ctx.getBattleLevel(), 0, '', callback=callback)
        self._cooldown.process(REQUEST_TYPE.PORTAL_SET_BATTLE_LEVEL, coolDown=ctx.getCooldown())

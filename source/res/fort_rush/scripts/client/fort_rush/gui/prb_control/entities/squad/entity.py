# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/prb_control/entities/squad/entity.py
from __future__ import absolute_import
import typing
import account_helpers
from fort_rush.gui.prb_control.entities.pre_queue.vehicles_watcher import FortRushVehicleWatcher
from gui.shared.event_dispatcher import showHangar
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush_common.configs.fort_rush_battles_config import fortRushBattlesConfigGameParamsSchema
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.base.squad.mixins import SquadRestrictionsMixin
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from fort_rush.gui.fort_rush_gui_constants import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, SELECTOR_BATTLE_TYPES
from fort_rush.gui.prb_control.entities.squad.actions_validator import FortRushSquadActionsValidator
from fort_rush.gui.prb_control.entities.squad.components import FortRushSquadRestrictionsProvider
from fort_rush_common.fort_rush_constants import PREBATTLE_TYPE, QUEUE_TYPE, CLIENT_UNIT_CMD

class FortRushEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(FortRushEntryPoint, self).__init__(FUNCTIONAL_FLAG.FORT_RUSH, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createSquadByQueueType(QUEUE_TYPE.FORT_RUSH)


class FortRushSquadEntity(SquadEntity, SquadRestrictionsMixin):
    frCtrl = dependency.descriptor(IFortRushBattleController)
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(FortRushSquadEntity, self).__init__(FUNCTIONAL_FLAG.FORT_RUSH, PREBATTLE_TYPE.FORT_RUSH)
        self._mmData = 0
        self.__watcher = None
        return

    def setReserve(self, ctx, callback=None):
        pass

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.initRestrictedRoleDataProvider(self)
        rv = super(FortRushSquadEntity, self).init(ctx)
        self.storage.queueType = self.getQueueType()
        self._switchActionsValidator()
        self._switchRosterSettings()
        self.invalidateVehicleStates()
        if not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.FORT_RUSH):
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.FORT_RUSH)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = FortRushVehicleWatcher()
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
        return super(FortRushSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    @property
    def squadRestrictions(self):
        config = fortRushBattlesConfigGameParamsSchema.getModel()
        return {} if config is None or config.squadRestrictions is None else config.squadRestrictions.toPlatoonRestrictionsDict()

    def getConfirmDialogMeta(self, ctx):
        return None if not self.frCtrl.isAvailable() else super(FortRushSquadEntity, self).getConfirmDialogMeta(ctx)

    def getQueueType(self):
        return QUEUE_TYPE.FORT_RUSH

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.FORT_RUSH, PREBATTLE_ACTION_NAME.FORT_RUSH_SQUAD):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(FortRushSquadEntity, self).doSelectAction(action)

    def doAction(self, action=None):
        self._mmData = 0 if action is None else action.mmData
        super(FortRushSquadEntity, self).doAction(action)
        return

    def doBattleQueue(self, ctx, callback=None):
        ctx.mmData = self._mmData
        self._mmData = 0
        super(FortRushSquadEntity, self).doBattleQueue(ctx, callback)

    def canInvite(self, prbType):
        return self.frCtrl.isAvailable()

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(FortRushSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(FortRushSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(FortRushSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(FortRushSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitReadyMaskChanged(self, prevMask, nextMask):
        super(FortRushSquadEntity, self).unit_onUnitReadyMaskChanged(prevMask, nextMask)
        self.invalidateVehicleStates()

    def _doStartBattleRequest(self, ctx, flags, callback):
        self._requestsProcessor.doRequest(ctx, 'startBattle', startBattleUnitCmd=CLIENT_UNIT_CMD.START_UNIT_FORT_RUSH_BATTLE, vehInvID=ctx.selectVehInvID, gameplaysMask=ctx.getGamePlayMask(), arenaTypeID=ctx.getDemoArenaTypeID(), callback=callback, stopAutoSearch=flags.isInSearch())

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
        return FortRushSquadActionsValidator(self)

    @classmethod
    def _createSquadRestrictionsProvider(cls):
        return FortRushSquadRestrictionsProvider()

    def _goToHangar(self):
        showHangar()

    def _vehicleStateCondition(self, v):
        return self.isVehicleSuitableForSquad(v) if self.isSquadRestrictionValid() else super(FortRushSquadEntity, self)._vehicleStateCondition(v)

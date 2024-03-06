# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/prb_control/entities/epic/squad/entity.py
from frontline.gui.prb_control.entities.epic.pre_queue.vehicles_watcher import EpicVehiclesWatcher
from frontline.gui.prb_control.entities.epic.squad.actions_validator import EpicSquadActionsValidator
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE, VEHICLE_CLASS_INDICES
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.header.fight_btn_tooltips import getEpicFightBtnTooltipData
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.random.squad.actions_handler import BalancedSquadActionsHandler
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
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


class EpicSquadEntity(SquadEntity):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._isBalancedSquad = False
        self._isUseSPGValidateRule = True
        self._maxSpgCount = False
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.EPIC)()
        super(EpicSquadEntity, self).__init__(FUNCTIONAL_FLAG.EPIC, PREBATTLE_TYPE.EPIC)
        return

    def init(self, ctx=None):
        self.storage.release()
        epicSquadEntity = super(EpicSquadEntity, self).init(ctx)
        self._maxSpgCount = self.getMaxSPGCount()
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
        self._isUseSPGValidateRule = False
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.invalidateVehicleStates()
        return super(EpicSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(EpicSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.EPIC

    def getFightBtnTooltipData(self, isStateDisabled):
        return (getEpicFightBtnTooltipData(self.canPlayerDoAction()), False) if isStateDisabled else super(EpicSquadEntity, self).getFightBtnTooltipData(isStateDisabled)

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.SQUAD,)

    def getMaxSPGCount(self):
        return self.lobbyContext.getServerSettings().getMaxSPGinSquads()

    def hasSlotForSPG(self):
        accountDbID = account_helpers.getAccountDatabaseID()
        return self.getMaxSPGCount() > 0 and (self.getCurrentSPGCount() < self.getMaxSPGCount() or self.isCommander(accountDbID))

    def getCurrentSPGCount(self):
        enableSPGCount = 0
        unitMgrId, unit = self.getUnit(safe=True)
        if unit is None:
            return enableSPGCount
        else:
            enableSPGCount = sum((slot.player is not None and slot.player.isReady and slot.vehicle is not None and slot.vehicle.vehClassIdx == VEHICLE_CLASS_INDICES['SPG'] for slot in self.getSlotsIterator(unitMgrId, unit)))
            return enableSPGCount

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

    def _createActionsHandler(self):
        return BalancedSquadActionsHandler(self)

    def _createActionsValidator(self):
        return EpicSquadActionsValidator(self)

    def _vehicleStateCondition(self, v):
        result = True
        if self._isUseSPGValidateRule and v.type == VEHICLE_CLASS_NAME.SPG:
            isHaveSPG = False
            accountDbID = account_helpers.getAccountDatabaseID()
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
        return super(EpicSquadEntity, self)._vehicleStateCondition(v)

    def _onServerSettingChanged(self, *args, **kwargs):
        self._maxSpgCount = self.getMaxSPGCount()
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def _onUnitMemberVehiclesChanged(self, accountDBID):
        self.invalidateVehicleStates()
        if accountDBID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

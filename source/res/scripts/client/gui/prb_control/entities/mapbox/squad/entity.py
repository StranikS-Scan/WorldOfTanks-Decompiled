# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/mapbox/squad/entity.py
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.Scaleform.daapi.view.lobby.header.fight_btn_tooltips import getMapboxFightBtnTooltipData
from gui.Scaleform.settings import TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.squad.components import RestrictedSPGDataProvider, RestrictedScoutDataProvider
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.mapbox.pre_queue.vehicles_watcher import MapboxVehiclesWatcher
from gui.prb_control.entities.mapbox.scheduler import MapboxScheduler
from gui.prb_control.entities.mapbox.squad.action_handler import MapboxSquadActionsHandler
from gui.prb_control.entities.mapbox.squad.actions_validator import MapboxSquadActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IMapboxController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class MapboxSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(MapboxSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.MAPBOX, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.MAPBOX, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createMapboxSquad()


class MapboxSquadEntity(SquadEntity):
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self):
        self._isBalancedSquad = False
        self._isUseSPGValidateRule = True
        self._isUseScoutValidateRule = True
        self.__watcher = None
        self.__restrictedSPGDataProvider = RestrictedSPGDataProvider()
        self.__restrictedScoutDataProvider = RestrictedScoutDataProvider()
        self.storage = prequeue_storage_getter(QUEUE_TYPE.MAPBOX)()
        super(MapboxSquadEntity, self).__init__(FUNCTIONAL_FLAG.MAPBOX, PREBATTLE_TYPE.MAPBOX)
        return

    def init(self, ctx=None):
        self.__restrictedSPGDataProvider.init(self)
        self.__restrictedScoutDataProvider.init(self)
        self.storage.release()
        mapboxSquadEntity = super(MapboxSquadEntity, self).init(ctx)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.__eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self.__watcher = MapboxVehiclesWatcher()
        self.__watcher.start()
        return mapboxSquadEntity

    def fini(self, ctx=None, woEvents=False):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.__eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self._isUseSPGValidateRule = False
        self._isUseScoutValidateRule = False
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self.invalidateVehicleStates()
        self.__restrictedSPGDataProvider.fini()
        self.__restrictedScoutDataProvider.fini()
        return super(MapboxSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(MapboxSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.MAPBOX

    def getMaxSPGCount(self):
        return self.__restrictedSPGDataProvider.getMaxPossibleVehicles()

    def getMaxScoutCount(self):
        return self.__restrictedScoutDataProvider.getMaxPossibleVehicles()

    def hasSlotForSPG(self):
        return self.__restrictedSPGDataProvider.hasSlotForVehicle()

    def hasSlotForScout(self):
        return self.__restrictedScoutDataProvider.hasSlotForVehicle()

    def getCurrentSPGCount(self):
        return self.__restrictedSPGDataProvider.getCurrentVehiclesCount()

    def getCurrentScoutCount(self):
        return self.__restrictedScoutDataProvider.getCurrentVehiclesCount()

    def getMaxScoutLevels(self):
        return self.__restrictedScoutDataProvider.getRestrictionLevels()

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__mapboxCtrl.isActive() else super(MapboxSquadEntity, self).getConfirmDialogMeta(ctx)

    def getFightBtnTooltipData(self, isStateDisabled):
        return (getMapboxFightBtnTooltipData(self.canPlayerDoAction()), False) if isStateDisabled else super(MapboxSquadEntity, self).getFightBtnTooltipData(isStateDisabled)

    def getSquadBtnTooltipData(self):
        header = backport.text(R.strings.platoon.headerButton.tooltips.inMapboxSquad.header())
        body = backport.text(R.strings.platoon.headerButton.tooltips.inMapboxSquad.body())
        return (makeTooltip(header, body), TOOLTIP_TYPES.COMPLEX)

    def unit_onUnitVehiclesChanged(self, dbID, vehicles):
        super(MapboxSquadEntity, self).unit_onUnitVehiclesChanged(dbID, vehicles)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitVehicleChanged(self, dbID, vehInvID, vehTypeCD):
        super(MapboxSquadEntity, self).unit_onUnitVehicleChanged(dbID, vehInvID, vehTypeCD)
        self._onUnitMemberVehiclesChanged(dbID)

    def unit_onUnitPlayerRoleChanged(self, playerID, prevRoleFlags, nextRoleFlags):
        super(MapboxSquadEntity, self).unit_onUnitPlayerRoleChanged(playerID, prevRoleFlags, nextRoleFlags)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def unit_onUnitPlayerRemoved(self, playerID, playerData):
        super(MapboxSquadEntity, self).unit_onUnitPlayerRemoved(playerID, playerData)
        if playerID == account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.MAPBOX_SQUAD,)

    def _createActionsHandler(self):
        return MapboxSquadActionsHandler(self)

    def _createActionsValidator(self):
        return MapboxSquadActionsValidator(self)

    def _createScheduler(self):
        return MapboxScheduler(self)

    def _vehicleStateCondition(self, v):
        if self._isUseSPGValidateRule and v.type == VEHICLE_CLASS_NAME.SPG:
            return self.__restrictedSPGDataProvider.isTagVehicleAvailable()
        return self.__restrictedScoutDataProvider.isTagVehicleAvailable() if self._isUseScoutValidateRule and v.isScout and v.level in self.getMaxScoutLevels() else super(MapboxSquadEntity, self)._vehicleStateCondition(v)

    def _onServerSettingChanged(self, *args, **kwargs):
        self.invalidateVehicleStates()
        self._switchActionsValidator()
        self.unit_onUnitRosterChanged()

    def _onInventoryVehiclesUpdated(self, diff):
        self.invalidateVehicleStates()

    def _onUnitMemberVehiclesChanged(self, accountDBID):
        self.invalidateVehicleStates()
        if accountDBID != account_helpers.getAccountDatabaseID():
            self.unit_onUnitRosterChanged()

    def __onVehicleClientStateChanged(self, _):
        if self.getPlayerInfo().isReady:
            vInfo = first(self.getVehiclesInfo())
            vehicle = vInfo.getVehicle()
            if vehicle and vehicle.getCustomState() in Vehicle.VEHICLE_STATE.UNSUITABLE:
                self.resetPlayerState()
        g_eventDispatcher.updateUI()

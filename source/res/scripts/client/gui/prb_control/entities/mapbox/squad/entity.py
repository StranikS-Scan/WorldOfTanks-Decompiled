# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/mapbox/squad/entity.py
import account_helpers
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.base.squad.components import RestrictedSPGDataProvider
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.mapbox.pre_queue.vehicles_watcher import MapboxVehiclesWatcher
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.mapbox.squad.actions_validator import MapboxSquadActionsValidator
from gui.prb_control.entities.mapbox.squad.action_handler import MapboxSquadActionsHandler
from gui.prb_control.entities.mapbox.scheduler import MapboxScheduler
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from skeletons.gui.game_control import IMapboxController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext

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
        self.__watcher = None
        self.__restrictedSPGDataProvider = RestrictedSPGDataProvider()
        self.storage = prequeue_storage_getter(QUEUE_TYPE.MAPBOX)()
        super(MapboxSquadEntity, self).__init__(FUNCTIONAL_FLAG.MAPBOX, PREBATTLE_TYPE.MAPBOX)
        return

    def init(self, ctx=None):
        self.__restrictedSPGDataProvider.init(self)
        self.storage.release()
        mapboxSquadEntity = super(MapboxSquadEntity, self).init(ctx)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        self.__eventsCache.onSyncCompleted += self._onServerSettingChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self._onInventoryVehiclesUpdated})
        self.__watcher = MapboxVehiclesWatcher()
        self.__watcher.start()
        return mapboxSquadEntity

    def fini(self, ctx=None, woEvents=False):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.__eventsCache.onSyncCompleted -= self._onServerSettingChanged
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self._isUseSPGValidateRule = False
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.invalidateVehicleStates()
        self.__restrictedSPGDataProvider.fini()
        return super(MapboxSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(MapboxSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.MAPBOX

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.MAPBOX_SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(MapboxSquadEntity, self).doSelectAction(action)

    def getMaxSPGCount(self):
        return self.__restrictedSPGDataProvider.getMaxVehiclesOfClass()

    def hasSlotForSPG(self):
        return self.__restrictedSPGDataProvider.hasSlotForVehicleClass()

    def getCurrentSPGCount(self):
        return self.__restrictedSPGDataProvider.getCurrentVheiclesOfClassCount()

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__mapboxCtrl.isActive() else super(MapboxSquadEntity, self).getConfirmDialogMeta(ctx)

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

    def _createActionsHandler(self):
        return MapboxSquadActionsHandler(self)

    def _createActionsValidator(self):
        return MapboxSquadActionsValidator(self)

    def _createScheduler(self):
        return MapboxScheduler(self)

    def _vehicleStateCondition(self, v):
        return self.__restrictedSPGDataProvider.isVehcleOfClassAvailable() if self._isUseSPGValidateRule and v.type == VEHICLE_CLASS_NAME.SPG else super(MapboxSquadEntity, self)._vehicleStateCondition(v)

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

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/fallout_controller.py
import weakref
import Event
from UnitBase import INV_ID_CLEAR_VEHICLE, FALLOUT_QUEUE_TYPE_TO_ROSTER, UNIT_OP
import account_helpers
from account_helpers.AccountSettings import FALLOUT_VEHICLES
from account_helpers.settings_core import g_settingsCore
from adisp import process
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.game_control.controllers import Controller
from gui.prb_control.context import unit_ctx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.storage import prequeue_storage_getter
from gui.server_events import g_eventsCache
from gui.shared import g_itemsCache
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import int2roman, i18n
from shared_utils import findFirst

class _BaseDataStorage(object):

    def __init__(self, proxy):
        super(_BaseDataStorage, self).__init__()
        self._proxy = weakref.proxy(proxy)

    def init(self):
        self._proxy.onSettingsChanged()

    def fini(self):
        pass

    def isEnabled(self):
        return False

    def setEnabled(self, isEnabled):
        pass

    def getBattleType(self):
        return QUEUE_TYPE.UNKNOWN

    def setBattleType(self, battleType):
        pass

    def getSelectedVehicles(self):
        return filter(None, map(g_itemsCache.items.getVehicle, filter(None, self.getSelectedSlots())))

    def addSelectedVehicle(self, vehInvID):
        pass

    def removeSelectedVehicle(self, vehInvID):
        pass

    def moveSelectedVehicle(self, vehInvID):
        pass

    def getSelectedSlots(self):
        pass

    def canChangeBattleType(self):
        return False

    def canAutomatch(self):
        return self.getBattleType() == QUEUE_TYPE.FALLOUT_MULTITEAM

    def isAutomatch(self):
        return False

    def setAutomatch(self, isAutomatch):
        pass


class _UserDataStorage(_BaseDataStorage):

    @prequeue_storage_getter(QUEUE_TYPE.FALLOUT)
    def falloutStorage(self):
        return None

    def init(self):
        super(_UserDataStorage, self).init()
        g_itemsCache.onSyncCompleted += self.__onItemsResync
        g_settingsCore.onSettingsChanged += self.__onSettingsResync

    def fini(self):
        g_itemsCache.onSyncCompleted -= self.__onItemsResync
        g_settingsCore.onSettingsChanged -= self.__onSettingsResync

    def isEnabled(self):
        return self.falloutStorage.isEnabled()

    def getBattleType(self):
        return self.falloutStorage.getBattleType()

    def setBattleType(self, battleType):
        if battleType != self.getBattleType():
            self.falloutStorage.setBattleType(battleType)
            self.falloutStorage.validateSelectedVehicles()

    def addSelectedVehicle(self, vehInvID):
        canSelect = self._proxy.canSelectVehicle(g_itemsCache.items.getVehicle(vehInvID))
        if not canSelect:
            LOG_ERROR('Selected vehicle in invalid!', vehInvID)
            return
        emptySlots = self._proxy.getEmptySlots()
        if not emptySlots:
            LOG_ERROR('No available slots to add new vehicle!', vehInvID)
            return
        firstEmptySlot = emptySlots[0]
        vehicles = self.getSelectedSlots()
        vehicles[firstEmptySlot] = vehInvID
        self.falloutStorage.setVehiclesInvIDs(vehicles)

    def removeSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        vehicles[vehicles.index(vehInvID)] = INV_ID_CLEAR_VEHICLE
        self.falloutStorage.setVehiclesInvIDs(vehicles)

    def moveSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        currentIndex = vehicles.index(vehInvID)
        if currentIndex == 0:
            newIndex = self._proxy.getConfig().maxVehiclesPerPlayer - 1
        else:
            newIndex = currentIndex - 1
        vehicles.insert(newIndex, vehicles.pop(currentIndex))
        self.falloutStorage.setVehiclesInvIDs(vehicles)

    def getSelectedSlots(self):
        return self.falloutStorage.getVehiclesInvIDs()

    def canChangeBattleType(self):
        return True

    def isAutomatch(self):
        return self.falloutStorage.isAutomatch()

    def setAutomatch(self, isAutomatch):
        if isAutomatch != self.isAutomatch():
            self.falloutStorage.setAutomatch(isAutomatch)

    def __onItemsResync(self, updateReason, _):
        if updateReason in (CACHE_SYNC_REASON.INVENTORY_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            self.falloutStorage.validateSelectedVehicles()
        if not (self.isEnabled() and self._proxy.isAvailable()):
            g_eventDispatcher.removeFalloutFromCarousel()

    def __onSettingsResync(self, diff):
        if {'falloutBattleType', 'isEnabled'} & set(diff.keys()):
            self.falloutStorage.validateSelectedVehicles()
            self._proxy.onSettingsChanged()
        if 'isAutomatch' in diff:
            self._proxy.onAutomatchChanged()
        if FALLOUT_VEHICLES in diff:
            self.falloutStorage.validateSelectedVehicles()
            self._proxy.onVehiclesChanged()


class _SquadDataStorage(_BaseDataStorage, GlobalListener):

    def __init__(self, proxy):
        super(_SquadDataStorage, self).__init__(proxy)
        self.__vehicles = []
        self.__battleType = QUEUE_TYPE.UNKNOWN

    def init(self):
        rosterType = self.unitFunctional.getRosterType()
        self.__battleType, _ = findFirst(lambda (k, v): v == rosterType, FALLOUT_QUEUE_TYPE_TO_ROSTER.iteritems(), (QUEUE_TYPE.UNKNOWN, None))
        self.__updateVehicles()
        self.startGlobalListening()
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehiclesUpdated})
        if self.isEnabled():
            g_eventDispatcher.addFalloutToCarousel()
        super(_SquadDataStorage, self).init()
        return

    def fini(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self, force=True)
        self.__vehicles = []
        self.__battleType = QUEUE_TYPE.UNKNOWN

    def isEnabled(self):
        return self.getBattleType() in QUEUE_TYPE.FALLOUT

    def getBattleType(self):
        return self.__battleType

    def setBattleType(self, battleType):
        if battleType != self.getBattleType():
            if not self.canChangeBattleType():
                LOG_ERROR('Cannot change battle type!', battleType)
                return
            self.__setFalloutType(battleType)

    def addSelectedVehicle(self, vehInvID):
        canSelect = self._proxy.canSelectVehicle(g_itemsCache.items.getVehicle(vehInvID))
        if not canSelect:
            LOG_ERROR('Selected vehicle in invalid!', vehInvID)
            return
        emptySlots = self._proxy.getEmptySlots()
        if not emptySlots:
            LOG_ERROR('No available slots to add new vehicle!', vehInvID)
            return
        firstEmptySlot = emptySlots[0]
        vehicles = self.getSelectedSlots()
        vehicles[firstEmptySlot] = vehInvID
        self.__setVehicles(vehicles)

    def removeSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        vehicles[vehicles.index(vehInvID)] = INV_ID_CLEAR_VEHICLE
        self.__setVehicles(vehicles)

    def moveSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        currentIndex = vehicles.index(vehInvID)
        if currentIndex == 0:
            newIndex = self._proxy.getConfig().maxVehiclesPerPlayer - 1
        else:
            newIndex = currentIndex - 1
        vehicles.insert(newIndex, vehicles.pop(currentIndex))
        self.__setVehicles(vehicles)

    def getSelectedSlots(self):
        return list(self.__vehicles)

    def canChangeBattleType(self):
        return self.unitFunctional.isCreator()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.CHANGE_FALLOUT_TYPE:
            rosterType = self.unitFunctional.getRosterType()
            self.__battleType, _ = findFirst(lambda (k, v): v == rosterType, FALLOUT_QUEUE_TYPE_TO_ROSTER.iteritems(), (QUEUE_TYPE.UNKNOWN, None))
            self.__updateVehicles()
            self._proxy.onSettingsChanged()
        return

    def onUnitVehiclesChanged(self, dbID, vInfos):
        if dbID == account_helpers.getAccountDatabaseID():
            self.__updateVehicles()
            self._proxy.onVehiclesChanged()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        if pInfo.isCurrentPlayer():
            self._proxy.onSettingsChanged()

    @process
    def __setVehicles(self, vehsList):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.SetVehiclesCtx(vehsList, 'prebattle/change_settings'))

    @process
    def __setFalloutType(self, eventType):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.ChangeFalloutQueueTypeCtx(eventType, 'prebattle/change_settings'))

    def __updateVehicles(self):
        maxVehs = self.unitFunctional.getRoster().MAX_VEHICLES
        valid = [INV_ID_CLEAR_VEHICLE] * maxVehs
        if self._proxy.getConfig().hasRequiredVehicles():
            slots = self.unitFunctional.getVehiclesInfo()
            vehicles = map(lambda vInfo: vInfo.vehInvID, slots)
            vehGetter = g_itemsCache.items.getVehicle
            for idx, invID in enumerate(vehicles[:maxVehs]):
                invVehicle = vehGetter(invID)
                if invVehicle is not None:
                    valid[idx] = invID

        if self.__vehicles != valid:
            self.__vehicles = valid
            return True
        else:
            return False

    def __onVehiclesUpdated(self, *args):
        if self.__updateVehicles():
            self.__setVehicles(self.__vehicles)


class FalloutController(Controller, GlobalListener):

    def __init__(self, proxy):
        super(FalloutController, self).__init__(proxy)
        self.__evtManager = Event.EventManager()
        self.onSettingsChanged = Event.Event(self.__evtManager)
        self.onAutomatchChanged = Event.Event(self.__evtManager)
        self.onVehiclesChanged = Event.Event(self.__evtManager)
        self.__dataStorage = None
        return

    def init(self):
        self.__dataStorage = _BaseDataStorage(self)

    def fini(self):
        self.__evtManager.clear()
        self.__dataStorage = None
        return

    def onLobbyInited(self, event):
        self.startGlobalListening()
        unitFunc = self.unitFunctional
        if unitFunc is not None and unitFunc.getEntityType() == PREBATTLE_TYPE.FALLOUT:
            self.__dataStorage = _SquadDataStorage(self)
        else:
            self.__dataStorage = _UserDataStorage(self)
        self.__dataStorage.init()
        return

    def onAvatarBecomePlayer(self):
        self.__dataStorage.fini()
        self.__dataStorage = _BaseDataStorage(self)
        self.stopGlobalListening()

    def onDisconnected(self):
        self.__dataStorage.fini()
        self.__dataStorage = _BaseDataStorage(self)
        self.stopGlobalListening()

    def isAvailable(self):
        return g_eventsCache.isFalloutEnabled()

    def isEnabled(self):
        return self.isAvailable() and self.__dataStorage.isEnabled()

    def isSelected(self):
        return self.isEnabled() and self.__dataStorage.getBattleType() in QUEUE_TYPE.FALLOUT

    def setEnabled(self, isEnabled):
        self.__dataStorage.setEnabled(isEnabled)

    def getBattleType(self):
        return self.__dataStorage.getBattleType()

    def setBattleType(self, battleType):
        self.__dataStorage.setBattleType(battleType)

    def getSelectedVehicles(self):
        return self.__dataStorage.getSelectedVehicles()

    def addSelectedVehicle(self, vehInvID):
        self.__dataStorage.addSelectedVehicle(vehInvID)

    def removeSelectedVehicle(self, vehInvID):
        self.__dataStorage.removeSelectedVehicle(vehInvID)

    def moveSelectedVehicle(self, vehInvID):
        self.__dataStorage.moveSelectedVehicle(vehInvID)

    def getConfig(self):
        return g_eventsCache.getFalloutConfig(self.getBattleType())

    def getSelectedSlots(self):
        return self.__dataStorage.getSelectedSlots()

    def getEmptySlots(self):
        emptySlots = []
        for idx, v in enumerate(self.getSelectedSlots()):
            if v == INV_ID_CLEAR_VEHICLE:
                emptySlots.append(idx)

        return emptySlots

    def getRequiredSlots(self):
        cfg = self.getConfig()
        selectedVehicles = self.getSelectedVehicles()
        requiredSlotsNumber = max(0, cfg.minVehiclesPerPlayer - len(selectedVehicles))
        return () if not requiredSlotsNumber else self.getEmptySlots()[:requiredSlotsNumber]

    def canSelectVehicle(self, vehicle):
        if not self.isSelected():
            return False
        cfg = self.getConfig()
        if not cfg.hasRequiredVehicles():
            return False
        if not vehicle.isFalloutAvailable:
            return False
        if vehicle.isInBattle:
            return False
        return False if self.mustSelectRequiredVehicle() and vehicle.level != cfg.vehicleLevelRequired else True

    def mustSelectRequiredVehicle(self):
        return len(self.getEmptySlots()) == 1 and not self.requiredVehicleSelected()

    def requiredVehicleSelected(self):
        cfg = self.getConfig()
        return findFirst(lambda v: v.level == cfg.vehicleLevelRequired, self.getSelectedVehicles()) is not None

    def carouselSelectionButtonTooltip(self):
        cfg = self.getConfig()
        return i18n.makeString(FALLOUT.TANKCAROUSELSLOT_SELECTIONBUTTONTOOLTIP, requiredLevel=int2roman(cfg.vehicleLevelRequired), level=toRomanRangeString(list(cfg.allowedLevels), 1))

    def canChangeBattleType(self):
        return self.__dataStorage.canChangeBattleType()

    def canAutomatch(self):
        return self.__dataStorage.canAutomatch()

    def isAutomatch(self):
        return self.__dataStorage.isAutomatch()

    def setAutomatch(self, isAutomatch):
        self.__dataStorage.setAutomatch(isAutomatch)

    def onUnitFunctionalInited(self):
        unitFunc = self.unitFunctional
        if unitFunc is not None and unitFunc.getEntityType() == PREBATTLE_TYPE.FALLOUT:
            self.__dataStorage.fini()
            self.__dataStorage = _SquadDataStorage(self)
            self.__dataStorage.init()
        return

    def onUnitFunctionalFinished(self):
        self.__dataStorage.fini()
        self.__dataStorage = _UserDataStorage(self)
        self.__dataStorage.init()

    def onUnitRejoin(self):
        unitFunc = self.unitFunctional
        if unitFunc is not None and unitFunc.getEntityType() == PREBATTLE_TYPE.FALLOUT:
            self.__dataStorage.fini()
            self.__dataStorage = _SquadDataStorage(self)
            self.__dataStorage.init()
        return

    def isSuitableVeh(self, vehicle):
        return not (self.isSelected() and not vehicle.isFalloutAvailable) and vehicle.getCustomState() not in Vehicle.VEHICLE_STATE.CUSTOM

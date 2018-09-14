# Embedded file name: scripts/client/gui/game_control/fallout_controller.py
import weakref
import Event
from UnitBase import INV_ID_CLEAR_VEHICLE
from adisp import process
from constants import PREBATTLE_TYPE, FALLOUT_BATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
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
from gui.shared.utils import getPlayerDatabaseID
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
        return FALLOUT_BATTLE_TYPE.UNDEFINED

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
        return ()

    def canChangeBattleType(self):
        return False

    def canAutomatch(self):
        return self.getBattleType() == FALLOUT_BATTLE_TYPE.MULTITEAM

    def isAutomatch(self):
        return False

    def setAutomatch(self, isAutomatch):
        pass


class _UserDataStorage(_BaseDataStorage):

    def __init__(self, proxy):
        super(_UserDataStorage, self).__init__(proxy)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def eventsStorage(self):
        return None

    def init(self):
        self._proxy.onSettingsChanged()
        g_itemsCache.onSyncCompleted += self.__onItemsResync

    def fini(self):
        g_itemsCache.onSyncCompleted -= self.__onItemsResync

    def isEnabled(self):
        return self.eventsStorage.isEnabled()

    def getBattleType(self):
        return self.eventsStorage.getBattleType()

    def setBattleType(self, battleType):
        if battleType != self.getBattleType():
            self.eventsStorage.setBattleType(battleType)
            self.eventsStorage.validateSelectedVehicles()
            self._proxy.onSettingsChanged()

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
        self.eventsStorage.setVehiclesInvIDs(vehicles)
        self._proxy.onVehiclesChanged()

    def removeSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        vehicles[vehicles.index(vehInvID)] = INV_ID_CLEAR_VEHICLE
        self.eventsStorage.setVehiclesInvIDs(vehicles)
        self._proxy.onVehiclesChanged()

    def moveSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        currentIndex = vehicles.index(vehInvID)
        if currentIndex == 0:
            newIndex = self._proxy.getConfig().maxVehiclesPerPlayer - 1
        else:
            newIndex = currentIndex - 1
        vehicles.insert(newIndex, vehicles.pop(currentIndex))
        self.eventsStorage.setVehiclesInvIDs(vehicles)
        self._proxy.onVehiclesChanged()

    def getSelectedSlots(self):
        return self.eventsStorage.getVehiclesInvIDs()

    def canChangeBattleType(self):
        return True

    def isAutomatch(self):
        return self.eventsStorage.isAutomatch()

    def setAutomatch(self, isAutomatch):
        if isAutomatch != self.isAutomatch():
            self.eventsStorage.setAutomatch(isAutomatch)
            self._proxy.onAutomatchChanged()

    def __onItemsResync(self, updateReason, _):
        if updateReason in (CACHE_SYNC_REASON.INVENTORY_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            if self.eventsStorage.validateSelectedVehicles():
                self._proxy.onVehiclesChanged()
        if not (self.isEnabled() and self._proxy.isAvailable()):
            g_eventDispatcher.removeFalloutFromCarousel()


class _SquadDataStorage(_BaseDataStorage, GlobalListener):

    def __init__(self, proxy):
        super(_SquadDataStorage, self).__init__(proxy)
        self.__vehicles = []
        self.__battleType = FALLOUT_BATTLE_TYPE.UNDEFINED

    def init(self):
        self.__battleType = self.__getExtra().eventType
        self.__updateVehicles()
        self.startGlobalListening()
        if self.isEnabled():
            g_eventDispatcher.addFalloutToCarousel()
        self._proxy.onSettingsChanged()

    def fini(self):
        self.stopGlobalListening()
        self.__vehicles = []
        self.__battleType = FALLOUT_BATTLE_TYPE.UNDEFINED

    def isEnabled(self):
        return self.getBattleType() != FALLOUT_BATTLE_TYPE.UNDEFINED

    def getBattleType(self):
        return self.__battleType

    def setBattleType(self, battleType):
        if battleType != self.getBattleType():
            if not self.canChangeBattleType():
                LOG_ERROR('Cannot change battle type!', battleType)
                return
            self.__setEventType(battleType)

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

    def onUnitExtraChanged(self, extra):
        if self.__battleType != self.__getExtra().eventType:
            self.__battleType = self.__getExtra().eventType
            self.__updateVehicles()
            self._proxy.onSettingsChanged()
            return
        if self.__updateVehicles():
            self._proxy.onVehiclesChanged()

    def onUnitPlayerRolesChanged(self, pInfo, pPermissions):
        if pInfo.isCurrentPlayer():
            self._proxy.onSettingsChanged()

    @process
    def __setVehicles(self, vehsList):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.SetEventVehiclesCtx(vehsList, 'prebattle/change_settings'))

    @process
    def __setEventType(self, eventType):
        yield self.prbDispatcher.sendUnitRequest(unit_ctx.ChangeEventSquadTypeCtx(eventType, 'prebattle/change_settings'))

    def __updateVehicles(self):
        maxVehs = self._proxy.getConfig().maxVehiclesPerPlayer
        valid = [INV_ID_CLEAR_VEHICLE] * maxVehs
        slots = self.__getExtra().accountVehicles.get(getPlayerDatabaseID(), ())
        vehicles = map(lambda (vehInvID, vehIntCD): vehInvID, slots)
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

    def __getExtra(self):
        return self.unitFunctional.getExtra()


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
        g_eventsCache.onSyncCompleted += self.__onEventsCacheResync

    def fini(self):
        g_eventsCache.onSyncCompleted -= self.__onEventsCacheResync
        self.__evtManager.clear()
        self.__dataStorage = None
        return

    def onLobbyInited(self, event):
        self.startGlobalListening()
        unitFunc = self.unitFunctional
        if unitFunc is not None and unitFunc.getEntityType() == PREBATTLE_TYPE.SQUAD and unitFunc.getExtra().eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
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
        return g_eventsCache.isEventEnabled()

    def isEnabled(self):
        return self.isAvailable() and self.__dataStorage.isEnabled()

    def isSelected(self):
        return self.isEnabled() and self.__dataStorage.getBattleType() != FALLOUT_BATTLE_TYPE.UNDEFINED

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
        if not requiredSlotsNumber:
            return ()
        return self.getEmptySlots()[:requiredSlotsNumber]

    def canSelectVehicle(self, vehicle):
        if not self.isSelected():
            return False
        cfg = self.getConfig()
        if not cfg.hasRequiredVehicles():
            return False
        if vehicle.intCD not in cfg.allowedVehicles:
            return False
        if self.mustSelectRequiredVehicle() and vehicle.level != cfg.vehicleLevelRequired:
            return False
        return True

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
        if unitFunc is not None and unitFunc.getEntityType() == PREBATTLE_TYPE.SQUAD and unitFunc.getExtra().eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
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
        if unitFunc is not None and unitFunc.getEntityType() == PREBATTLE_TYPE.SQUAD and unitFunc.getExtra().eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
            self.__dataStorage.fini()
            self.__dataStorage = _SquadDataStorage(self)
            self.__dataStorage.init()
        return

    def onPreQueueFunctionalFinished(self):
        self.onSettingsChanged()
        self.onVehiclesChanged()

    def __onEventsCacheResync(self):
        self.onSettingsChanged()

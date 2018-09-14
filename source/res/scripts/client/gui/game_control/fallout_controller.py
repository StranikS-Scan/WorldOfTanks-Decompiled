# Embedded file name: scripts/client/gui/game_control/fallout_controller.py
import weakref
import Event
from UnitBase import INV_ID_CLEAR_VEHICLE
from account_helpers.AccountSettings import AccountSettings, FALLOUT_VEHICLES
from account_helpers.settings_core import g_settingsCore
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from adisp import process
from constants import PREBATTLE_TYPE, FALLOUT_BATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.game_control.controllers import Controller
from gui.prb_control.context import unit_ctx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.prb_helpers import GlobalListener
from gui.server_events import g_eventsCache
from gui.shared import g_itemsCache
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.utils import getPlayerDatabaseID
from helpers import int2roman, i18n
from shared_utils import findFirst
_SETTINGS_DEFAULTS = {'isEnabled': False,
 'falloutBattleType': 0}

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


class _UserDataStorage(_BaseDataStorage):

    def __init__(self, proxy):
        super(_UserDataStorage, self).__init__(proxy)
        self.__settings = {}
        self.__vehicles = {}

    def init(self):
        self.__settings = g_settingsCore.serverSettings.getSection(SETTINGS_SECTIONS.FALLOUT, _SETTINGS_DEFAULTS)
        self.__vehicles = AccountSettings.getFavorites(FALLOUT_VEHICLES)
        self.__updateVehicles()
        g_itemsCache.onSyncCompleted += self.__onItemsResync
        if self.isEnabled() and self._proxy.isAvailable():
            g_eventDispatcher.addFalloutToCarousel()
        self._proxy.onSettingsChanged()

    def fini(self):
        self.__settings.clear()
        self.__vehicles.clear()
        g_itemsCache.onSyncCompleted -= self.__onItemsResync

    def isEnabled(self):
        return bool(self.__settings['isEnabled'])

    def setEnabled(self, isEnabled):
        self.__settings['isEnabled'] = isEnabled
        if not isEnabled:
            self.__settings['falloutBattleType'] = FALLOUT_BATTLE_TYPE.UNDEFINED
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)
        self.__updateVehicles()
        self._proxy.onSettingsChanged()

    def getBattleType(self):
        return self.__settings['falloutBattleType']

    def setBattleType(self, battleType):
        if battleType not in FALLOUT_BATTLE_TYPE.ALL:
            LOG_ERROR('Unsupported battle type given!', battleType)
            return
        self.__settings['falloutBattleType'] = battleType
        g_settingsCore.serverSettings.setSection(SETTINGS_SECTIONS.FALLOUT, self.__settings)
        self.__updateVehicles()
        self._proxy.onSettingsChanged()

    def addSelectedVehicle(self, vehInvID):
        canSelect, _ = self._proxy.canSelectVehicle(g_itemsCache.items.getVehicle(vehInvID))
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
        AccountSettings.setFavorites(FALLOUT_VEHICLES, self.__vehicles)
        self._proxy.onVehiclesChanged()

    def removeSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        vehicles[vehicles.index(vehInvID)] = INV_ID_CLEAR_VEHICLE
        AccountSettings.setFavorites(FALLOUT_VEHICLES, self.__vehicles)
        self._proxy.onVehiclesChanged()

    def moveSelectedVehicle(self, vehInvID):
        vehicles = self.getSelectedSlots()
        currentIndex = vehicles.index(vehInvID)
        if currentIndex == 0:
            newIndex = self._proxy.getConfig().maxVehiclesPerPlayer - 1
        else:
            newIndex = currentIndex - 1
        vehicles.insert(newIndex, vehicles.pop(currentIndex))
        AccountSettings.setFavorites(FALLOUT_VEHICLES, self.__vehicles)
        self._proxy.onVehiclesChanged()

    def getSelectedSlots(self):
        return self.__vehicles[self.getBattleType()]

    def canChangeBattleType(self):
        return True

    def __updateVehicles(self):
        maxVehs = self._proxy.getConfig().maxVehiclesPerPlayer
        valid = [INV_ID_CLEAR_VEHICLE] * maxVehs
        battleType = self.getBattleType()
        vehicles = self.__vehicles.get(battleType, ())
        vehGetter = g_itemsCache.items.getVehicle
        for idx, invID in enumerate(vehicles[:maxVehs]):
            invVehicle = vehGetter(invID)
            if invVehicle is not None:
                valid[idx] = invID

        if valid != vehicles:
            self.__vehicles[battleType] = valid
            AccountSettings.setFavorites(FALLOUT_VEHICLES, self.__vehicles)
        return

    def __onItemsResync(self, updateReason, _):
        if updateReason == CACHE_SYNC_REASON.INVENTORY_RESYNC:
            self.__updateVehicles()
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
        if self.isEnabled() and self.canChangeBattleType():
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
        if not self.canChangeBattleType():
            LOG_ERROR('Cannot change battle type!', battleType)
            return
        self.__setEventType(battleType)

    def addSelectedVehicle(self, vehInvID):
        canSelect, _ = self._proxy.canSelectVehicle(g_itemsCache.items.getVehicle(vehInvID))
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
        self.__battleType = self.__getExtra().eventType
        self.__updateVehicles()
        self._proxy.onSettingsChanged()
        self._proxy.onVehiclesChanged()

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

        self.__vehicles = valid
        return

    def __getExtra(self):
        return self.unitFunctional.getExtra()


class FalloutController(Controller, GlobalListener):

    def __init__(self, proxy):
        super(FalloutController, self).__init__(proxy)
        self.__evtManager = Event.EventManager()
        self.onSettingsChanged = Event.Event(self.__evtManager)
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
        if unitFunc is not None and unitFunc.getPrbType() == PREBATTLE_TYPE.SQUAD and unitFunc.getExtra().eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
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
            return (False, '')
        else:
            cfg = self.getConfig()
            if findFirst(lambda v: v.level == cfg.vehicleLevelRequired, self.getSelectedVehicles()) is None and vehicle.level != cfg.vehicleLevelRequired:
                return (False, i18n.makeString(FALLOUT.TANKCAROUSELSLOT_SELECTIONBUTTONTOOLTIP, requiredLevel=int2roman(cfg.vehicleLevelRequired), level=toRomanRangeString(list(cfg.allowedLevels - {cfg.vehicleLevelRequired}), 1)))
            return (True, '')

    def canChangeBattleType(self):
        return self.__dataStorage.canChangeBattleType()

    def onUnitFunctionalInited(self):
        unitFunc = self.unitFunctional
        if unitFunc is not None and unitFunc.getPrbType() == PREBATTLE_TYPE.SQUAD and unitFunc.getExtra().eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
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
        if unitFunc is not None and unitFunc.getPrbType() == PREBATTLE_TYPE.SQUAD and unitFunc.getExtra().eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
            self.__dataStorage.fini()
            self.__dataStorage = _SquadDataStorage(self)
            self.__dataStorage.init()
        return

    def __onEventsCacheResync(self):
        self.onSettingsChanged()

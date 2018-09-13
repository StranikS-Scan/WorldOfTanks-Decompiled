# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TankCarousel.py
from operator import attrgetter
import BigWorld
import constants
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, CAROUSEL_FILTER
from adisp import process
from gui.shared.tooltips import ACTION_TOOLTIPS_STATE, ACTION_TOOLTIPS_TYPE
from items.vehicles import VEHICLE_CLASS_TAGS
from gui import SystemMessages
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache, REQ_CRITERIA
from gui.shared.utils import decorators
from gui.shared.gui_items import CLAN_LOCK
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer, VehicleFavoriteProcessor
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, Vehicle
from gui.Scaleform import getVehicleTypeAssetPath
from gui.Scaleform.daapi.view.meta.TankCarouselMeta import TankCarouselMeta

class TankCarousel(TankCarouselMeta, GlobalListener):
    UPDATE_LOCKS_PERIOD = 60

    def __init__(self):
        super(TankCarousel, self).__init__()
        self.__updateVehiclesTimerId = None
        defaults = AccountSettings.getFilterDefault(CAROUSEL_FILTER)
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        filters = g_settingsCore.serverSettings.getSection(CAROUSEL_FILTER, defaults)
        tankTypeIsNegative = filters['tankTypeIsNegative']
        del filters['tankTypeIsNegative']
        if tankTypeIsNegative:
            intTankType = -filters['tankType']
        else:
            intTankType = filters['tankType']
        filters['tankType'] = 'none'
        for idx, type in enumerate(VEHICLE_CLASS_TAGS):
            if idx == intTankType:
                filters['tankType'] = type
                break

        nationIsNegative = filters['nationIsNegative']
        del filters['nationIsNegative']
        if nationIsNegative:
            filters['nation'] = -filters['nation']
        self.vehiclesFilter = filters
        return

    def _populate(self):
        super(TankCarousel, self)._populate()
        if self.__updateVehiclesTimerId is not None:
            BigWorld.cancelCallback(self.__updateVehiclesTimerId)
            self.__updateVehiclesTimerId = None
        self.as_setCarouselFilterS(self.vehiclesFilter)
        return

    def _dispose(self):
        if self.__updateVehiclesTimerId is not None:
            BigWorld.cancelCallback(self.__updateVehiclesTimerId)
            self.__updateVehiclesTimerId = None
        super(TankCarousel, self)._dispose()
        return

    def showVehicleInfo(self, vehInvID):
        vehicle = g_itemsCache.items.getVehicle(int(vehInvID))
        if vehicle is not None:
            self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_INFO_WINDOW, {'vehicleCompactDescr': vehicle.intCD}))
        return

    def toResearch(self, intCD):
        if intCD is not None:
            Event = events.LoadEvent
            exitEvent = Event(Event.LOAD_HANGAR)
            loadEvent = Event(Event.LOAD_RESEARCH, ctx={'rootCD': intCD,
             'exit': exitEvent})
            self.fireEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            LOG_ERROR("Can't go to Research because id for current vehicle is None")
        return

    def vehicleSell(self, vehInvID):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_VEHICLE_SELL_DIALOG, {'vehInvID': int(vehInvID)}))

    def vehicleChange(self, vehInvID):
        g_currentVehicle.selectVehicle(int(vehInvID))

    @decorators.process('buySlot')
    def buySlot(self):
        result = yield VehicleSlotBuyer().request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def buyTankClick(self):
        shopFilter = list(AccountSettings.getFilter('shop_current'))
        shopFilter[1] = 'vehicle'
        AccountSettings.setFilter('shop_current', tuple(shopFilter))
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_SHOP), EVENT_BUS_SCOPE.LOBBY)

    def getVehicleTypeProvider(self):
        all = self.__getProviderObject('none')
        all['label'] = self.__getVehicleTypeLabel('all')
        result = [all]
        for vehicleType in VEHICLE_TYPES_ORDER:
            result.append(self.__getProviderObject(vehicleType))

        return result

    def __getProviderObject(self, vehicleType):
        assetPath = {'label': self.__getVehicleTypeLabel(vehicleType),
         'data': vehicleType,
         'icon': getVehicleTypeAssetPath(vehicleType)}
        return assetPath

    def __getVehicleTypeLabel(self, vehicleType):
        return '#menu:carousel_tank_filter/' + vehicleType

    @process
    def favoriteVehicle(self, vehInvID, isFavorite):
        vehicle = g_itemsCache.items.getVehicle(int(vehInvID))
        if vehicle is not None:
            result = yield VehicleFavoriteProcessor(vehicle, bool(isFavorite)).request()
            if not result.success:
                LOG_ERROR('Cannot set selected vehicle as favorite due to following error: ', result.userMsg)
        return

    def setVehiclesFilter(self, nation, tankType, ready):
        self.vehiclesFilter['nation'] = nation
        self.vehiclesFilter['ready'] = ready
        self.vehiclesFilter['tankType'] = tankType
        filters = {'nation': abs(nation),
         'nationIsNegative': nation < 0,
         'ready': ready}
        intTankType = -1
        for idx, type in enumerate(VEHICLE_CLASS_TAGS):
            if type == tankType:
                intTankType = idx
                break

        filters['tankTypeIsNegative'] = intTankType < 0
        filters['tankType'] = abs(intTankType)
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.serverSettings.setSection(CAROUSEL_FILTER, filters)
        self.showVehicles()

    def showVehicles(self):
        filterCriteria = REQ_CRITERIA.INVENTORY
        if self.vehiclesFilter['nation'] != -1:
            filterCriteria |= REQ_CRITERIA.NATIONS([self.vehiclesFilter['nation']])
        if self.vehiclesFilter['tankType'] != 'none':
            filterCriteria |= REQ_CRITERIA.VEHICLE.CLASSES([self.vehiclesFilter['tankType']])
        if self.vehiclesFilter['ready']:
            filterCriteria |= REQ_CRITERIA.VEHICLE.FAVORITE
        items = g_itemsCache.items
        filteredVehs = items.getVehicles(filterCriteria)

        def sorting(v1, v2):
            if v1.isFavorite and not v2.isFavorite:
                return -1
            if not v1.isFavorite and v2.isFavorite:
                return 1
            return v1.__cmp__(v2)

        vehsCDs = map(attrgetter('intCD'), sorted(filteredVehs.itervalues(), sorting))
        LOG_DEBUG('Showing carousel vehicles: ', vehsCDs)
        self.as_showVehiclesS(vehsCDs)

    def updateVehicles(self, vehicles = None):
        isSet = vehicles is None
        filterCriteria = REQ_CRITERIA.INVENTORY
        if vehicles is not None:
            filterCriteria |= REQ_CRITERIA.IN_CD_LIST(vehicles)
        items = g_itemsCache.items
        filteredVehs = items.getVehicles(filterCriteria)
        if vehicles is None:
            vehicles = filteredVehs.keys()
        isSuitablePredicate = lambda vehIntCD: True
        if self.preQueueFunctional.getQueueType() == constants.QUEUE_TYPE.HISTORICAL:
            battle = self.preQueueFunctional.getItemData()
            if battle is not None:
                isSuitablePredicate = battle.canParticipateWith
        vehsData = {}
        for intCD in vehicles:
            data = None
            vehicle = filteredVehs.get(intCD)
            if vehicle is not None:
                vState, vStateLvl = vehicle.getState()
                if vState != Vehicle.VEHICLE_STATE.BATTLE and not isSuitablePredicate(vehicle.intCD):
                    vState, vStateLvl = Vehicle.VEHICLE_STATE.NOT_SUITABLE, Vehicle.VEHICLE_STATE_LEVEL.WARNING
                data = {'id': vehicle.invID,
                 'inventoryId': vehicle.invID,
                 'label': vehicle.userName,
                 'image': vehicle.icon,
                 'nation': vehicle.nationID,
                 'level': vehicle.level,
                 'stat': vState,
                 'stateLevel': vStateLvl,
                 'doubleXPReceived': vehicle.dailyXPFactor,
                 'compactDescr': vehicle.intCD,
                 'favorite': vehicle.isFavorite,
                 'canSell': vehicle.canSell,
                 'clanLock': vehicle.clanLock,
                 'elite': vehicle.isElite,
                 'premium': vehicle.isPremium,
                 'tankType': vehicle.type,
                 'exp': vehicle.xp,
                 'current': 0,
                 'enabled': True}
            vehsData[intCD] = data

        LOG_DEBUG('Updating carousel vehicles: ', vehsData if not isSet else 'full sync')
        self.as_updateVehiclesS(vehsData, isSet)
        self.showVehicles()
        isVehTypeLock = sum((len(v) for v in items.stats.vehicleTypeLocks.itervalues()))
        isGlobalVehLock = sum((len(v) for v in items.stats.globalVehicleLocks.itervalues()))
        if self.__updateVehiclesTimerId is None and (isVehTypeLock or isGlobalVehLock):
            self.__updateVehiclesTimerId = BigWorld.callback(self.UPDATE_LOCKS_PERIOD, self.updateLockTimers)
            LOG_DEBUG('Lock timer updated')
        return

    def updateParams(self):
        items = g_itemsCache.items
        slots = items.stats.vehicleSlots
        vehicles = len(items.getVehicles(REQ_CRITERIA.INVENTORY))
        shopPrice = items.shop.getVehicleSlotsPrice(slots)
        defaultPrice = items.shop.defaults.getVehicleSlotsPrice(slots)
        selectedTankID = g_currentVehicle.item.intCD if g_currentVehicle.isPresent() else None
        action = None
        if shopPrice != defaultPrice:
            action = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
             'key': 'slotsPrices',
             'isBuying': True,
             'state': (None, ACTION_TOOLTIPS_STATE.DISCOUNT),
             'newPrice': (0, shopPrice),
             'oldPrice': (0, defaultPrice)}
        self.as_setParamsS({'slotPrice': (0, shopPrice),
         'freeSlots': slots - vehicles,
         'selectedTankID': selectedTankID,
         'slotPriceActionData': action})
        return

    def showVehicleStats(self, intCD):
        self.fireEvent(events.LoadEvent(events.LoadEvent.LOAD_PROFILE, {'itemCD': intCD}), scope=EVENT_BUS_SCOPE.LOBBY)

    def updateLockTimers(self):
        self.__updateVehiclesTimerId = None
        items = g_itemsCache.items
        if items.stats.globalVehicleLocks.get(CLAN_LOCK) is not None:
            vehicles = None
        else:
            vehicles = items.stats.vehicleTypeLocks.keys()
        self.updateVehicles(vehicles)
        return

# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TankCarousel.py
from operator import attrgetter
import BigWorld
import constants
from debug_utils import LOG_DEBUG
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, CAROUSEL_FILTER, SHOW_FALLOUT_VEHICLES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import AppRef
from gui.game_control import g_instance as g_gameCtrl
from gui.shared.formatters.time_formatters import getRentLeftTimeStr
from gui.shared.tooltips import ACTION_TOOLTIPS_STATE, ACTION_TOOLTIPS_TYPE
from helpers import i18n
from items.vehicles import VEHICLE_CLASS_TAGS
from gui import SystemMessages
from gui.prb_control.prb_helpers import GlobalListener
from gui.server_events import g_eventsCache
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache, REQ_CRITERIA
from gui.shared.utils import decorators
from gui.shared.gui_items import CLAN_LOCK
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, Vehicle
from gui.shared.formatters import icons
from gui.Scaleform import getVehicleTypeAssetPath
from gui.Scaleform.daapi.view.meta.TankCarouselMeta import TankCarouselMeta

class TankCarousel(TankCarouselMeta, GlobalListener, AppRef):
    UPDATE_LOCKS_PERIOD = 60
    IGR_FILTER_ID = 100

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
        filters['ready'] = bool(filters['ready'])
        showFallout = AccountSettings.getFilter(SHOW_FALLOUT_VEHICLES)
        filters['isFalloutVehicle'] = bool(showFallout)
        self.vehiclesFilter = filters
        return

    def _populate(self):
        super(TankCarousel, self)._populate()
        if self.__updateVehiclesTimerId is not None:
            BigWorld.cancelCallback(self.__updateVehiclesTimerId)
            self.__updateVehiclesTimerId = None
        g_gameCtrl.rentals.onRentChangeNotify += self._updateRent
        g_gameCtrl.igr.onIgrTypeChanged += self._updateIgrType
        self.as_setCarouselFilterS(self.vehiclesFilter)
        self.as_setIsEventS(g_eventsCache.isEventEnabled())
        return

    def _dispose(self):
        if self.__updateVehiclesTimerId is not None:
            BigWorld.cancelCallback(self.__updateVehiclesTimerId)
            self.__updateVehiclesTimerId = None
        g_gameCtrl.rentals.onRentChangeNotify -= self._updateRent
        g_gameCtrl.igr.onIgrTypeChanged -= self._updateIgrType
        super(TankCarousel, self)._dispose()
        return

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
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_SHOP), EVENT_BUS_SCOPE.LOBBY)

    def getVehicleTypeProvider(self):
        all = self.__getProviderObject('none')
        all['label'] = self.__getVehicleTypeLabel('all')
        result = [all]
        for vehicleType in VEHICLE_TYPES_ORDER:
            result.append(self.__getProviderObject(vehicleType))

        return result

    def _updateRent(self, vehicles):
        self.updateVehicles(vehicles)

    def _updateIgrType(self, *args):
        filterCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        items = g_itemsCache.items
        filteredVehs = items.getVehicles(filterCriteria)
        self.updateVehicles(filteredVehs)

    def _updateEventBattles(self, *args):
        filterCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        items = g_itemsCache.items
        filteredVehs = items.getVehicles(filterCriteria)
        self.updateVehicles(filteredVehs, updateEventBattles=False)

    def __getProviderObject(self, vehicleType):
        assetPath = {'label': self.__getVehicleTypeLabel(vehicleType),
         'data': vehicleType,
         'icon': getVehicleTypeAssetPath(vehicleType)}
        return assetPath

    def __getVehicleTypeLabel(self, vehicleType):
        return '#menu:carousel_tank_filter/' + vehicleType

    def setVehiclesFilter(self, nation, tankType, ready):
        self.vehiclesFilter['nation'] = nation
        self.vehiclesFilter['ready'] = bool(ready)
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

    def setFalloutFilter(self, falloutVehVisible):
        self.vehiclesFilter['isFalloutVehicle'] = bool(falloutVehVisible)
        AccountSettings.setFilter(SHOW_FALLOUT_VEHICLES, falloutVehVisible)
        self.showVehicles()

    def showVehicles(self):
        filterCriteria = REQ_CRITERIA.INVENTORY
        if self.vehiclesFilter['nation'] != -1:
            if self.vehiclesFilter['nation'] == 100:
                filterCriteria |= REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
            else:
                filterCriteria |= REQ_CRITERIA.NATIONS([self.vehiclesFilter['nation']])
        if self.vehiclesFilter['tankType'] != 'none':
            filterCriteria |= REQ_CRITERIA.VEHICLE.CLASSES([self.vehiclesFilter['tankType']])
        if self.vehiclesFilter['ready']:
            filterCriteria |= REQ_CRITERIA.VEHICLE.FAVORITE
        if not self.vehiclesFilter['isFalloutVehicle']:
            filterCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        items = g_itemsCache.items
        filteredVehs = items.getVehicles(filterCriteria)

        def sorting(v1, v2):
            if v1.isEvent and not v2.isEvent:
                return -1
            if not v1.isEvent and v2.isEvent:
                return 1
            if v1.isFavorite and not v2.isFavorite:
                return -1
            if not v1.isFavorite and v2.isFavorite:
                return 1
            return v1.__cmp__(v2)

        vehsCDs = map(attrgetter('intCD'), sorted(filteredVehs.values(), sorting))
        LOG_DEBUG('Showing carousel vehicles: ', vehsCDs)
        self.as_showVehiclesS(vehsCDs)

    def updateVehicles(self, vehicles = None, updateEventBattles = True):
        eventVehicles = g_eventsCache.getEventBattles().vehicles
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
                 'label': vehicle.shortUserName if vehicle.isPremiumIGR else vehicle.userName,
                 'image': vehicle.icon,
                 'nation': vehicle.nationID,
                 'level': vehicle.level,
                 'stat': vState,
                 'statStr': self.getStringStatus(vState),
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
                 'enabled': True,
                 'rentLeft': self.getRentLeftInfo(vehicle.isPremiumIGR, vehicle.rentLeftTime),
                 'groupIndicatorVisible': vehicle.intCD in eventVehicles}
                vehsData[intCD] = data

        LOG_DEBUG('Updating carousel vehicles: ', vehsData if not isSet else 'full sync')
        self.as_updateVehiclesS(vehsData, isSet)
        self.showVehicles()
        isVehTypeLock = sum((len(v) for v in items.stats.vehicleTypeLocks.itervalues()))
        isGlobalVehLock = sum((len(v) for v in items.stats.globalVehicleLocks.itervalues()))
        if self.__updateVehiclesTimerId is None and (isVehTypeLock or isGlobalVehLock):
            self.__updateVehiclesTimerId = BigWorld.callback(self.UPDATE_LOCKS_PERIOD, self.updateLockTimers)
            LOG_DEBUG('Lock timer updated')
        if updateEventBattles:
            self._updateEventBattles()
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

    def updateLockTimers(self):
        self.__updateVehiclesTimerId = None
        items = g_itemsCache.items
        if items.stats.globalVehicleLocks.get(CLAN_LOCK) is not None:
            vehicles = None
        else:
            vehicles = items.stats.vehicleTypeLocks.keys()
        self.updateVehicles(vehicles)
        return

    def getStringStatus(self, vState):
        if vState == Vehicle.VEHICLE_STATE.IN_PREMIUM_IGR_ONLY:
            icon = icons.premiumIgrSmall()
            return i18n.makeString('#menu:tankCarousel/vehicleStates/%s' % vState, icon=icon)
        return i18n.makeString('#menu:tankCarousel/vehicleStates/%s' % vState)

    def getRentLeftInfo(self, isPremIgr, rentLeftTime):
        if isPremIgr:
            return ''
        localization = '#menu:vehicle/rentLeft/%s'
        return getRentLeftTimeStr(localization, rentLeftTime)

# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TankCarousel.py
from operator import attrgetter
import BigWorld
from debug_utils import LOG_DEBUG
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import AccountSettings, CAROUSEL_FILTER, FALLOUT_CAROUSEL_FILTER
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control import g_instance as g_gameCtrl, getFalloutCtrl
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.formatters.text_styles import alert, standard, main, middleTitle, highTitle
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.tooltips import ACTION_TOOLTIPS_STATE, ACTION_TOOLTIPS_TYPE
from helpers import i18n, int2roman
from items.vehicles import VEHICLE_CLASS_TAGS
from gui import SystemMessages
from gui.prb_control.prb_helpers import GlobalListener
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache, REQ_CRITERIA
from gui.shared.utils import decorators
from gui.shared.gui_items import CLAN_LOCK
from gui.shared.gui_items.processors.vehicle import VehicleSlotBuyer
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, Vehicle
from gui.shared.formatters import icons
from gui.Scaleform import getVehicleTypeAssetPath
from gui.Scaleform.daapi.view.meta.TankCarouselMeta import TankCarouselMeta

class TankCarousel(TankCarouselMeta, GlobalListener):
    UPDATE_LOCKS_PERIOD = 60
    IGR_FILTER_ID = 100

    def __init__(self):
        super(TankCarousel, self).__init__()
        self.__updateVehiclesTimerId = None
        self.__vehiclesFilterSection = None
        self.__vehiclesFilter = None
        self.__falloutCtrl = None
        self.__multiselectionMode = False
        return

    def _populate(self):
        super(TankCarousel, self)._populate()
        if self.__updateVehiclesTimerId is not None:
            BigWorld.cancelCallback(self.__updateVehiclesTimerId)
            self.__updateVehiclesTimerId = None
        g_gameCtrl.rentals.onRentChangeNotify += self._updateRent
        g_gameCtrl.igr.onIgrTypeChanged += self._updateIgrType
        self.__falloutCtrl = getFalloutCtrl()
        self.__falloutCtrl.onVehiclesChanged += self._updateFalloutVehicles
        self.__falloutCtrl.onSettingsChanged += self._updateFalloutSettings
        self.__multiselectionMode = self.__falloutCtrl.isSelected()
        self.__setFilters()
        self.__updateMultiselectionData()
        return

    def _dispose(self):
        if self.__updateVehiclesTimerId is not None:
            BigWorld.cancelCallback(self.__updateVehiclesTimerId)
            self.__updateVehiclesTimerId = None
        g_gameCtrl.rentals.onRentChangeNotify -= self._updateRent
        g_gameCtrl.igr.onIgrTypeChanged -= self._updateIgrType
        self.__falloutCtrl.onVehiclesChanged -= self._updateFalloutVehicles
        self.__falloutCtrl.onSettingsChanged -= self._updateFalloutSettings
        self.__falloutCtrl = None
        self.__vehiclesFilter = None
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
        self.updateVehicles(filterCriteria=filterCriteria)

    def _updateFallout(self):
        filterCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.FALLOUT.SELECTED
        self.updateVehicles(filterCriteria=filterCriteria, updateFallout=False)
        self.__updateMultiselectionData()

    def _updateFalloutSettings(self, *args):
        self.__multiselectionMode = self.__falloutCtrl.isSelected()
        self.__setFilters()
        self.updateVehicles()
        self.__updateMultiselectionData()

    def _updateFalloutVehicles(self, *args):
        filterCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.FALLOUT.AVAILABLE
        self.updateVehicles(filterCriteria=filterCriteria, updateFallout=False)
        self.__updateMultiselectionData()

    def __getProviderObject(self, vehicleType):
        assetPath = {'label': self.__getVehicleTypeLabel(vehicleType),
         'data': vehicleType,
         'icon': getVehicleTypeAssetPath(vehicleType)}
        return assetPath

    def __getVehicleTypeLabel(self, vehicleType):
        return '#menu:carousel_tank_filter/' + vehicleType

    def setVehiclesFilter(self, nation, tankType, ready, gameModeFilter):
        self.__vehiclesFilter['nation'] = nation
        self.__vehiclesFilter['ready'] = ready
        self.__vehiclesFilter['tankType'] = tankType
        self.__vehiclesFilter['gameModeFilter'] = gameModeFilter
        filters = {'nation': abs(nation),
         'nationIsNegative': nation < 0,
         'ready': ready,
         'gameModeFilter': gameModeFilter}
        intTankType = -1
        for idx, type in enumerate(VEHICLE_CLASS_TAGS):
            if type == tankType:
                intTankType = idx
                break

        filters['tankTypeIsNegative'] = intTankType < 0
        filters['tankType'] = abs(intTankType)
        g_settingsCore.serverSettings.setSection(self.__vehiclesFilterSection, filters)
        self.showVehicles()

    def showVehicles(self):
        filterCriteria = REQ_CRITERIA.INVENTORY
        if self.__vehiclesFilter['nation'] != -1:
            if self.__vehiclesFilter['nation'] == 100:
                filterCriteria |= REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
            else:
                filterCriteria |= REQ_CRITERIA.NATIONS([self.__vehiclesFilter['nation']])
        if self.__vehiclesFilter['tankType'] != 'none':
            filterCriteria |= REQ_CRITERIA.VEHICLE.CLASSES([self.__vehiclesFilter['tankType']])
        if self.__vehiclesFilter['ready']:
            filterCriteria |= REQ_CRITERIA.VEHICLE.FAVORITE
        if self.__vehiclesFilter['gameModeFilter'] and self.__multiselectionMode:
            filterCriteria |= REQ_CRITERIA.VEHICLE.FALLOUT.AVAILABLE
        if not getFalloutCtrl().isSelected():
            filterCriteria |= ~REQ_CRITERIA.VEHICLE.ONLY_FOR_FALLOUT
        items = g_itemsCache.items
        filteredVehs = items.getVehicles(filterCriteria)

        def sorting(v1, v2):
            if v1.isFavorite and not v2.isFavorite:
                return -1
            if not v1.isFavorite and v2.isFavorite:
                return 1
            return v1.__cmp__(v2)

        vehsCDs = map(attrgetter('intCD'), sorted(filteredVehs.values(), sorting))
        LOG_DEBUG('Showing carousel vehicles: ', vehsCDs)
        self.as_showVehiclesS(vehsCDs)

    def updateVehicles(self, vehicles = None, filterCriteria = None, updateFallout = True):
        isSet = vehicles is None and filterCriteria is None
        filterCriteria = filterCriteria or REQ_CRITERIA.INVENTORY
        if vehicles is not None:
            filterCriteria |= REQ_CRITERIA.IN_CD_LIST(vehicles)
        items = g_itemsCache.items
        filteredVehs = items.getVehicles(filterCriteria)
        if vehicles is None:
            vehicles = filteredVehs.keys()
        isSuitablePredicate = lambda vehIntCD: True
        hasEmptySlots = self.__multiselectionMode and len(self.__falloutCtrl.getEmptySlots()) > 0
        vehsData = {}
        multiselectionsData = {}
        for intCD in vehicles:
            vehicle = filteredVehs.get(intCD)
            vehData = None
            if vehicle is not None:
                vState, vStateLvl = vehicle.getState()
                isNotSuitableVeh = vState != Vehicle.VEHICLE_STATE.BATTLE and not isSuitablePredicate(vehicle.intCD)
                isNotSuitableVeh |= self.__multiselectionMode and not vehicle.isFalloutAvailable
                isNotSuitableVeh |= vehicle.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE
                if isNotSuitableVeh:
                    vState, vStateLvl = Vehicle.VEHICLE_STATE.NOT_SUITABLE, Vehicle.VEHICLE_STATE_LEVEL.WARNING
                rentInfoStr = RentLeftFormatter(vehicle.rentInfo, vehicle.isPremiumIGR).getRentLeftStr()
                vehData = self._getVehicleData(vehicle, vState, vStateLvl, rentInfoStr)
                multiselectionsData[intCD] = self.__packMultiselectionFlags(self.__multiselectionMode and vehicle.isFalloutSelected, self.__falloutCtrl.canSelectVehicle(vehicle) and hasEmptySlots, hasEmptySlots or vehicle.isFalloutSelected)
            vehsData[intCD] = vehData

        LOG_DEBUG('Updating carousel vehicles: ', vehsData if not isSet else 'full sync')
        self.as_updateVehiclesS(vehsData, isSet)
        self.as_setMultiselectionButtonLabelsS(FALLOUT.TANKCAROUSELSLOT_ACTIVATEBUTTON, FALLOUT.TANKCAROUSELSLOT_DEACTIVATEBUTTON, self.__falloutCtrl.carouselSelectionButtonTooltip())
        self.as_updateMultiselectionDataS(multiselectionsData)
        isVehTypeLock = sum((len(v) for v in items.stats.vehicleTypeLocks.itervalues()))
        isGlobalVehLock = sum((len(v) for v in items.stats.globalVehicleLocks.itervalues()))
        if self.__updateVehiclesTimerId is None and (isVehTypeLock or isGlobalVehLock):
            self.__updateVehiclesTimerId = BigWorld.callback(self.UPDATE_LOCKS_PERIOD, self.updateLockTimers)
            LOG_DEBUG('Lock timer updated')
        if self.__multiselectionMode and updateFallout and not isSet:
            self._updateFallout()
        else:
            self.showVehicles()
        return

    def setVehicleSelected(self, vehicleInventoryId, isSelected):
        vehicleInventoryId = int(vehicleInventoryId)
        if isSelected:
            self.__falloutCtrl.addSelectedVehicle(vehicleInventoryId)
        else:
            self.__falloutCtrl.removeSelectedVehicle(vehicleInventoryId)

    def moveVehiclesSelectionSlot(self, vehicleInventoryId):
        self.__falloutCtrl.moveSelectedVehicle(int(vehicleInventoryId))

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

    def _getVehicleData(self, vehicle, vState, vStateLvl, rentInfoStr):
        return {'id': vehicle.invID,
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
         'clanLock': vehicle.clanLock,
         'elite': vehicle.isElite,
         'premium': vehicle.isPremium,
         'tankType': vehicle.type,
         'current': 0,
         'enabled': True,
         'rentLeft': rentInfoStr,
         'selectableForSlot': self.__multiselectionMode and vehicle.isFalloutAvailable and not vehicle.isDisabledInPremIGR}

    def __getMultiselectionSlots(self):
        result = []
        if not self.__multiselectionMode:
            return ()
        else:
            falloutCfg = self.__falloutCtrl.getConfig()
            selectedSlots = self.__falloutCtrl.getSelectedSlots()
            selectedSlotsNumber = len(selectedSlots)
            requiredSlots = self.__falloutCtrl.getRequiredSlots()
            mustSelectRequiredVehicle = self.__falloutCtrl.mustSelectRequiredVehicle()
            for slotIdx in range(falloutCfg.maxVehiclesPerPlayer):
                vehicle = None
                if slotIdx < selectedSlotsNumber:
                    vehicle = g_itemsCache.items.getVehicle(selectedSlots[slotIdx])
                if slotIdx in requiredSlots:
                    if mustSelectRequiredVehicle:
                        formattedStatusStr = alert(i18n.makeString(FALLOUT.MULTISELECTIONSLOT_DOMINATION_REQUIREDVEHICLENOTACTIVATED, level=int2roman(falloutCfg.vehicleLevelRequired)))
                    else:
                        formattedStatusStr = alert(FALLOUT.MULTISELECTIONSLOT_DOMINATION_VEHICLENOTACTIVATED)
                else:
                    formattedStatusStr = standard(FALLOUT.MULTISELECTIONSLOT_MULTITEAM_VEHICLENOTACTIVATED)
                data = {'indexStr': i18n.makeString(FALLOUT.MULTISELECTIONSLOT_INDEX, index=slotIdx + 1),
                 'isActivated': False,
                 'formattedStatusStr': formattedStatusStr,
                 'stateLevel': '',
                 'showAlert': slotIdx in requiredSlots,
                 'alertTooltip': TOOLTIPS.MULTISELECTION_ALERT}
                if vehicle is not None:
                    vState, vStateLvl = vehicle.getState()
                    data.update({'isActivated': True,
                     'formattedStatusStr': self.getStringStatus(vState),
                     'inventoryId': vehicle.invID,
                     'vehicleName': vehicle.shortUserName,
                     'vehicleIcon': vehicle.iconSmall,
                     'vehicleType': vehicle.type,
                     'vehicleLevel': vehicle.level,
                     'isElite': vehicle.isElite,
                     'stat': vState,
                     'stateLevel': vStateLvl,
                     'showAlert': False})
                result.append(data)

            return result

    def __getMultiselectionStatus(self):
        if self.__multiselectionMode:
            falloutCfg = self.__falloutCtrl.getConfig()
            messageTemplate = '#fallout:multiselectionSlot/%d' % self.__falloutCtrl.getBattleType()
            if not falloutCfg.hasRequiredVehicles():
                return (False, i18n.makeString(messageTemplate + '/topTierVehicleRequired', level=int2roman(falloutCfg.vehicleLevelRequired)))
            if self.__falloutCtrl.getSelectedVehicles():
                return (True, middleTitle(i18n.makeString(FALLOUT.MULTISELECTIONSLOT_SELECTIONSTATUS)) + '\n' + main(i18n.makeString(FALLOUT.MULTISELECTIONSLOT_SELECTIONREQUIREMENTS, level=toRomanRangeString(list(falloutCfg.allowedLevels), 1))))
            if falloutCfg.getAllowedVehicles():
                levels = list(falloutCfg.allowedLevels)
                topLevel = levels[-1]
                header = highTitle(i18n.makeString(messageTemplate + '/descriptionTitle', topLevel=int2roman(topLevel)))
                body = main(i18n.makeString(messageTemplate + '/message', level=toRomanRangeString(levels, 1)))
                return (False, header + '\n' + body)
        return (False, '')

    def __updateMultiselectionData(self):
        showSlots, msg = self.__getMultiselectionStatus()
        self.as_setMultiselectionModeS(self.__multiselectionMode, msg, showSlots, self.__getMultiselectionSlots())

    def __setFilters(self):
        if self.__multiselectionMode:
            self.__vehiclesFilterSection = FALLOUT_CAROUSEL_FILTER
        else:
            self.__vehiclesFilterSection = CAROUSEL_FILTER
        defaults = AccountSettings.getFilterDefault(self.__vehiclesFilterSection)
        filters = g_settingsCore.serverSettings.getSection(self.__vehiclesFilterSection, defaults)
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
        self.__vehiclesFilter = filters
        self.as_setCarouselFilterS(self.__vehiclesFilter)

    def __packMultiselectionFlags(self, selected, enabled, visible):
        value = 0
        idx = 0
        flags = (selected, enabled, visible)
        for flag in flags:
            if flag:
                value |= 1 << idx
            idx += 1

        return value

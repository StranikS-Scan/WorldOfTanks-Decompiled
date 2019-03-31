# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Inventory.py
# Compiled at: 2011-12-16 17:20:43
import BigWorld
from account_helpers.AccountSettings import AccountSettings
from adisp import process
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG, LOG_ERROR
from helpers.i18n import makeString
from gui import SystemMessages, GUI_NATIONS, GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.utils.gui_items import InventoryVehicle, VehicleItem, compactItem, getItemByCompact
from gui.Scaleform.utils.functions import makeTooltip
from gui.Scaleform.utils.requesters import Requester, VehicleItemsRequester, StatsRequester, _getComponentsByType, ITEM_TYPE_INDICES
from gui.Scaleform.windows import UIInterface
from PlayerEvents import g_playerEvents
import constants
import MusicController
import nations

class Inventory(UIInterface):

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.movie.backgroundAlpha = 0.0
        self.uiHolder.addExternalCallbacks({'inventory.populateTable': self.__onDataRequest,
         'inventory.populateMenuFilter': self.populateMenuFilter,
         'inventory.sellItem': self.__onSellItem,
         'inventory.sellVehicle': self.__onSellVehicle,
         'inventory.getVehicleSellParams': self.__onGetSellVehicleParams})
        g_playerEvents.onClientUpdated += self.update
        g_playerEvents.onShopResync += self.update
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_SHOP)
        self.populateFilters(True)
        Waiting.hide('loadPage')

    def dispossessUI(self):
        g_playerEvents.onClientUpdated -= self.update
        g_playerEvents.onShopResync -= self.update
        self.uiHolder.removeExternalCallbacks('inventory.populateTable', 'inventory.populateMenuFilter', 'inventory.sellItem', 'inventory.getVehicleSellParams', 'inventory.sellVehicle')
        UIInterface.dispossessUI(self)

    def __del__(self):
        LOG_DEBUG('InventoryHandler deleted')

    def update(self, diff={}):
        if diff.get('inventory', {}).get(1, False):
            self.populateFilters()
        params = list(AccountSettings.getFilter('inventory_current'))
        params.extend(AccountSettings.getFilter('inventory_' + params[1]))
        self.__onDataRequest(0, *params)

    @process
    def populateFilters(self, init=False):
        self.uiHolder.updateAccountInfo()
        vehicles = yield Requester('vehicle').getFromInventory()
        vehFilter = [None]
        if g_currentVehicle.isPresent():
            vehFilter = [compactItem(g_currentVehicle.vehicle)]
        vehicles.sort(reverse=True)
        for v in vehicles:
            vehFilter.append(compactItem(v))
            vehFilter.append(v.nation)
            vehFilter.append(v.name)

        if init:
            self.call('inventory.setFilter', list(AccountSettings.getFilter('inventory_current')))
        self.call('inventory.setVehicleFilter', vehFilter)
        return

    def populateMenuFilter(self, callbackId, type):
        resp = [callbackId]
        mf = AccountSettings.getFilter('inventory_' + type)
        resp.extend(mf)
        self.respond(resp)

    @process
    def __onDataRequest(self, callbackId, nation, type, *filter):
        Waiting.show('updateInventory')
        AccountSettings.setFilter('inventory_current', (nation, type))
        AccountSettings.setFilter('inventory_' + type, filter)
        nation = int(nation) if nation >= 0 else None
        if nation is not None:
            nation = nations.INDICES[GUI_NATIONS[nation]]
        filter = list(filter)
        requestType = [type]
        checkFits = None
        checkFitsArtefacts = None
        checkExtra = False
        modulesFits = {}
        vehicleFits = []
        extra = []
        modulesAllVehicle = []
        header = ''
        headerValues = {'nation': '' if nation is None else ' (%s)' % makeString('#menu:nations/' + nations.NAMES[nation])}
        if type == 'module':
            typeSize = int(filter.pop(0))
            requestType = filter[0:typeSize]
            filter = filter[typeSize:]
            fitsType = filter.pop(0)
            fitsVehicle = getItemByCompact(filter.pop(0))
            checkExtra = True
            extra = filter[:]
            checkFits = True if fitsType != 'otherVehicles' else False
            headerValues['type'] = ', '.join([ makeString('#menu:inventory/menu/module/types/' + t + '/name') for t in requestType ])
            myVehicles = yield Requester('vehicle').getFromInventory()
            modulesAllVehicle = VehicleItemsRequester(myVehicles).getItems(requestType)
            if fitsType == 'myVehicle':
                if fitsVehicle:
                    headerValues['vehicle'] = fitsVehicle.shortName
                    for rType in requestType:
                        modulesFits.update(_getComponentsByType(fitsVehicle, ITEM_TYPE_INDICES[rType]))

                else:
                    headerValues['vehicle'] = ''
            else:
                for vehicle in myVehicles:
                    for rType in requestType:
                        modulesFits.update(_getComponentsByType(vehicle, ITEM_TYPE_INDICES[rType]))

            filter = requestType
            header = makeString('#menu:inventory/header/module/' + fitsType) % headerValues
        elif type == 'shell':
            filterSize = int(filter.pop(0))
            fitsType = filter.pop(filterSize)
            fitsVehicle = getItemByCompact(filter.pop(filterSize))
            checkFits = True if fitsType != 'otherGuns' else False
            if fitsType == 'myVehicleGun':
                headerValues['vehicle'] = fitsVehicle.shortName
                for shoot in fitsVehicle.descriptor.gun['shots']:
                    modulesFits[shoot['shell']['compactDescr']] = True

            else:
                if fitsType == 'myInventoryGuns':
                    myGuns = yield Requester('vehicleGun').getFromInventory()
                    for gun in myGuns:
                        for shoot in gun.descriptor['shots']:
                            modulesFits[shoot['shell']['compactDescr']] = True

                else:
                    myGuns = yield Requester('vehicleGun').getFromInventory()
                    for gun in myGuns:
                        for shoot in gun.descriptor['shots']:
                            modulesFits[shoot['shell']['compactDescr']] = True

                myVehicles = yield Requester('vehicle').getFromInventory()
                for vehicle in myVehicles:
                    for shoot in vehicle.descriptor.gun['shots']:
                        modulesFits[shoot['shell']['compactDescr']] = True

            headerValues['type'] = ', '.join([ makeString('#menu:shop/menu/shell/kinds/' + t + '/name') for t in filter ])
            header = makeString('#menu:inventory/header/shell/' + fitsType) % headerValues
        elif type == 'vehicle':
            filterSize = int(filter.pop(0))
            extra = filter[filterSize:]
            checkExtra = True
            filter = filter[0:filterSize]
            headerValues['type'] = ', '.join([ makeString('#menu:inventory/menu/vehicle/tags/' + t + '/name') for t in filter ])
            header = makeString('#menu:inventory/header/vehicle') % headerValues
        else:
            fitsType = filter.pop(0)
            fitsVehicle = getItemByCompact(filter.pop(0))
            extra = filter
            checkExtra = type in ('optionalDevice', 'equipment')
            checkFitsArtefacts = True if fitsType != 'otherVehicles' else False
            myVehicles = yield Requester('vehicle').getFromInventory()
            modulesAllVehicle = VehicleItemsRequester(myVehicles).getItems(requestType)
            if fitsType == 'myVehicle':
                headerValues['vehicle'] = fitsVehicle.shortName
                vehicleFits = [fitsVehicle]
            else:
                vehicleFits = myVehicles
            filter = requestType
            header = makeString('#menu:inventory/header/' + type + '/' + fitsType) % headerValues
        filter = map(lambda w: w.lower(), filter)
        modulesAll = list()
        modulesShop = list()
        for rType in requestType:
            inv = yield Requester(rType).getFromInventory()
            shp = yield Requester(rType).getFromShop()
            modulesShop.extend(shp)
            modulesAll.extend(inv)

        vehPrices = {}
        if type == 'vehicle':
            compactDescrs = [ v.compactDescr for v in modulesAll ]
            vehPrices = yield StatsRequester().getVehiclesPrices(compactDescrs)
            vehPrices = dict(zip(compactDescrs, vehPrices))
        if type in ('module', 'optionalDevice', 'equipment'):
            for vehModule in modulesAllVehicle:
                if vehModule not in modulesAll:
                    if modulesShop.count(vehModule) != 0:
                        modulesAll.append(vehModule)

        value = [type, header]
        excludeModules = []
        for module in modulesAll:
            if modulesShop.count(module) != 0:
                module.priceOrder = modulesShop[modulesShop.index(module)].priceOrder
            elif constants.IS_DEVELOPMENT:
                LOG_ERROR("Not found module %s '%s' (%r) in shop." % (module.type, module.unicName, module.compactDescr))

        modulesAll.sort()
        priceModifiers = yield StatsRequester().getSellPriceModifiers()
        if priceModifiers:
            for module in modulesAll:
                if module in excludeModules:
                    continue
                if nation is not None:
                    if module.nation != nation and module.nation != nations.NONE_INDEX:
                        continue
                    if module.type.lower() not in filter:
                        continue
                    if checkFits is not None:
                        if (module.compactDescr in modulesFits.keys()) != checkFits:
                            continue
                    if checkFitsArtefacts is not None:
                        compatible = False
                        for veh in vehicleFits:
                            if nation is not None and veh.nation != nation:
                                continue
                            compatible |= module.descriptor.checkCompatibilityWithVehicle(veh.descriptor)[0]

                        if compatible != checkFitsArtefacts:
                            continue
                    inventoryCount = 0
                    vehicleCount = 0
                    installedIn = ''
                    if isinstance(module, VehicleItem):
                        vehicleCount = module.count
                        installedIn = ', '.join([ v.shortName for v in module.vehicles ])
                    else:
                        inventoryCount = module.count
                        if type in ('module', 'optionalDevice', 'equipment') and module in modulesAllVehicle:
                            vehModule = modulesAllVehicle[modulesAllVehicle.index(module)]
                            vehicleCount = vehModule.count
                            installedIn = ', '.join([ v.shortName for v in vehModule.vehicles ])
                    if checkExtra:
                        if type == 'vehicle' and 'brocken' not in extra:
                            if module.repairCost > 0:
                                continue
                        if type == 'vehicle' and 'locked' not in extra:
                            if module.lock != 0:
                                continue
                        if 'onVehicle' not in extra:
                            if vehicleCount > 0 and inventoryCount == 0:
                                continue
                    value.append(compactItem(module))
                    value.append(module.name if type in ('optionalDevice', 'equipment') else module.longName)
                    value.append(module.tableName)
                    disable = ''
                    disableTooltip = ''
                    if installedIn:
                        disableTooltip = makeString('#tooltips:inventory/listItemRenderer_installed/note', installedIn)
                    if type == 'vehicle' and module.getState() != 'crewNotFull':
                        disable = makeString('#menu:tankCarousel/vehicleStates/' + module.getState())
                    elif type in ('module', 'optionalDevice', 'equipment') and isinstance(module, VehicleItem):
                        if type == 'optionalDevice' and module.descriptor['removable'] == False:
                            disable = makeString('#menu:inventory/errors/not_removable')
                        else:
                            disable = makeString('#menu:inventory/errors/reserved')
                    tooltip_note = ('' if len(disable) != 0 else makeString('#tooltips:inventory/listItemRenderer/note') + '\n') + makeString('#tooltips:inventory/listItemRenderer_info/note')
                    value.append(makeTooltip(module.longName, disableTooltip if disableTooltip else (disable if len(disable) != 0 else None), tooltip_note))
                    value.append(inventoryCount)
                    value.append(vehicleCount)
                    if isinstance(module, InventoryVehicle):
                        sellPrice = (vehPrices.get(module.compactDescr, 0), 0)
                    else:
                        sellPrice = module.getPriceByModifiers(priceModifiers)
                    sellPrice[1] == 0 and value.append(sellPrice[0])
                    value.append('credits')
                else:
                    value.append(sellPrice[1])
                    value.append('gold')
                value.append(module.level)
                value.append(module.nation)
                value.append(module.itemTypeName if type not in ('vehicle', 'optionalDevice', 'shell', 'equipment') else module.icon)
                value.append(disable)
                value.append(module.descriptor['removable'] if type == 'optionalDevice' else True)

            self.call('table.setTable', value)
        Waiting.hide('updateInventory')
        return

    @process
    def __onGetSellVehicleParams(self, callbackID, compact):
        item = getItemByCompact(compact)
        vcls = yield Requester('vehicle').getFromInventory()
        vehicle = None
        for vcl in vcls:
            if vcl.inventoryId == item.inventoryId:
                vehicle = vcl

        isUnique = yield vehicle.isUnique()
        sellParams = yield vehicle.sellParams()
        args = [isUnique]
        args.extend(sellParams)
        self.call('inventory.sellVehicle', args)
        return

    def __onSellItem(self, callbackId, id, count):

        @process
        def sellItem(id, count):
            Waiting.show('sellItem')
            item = getItemByCompact(id)
            success = yield item.sell(count=count if count is not None else 1)
            self.uiHolder.updateAccountInfo()
            SystemMessages.pushI18nMessage(success[1], type=SystemMessages.SM_TYPE.Selling if success[0] else SystemMessages.SM_TYPE.Error)
            self.call('inventory.sellComplete', list(success))
            Waiting.hide('sellItem')
            return

        if id is not None:
            sellItem(id, count)
        return

    @process
    def __onSellVehicle(self, callbackId, id, isUnload, isDismantling):
        Waiting.show('sellItem')
        item = getItemByCompact(id)
        vcls = yield Requester('vehicle').getFromInventory()
        vehicle = None
        for vcl in vcls:
            if vcl.inventoryId == item.inventoryId:
                vehicle = vcl

        berths = yield StatsRequester().getTankmenBerthsCount()
        tankmenInBarrack = 0
        tankmen = yield Requester('tankman').getFromInventory()
        for t in tankmen:
            if not t.isInTank:
                tankmenInBarrack += 1

        currentCrew = [ t for t in vehicle.crew if t is not None ]
        if berths - tankmenInBarrack < len(currentCrew) and isUnload:
            SystemMessages.pushI18nMessage(makeString('#system_messages:fitting/vehicle_sell_barracks_full', vehicle.name), type=SystemMessages.SM_TYPE.Error)
            Waiting.hide('sellItem')
            return
        else:
            success = yield vehicle.sell(not isUnload, isDismantling)
            SystemMessages.pushI18nMessage(success[1], type=SystemMessages.SM_TYPE.Selling if success[0] else SystemMessages.SM_TYPE.Error)
            self.call('inventory.sellComplete', list(success))
            Waiting.hide('sellItem')
            return

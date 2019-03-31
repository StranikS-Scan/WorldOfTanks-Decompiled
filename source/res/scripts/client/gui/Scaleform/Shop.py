# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Shop.py
# Compiled at: 2011-11-18 02:29:27
import BigWorld
from account_helpers.AccountSettings import AccountSettings
from adisp import process
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from helpers.i18n import makeString
from gui import SystemMessages
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.utils.gui_items import compactItem, getItemByCompact, formatPrice
from gui.Scaleform.utils.functions import makeTooltip
from gui.Scaleform.utils.requesters import Requester, StatsRequester, _getComponentsByType, VehicleItemsRequester, ITEM_TYPE_INDICES
from gui.Scaleform.windows import UIInterface
import nations
from PlayerEvents import g_playerEvents
import MusicController
from items.vehicles import getDefaultAmmoForGun, parseIntCompactDescr
from items import ITEM_TYPE_INDICES

class Shop(UIInterface):

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.movie.backgroundAlpha = 0.0
        self.uiHolder.addExternalCallbacks({'shop.populateTable': self.__onDataRequest,
         'shop.populateMenuFilter': self.populateMenuFilter})
        g_playerEvents.onClientUpdated += self.update
        g_playerEvents.onShopResync += self.update
        g_playerEvents.onCenterIsLongDisconnected += self.update
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_SHOP)
        self.populateFilters(True)
        Waiting.hide('loadPage')

    def dispossessUI(self):
        g_playerEvents.onClientUpdated -= self.update
        g_playerEvents.onShopResync -= self.update
        g_playerEvents.onCenterIsLongDisconnected -= self.update
        self.uiHolder.removeExternalCallbacks('shop.populateTable', 'shop.populateMenuFilter', 'shop.buyItem', 'ShopBuyWindow.getStats')
        UIInterface.dispossessUI(self)

    def __del__(self):
        LOG_DEBUG('ShopHandler deleted')

    def update(self, diff={}):
        if diff.get('inventory', {}).get(1, False):
            self.populateFilters()
        params = list(AccountSettings.getFilter('shop_current'))
        params.extend(AccountSettings.getFilter('shop_' + params[1]))
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
            self.call('shop.setFilter', list(AccountSettings.getFilter('shop_current')))
        self.call('shop.setVehicleFilter', vehFilter)
        return

    def populateMenuFilter(self, callbackId, type):
        resp = [callbackId]
        mf = AccountSettings.getFilter('shop_' + type)
        resp.extend(mf)
        self.respond(resp)

    @process
    def __onDataRequest(self, callbackId, nation, type, *filter):
        Waiting.show('updateShop')
        AccountSettings.setFilter('shop_current', (nation, type))
        AccountSettings.setFilter('shop_' + type, filter)
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
            checkFits = True if fitsType != 'otherVehicles' else None
            headerValues['type'] = ', '.join([ makeString('#menu:shop/menu/module/types/' + t + '/name') for t in requestType ])
            myVehicles = yield Requester('vehicle').getFromInventory()
            modulesAllVehicle = VehicleItemsRequester(myVehicles).getItems(requestType)
            if fitsType == 'myVehicle':
                headerValues['vehicle'] = fitsVehicle.shortName
                for rType in requestType:
                    modulesFits.update(_getComponentsByType(fitsVehicle, ITEM_TYPE_INDICES[rType]))

            elif fitsType != 'otherVehicles':
                for vehicle in myVehicles:
                    for rType in requestType:
                        modulesFits.update(_getComponentsByType(vehicle, ITEM_TYPE_INDICES[rType]))

            filter = requestType
            header = makeString('#menu:shop/header/module/' + fitsType) % headerValues
        elif type == 'shell':
            filterSize = int(filter.pop(0))
            fitsType = filter.pop(filterSize)
            compact = filter.pop(filterSize)
            fitsVehicle = getItemByCompact(compact)
            checkFits = True if fitsType != 'otherGuns' else None
            if fitsType == 'myVehicleGun':
                headerValues['vehicle'] = fitsVehicle.shortName
                for shoot in fitsVehicle.descriptor.gun['shots']:
                    modulesFits[shoot['shell']['compactDescr']] = True

            elif fitsType == 'myInventoryGuns':
                myGuns = yield Requester('vehicleGun').getFromInventory()
                for gun in myGuns:
                    for shoot in gun.descriptor['shots']:
                        modulesFits[shoot['shell']['compactDescr']] = True

            elif fitsType != 'otherGuns':
                myGuns = yield Requester('vehicleGun').getFromInventory()
                for gun in myGuns:
                    for shoot in gun.descriptor['shots']:
                        modulesFits[shoot['shell']['compactDescr']] = True

                myVehicles = yield Requester('vehicle').getFromInventory()
                for vehicle in myVehicles:
                    for shoot in vehicle.descriptor.gun['shots']:
                        modulesFits[shoot['shell']['compactDescr']] = True

            headerValues['type'] = ', '.join([ makeString('#menu:shop/menu/shell/kinds/' + t + '/name') for t in filter ])
            header = makeString('#menu:shop/header/shell/' + fitsType) % headerValues
        elif type == 'vehicle':
            filterSize = int(filter.pop(0))
            extra = filter[filterSize:]
            checkExtra = True
            filter = filter[0:filterSize]
            headerValues['type'] = ', '.join([ makeString('#menu:shop/menu/vehicle/tags/' + t + '/name') for t in filter ])
            header = makeString('#menu:shop/header/vehicle') % headerValues
        else:
            fitsType = filter.pop(0)
            fitsVehicle = getItemByCompact(filter.pop(0))
            extra = filter
            checkExtra = type in ('optionalDevice', 'equipment')
            checkFitsArtefacts = True if fitsType != 'otherVehicles' else None
            myVehicles = yield Requester('vehicle').getFromInventory()
            modulesAllVehicle = VehicleItemsRequester(myVehicles).getItems(requestType)
            if fitsType == 'myVehicle':
                headerValues['vehicle'] = fitsVehicle.shortName
                vehicleFits = [fitsVehicle]
            elif fitsType != 'otherVehicles':
                vehicleFits = [ v for v in myVehicles if v.nation == nation ] if nation != None else myVehicles
            filter = requestType
            header = makeString('#menu:shop/header/' + type + '/' + fitsType) % headerValues
        filter = map(lambda w: w.lower(), filter)
        modulesAll = list()
        modulesAllInventory = list()
        for rType in requestType:
            inv = yield Requester(rType).getFromInventory()
            modulesAllInventory.extend(inv)
            shp = yield Requester(rType).getFromShop(nation=nation)
            modulesAll.extend(shp)

        unlocks = yield StatsRequester().getUnlocks()
        value = [type, header]
        modulesAll.sort()
        for module in modulesAll:
            if module.hidden:
                continue
            if module.type.lower() not in filter:
                continue
            if checkFits is not None:
                if (module.compactDescr in modulesFits.keys()) != checkFits:
                    continue
            if checkFitsArtefacts is not None:
                for veh in vehicleFits:
                    if module.descriptor.checkCompatibilityWithVehicle(veh.descriptor)[0] == checkFitsArtefacts:
                        break
                else:
                    continue

            inventoryCount = 0
            vehicleCount = 0
            installedIn = ''
            if module in modulesAllInventory:
                inventoryCount = 1
                if type != 'vehicle':
                    inventoryModule = modulesAllInventory[modulesAllInventory.index(module)]
                    inventoryCount = inventoryModule.count
            if type in ('module', 'optionalDevice', 'equipment') and module in modulesAllVehicle:
                vehModule = modulesAllVehicle[modulesAllVehicle.index(module)]
                vehicleCount = vehModule.count
                installedIn = ', '.join([ v.shortName for v in vehModule.vehicles ])
            if checkExtra:
                if 'locked' not in extra:
                    if type == 'vehicle':
                        compdecs = module.descriptor.type.compactDescr
                        if compdecs not in unlocks:
                            continue
                    elif type not in ('shell', 'optionalDevice', 'equipment') and module.compactDescr not in unlocks:
                        continue
                if 'inHangar' not in extra and type not in ('optionalDevice', 'equipment'):
                    if inventoryCount > 0:
                        continue
                if 'onVehicle' not in extra:
                    if vehicleCount > 0:
                        continue
            value.append(compactItem(module))
            value.append(module.name if type in ('optionalDevice', 'equipment') else module.longName)
            value.append(module.tableName)
            disabled = ''
            disableTooltip = ''
            if installedIn:
                disableTooltip = makeString('#tooltips:inventory/listItemRenderer_installed/note', installedIn)
            if type == 'vehicle':
                if BigWorld.player().isLongDisconnectedFromCenter:
                    disabled = '#menu:shop/errors/centerIsDown'
                if inventoryCount > 0:
                    disabled = '#menu:shop/errors/inHangar'
                else:
                    compdecs = module.descriptor.type.compactDescr
                    if compdecs not in unlocks:
                        disabled = '#menu:shop/errors/unlockNeeded'
            elif type not in ('shell', 'optionalDevice', 'equipment') and module.compactDescr not in unlocks:
                disabled = '#menu:shop/errors/unlockNeeded'
            tooltip_note = ('' if len(disabled) != 0 else makeString('#tooltips:shop/listItemRenderer/note') + '\n') + makeString('#tooltips:shop/listItemRenderer_info/note')
            value.append(makeTooltip(module.longName, disableTooltip if disableTooltip else (disabled if len(disabled) != 0 else None), tooltip_note))
            value.append(inventoryCount)
            value.append(vehicleCount)
            if module.priceOrder[1] == 0:
                value.append(module.priceOrder[0])
                value.append('credits')
            else:
                value.append(module.priceOrder[1])
                value.append('gold')
            value.append(module.level)
            value.append(module.nation)
            value.append(module.itemTypeName if type not in ('vehicle', 'optionalDevice', 'shell', 'equipment') else module.icon)
            value.append(disabled)
            value.append(module.descriptor['removable'] if type == 'optionalDevice' else True)

        self.call('table.setTable', value)
        Waiting.hide('updateShop')
        return

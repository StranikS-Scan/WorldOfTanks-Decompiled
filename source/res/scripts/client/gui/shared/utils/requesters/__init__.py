# Embedded file name: scripts/client/gui/shared/utils/requesters/__init__.py
import weakref
from functools import partial
import BigWorld
import nations
import constants
import dossiers2
import AccountCommands
from adisp import async, process
from items import tankmen, vehicles, ITEM_TYPE_NAMES, ITEM_TYPE_INDICES
from debug_utils import *
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.gui_items import InventoryItem, ShopItem, InventoryVehicle, InventoryTankman, VehicleItem
from helpers import isPlayerAccount
from gui.shared.utils import ParametersCache
from gui.shared.utils.requesters.ItemsRequester import ItemsRequester, REQ_CRITERIA
from gui.shared.utils.requesters.ItemsRequester import ItemsRequester, StatsRequesterr, ShopRequester, InventoryRequester, DossierRequester
_ARTEFACTS_ITEMS = (ITEM_TYPE_INDICES['optionalDevice'], ITEM_TYPE_INDICES['equipment'])
_TANKMAN = ITEM_TYPE_INDICES['tankman']
__all__ = ['ItemsRequester',
 'code2str',
 'InventoryParser',
 'ShopParser',
 'Requester',
 'getComponentsByType',
 '_getComponentsByType',
 'AvailableItemsRequester',
 'StatsRequester',
 'VehicleItemsRequester',
 'StatsRequesterr',
 'ShopRequester',
 'InventoryRequester',
 'DossierRequester']
_SAFE_SERVER_ERROR_CODES = (AccountCommands.RES_NOT_AVAILABLE,)

class ShopDataParser(object):

    def __init__(self, data = None):

        def wrapper(method):
            obj = weakref.proxy(self)

            def caller(*args):
                return getattr(obj, method)(*args)

            return caller

        self.__modulesGetters = {GUI_ITEM_TYPE.VEHICLE: vehicles.g_list.getList,
         GUI_ITEM_TYPE.CHASSIS: vehicles.g_cache.chassis,
         GUI_ITEM_TYPE.ENGINE: vehicles.g_cache.engines,
         GUI_ITEM_TYPE.RADIO: vehicles.g_cache.radios,
         GUI_ITEM_TYPE.TURRET: vehicles.g_cache.turrets,
         GUI_ITEM_TYPE.GUN: vehicles.g_cache.guns,
         GUI_ITEM_TYPE.SHELL: vehicles.g_cache.shells,
         GUI_ITEM_TYPE.EQUIPMENT: wrapper('getEquipments'),
         GUI_ITEM_TYPE.OPTIONALDEVICE: wrapper('getOptionalDevices')}
        self.data = data or {}

    def __del__(self):
        self.__modulesGetters.clear()
        self.__modulesGetters = None
        return

    def getEquipments(self, nationID):
        allEquipments = vehicles.g_cache.equipments()
        return self.__filterByNation(allEquipments, ParametersCache.g_instance.getEquipmentParameters, nationID)

    def getOptionalDevices(self, nationID):
        allOptDevices = vehicles.g_cache.optionalDevices()
        return self.__filterByNation(allOptDevices, ParametersCache.g_instance.getOptionalDeviceParameters, nationID)

    def getItemsIterator(self, nationID = None, itemTypeID = None):
        hiddenInShop = self.data.get('notInShopItems', [])
        sellForGold = self.data.get('vehiclesToSellForGold', [])
        prices = self.getPrices()
        for intCD in self.__getListOfCompDescrs(nationID, itemTypeID):
            if intCD in prices:
                yield (intCD,
                 prices[intCD],
                 intCD in hiddenInShop,
                 intCD in sellForGold)

    def getPrices(self):
        return self.data.get('itemPrices', {})

    def getHiddenItems(self, nationID = None):
        hiddenItems = self.data.get('notInShopItems', set([]))
        result = set([])
        for intCD in self.__getListOfCompDescrs(nationID):
            if intCD in hiddenItems:
                result.add(intCD)

        return result

    def getSellForGoldItems(self):
        return self.data.get('vehiclesToSellForGold', set([]))

    def getPrice(self, intCD):
        return self.getPrices().get(intCD, (0, 0))

    def isHidden(self, intCD):
        return intCD in self.getHiddenItems()

    def isSellForGold(self, intCD):
        return intCD in self.getSellForGoldItems()

    def __getListOfCompDescrs(self, nationID = None, itemTypeID = None):
        itemTypes = [itemTypeID]
        if itemTypeID is None:
            itemTypes = self.__modulesGetters.keys()
        itemNations = [nationID]
        if nationID is None:
            itemNations = nations.INDICES.values()
        result = set()
        for nIdx in itemNations:
            for typeIdx in itemTypes:
                if typeIdx in self.__modulesGetters:
                    getter = self.__modulesGetters[typeIdx]
                    result |= set((v['compactDescr'] for v in getter(nIdx).itervalues()))

        return result

    def __filterByNation(self, items, getParameters, nationID):
        if nationID == nations.NONE_INDEX or nationID is None:
            return items
        else:
            result = {}
            for key, value in items.iteritems():
                params = getParameters(value)
                if nationID in params['nations']:
                    result[key] = value

            return result


class Parser(object):

    @staticmethod
    def parseVehicles(data):
        return data

    @staticmethod
    def parseModules(data, type):
        return data

    @staticmethod
    def getParser(itemTypeID):
        if itemTypeID == 1:
            return Parser.parseVehicles
        return lambda data: Parser.parseModules(data, itemTypeID)


class InventoryParser(Parser):

    @staticmethod
    def parseVehicles(data):
        if data is None:
            return []
        else:
            vehicles = []
            for id, vehCompDescr in data.get('compDescr', {}).items():
                descriptor = vehCompDescr
                ammoLayout = dict(data['shellsLayout'].get(id, {}))
                shells = list(data['shells'].get(id, []))
                crew = list(data['crew'].get(id, []))
                repairCost, health = data['repair'].get(id, (0, 0))
                equipmentsLayout = data['eqsLayout'].get(id, [0, 0, 0])
                equipments = data['eqs'].get(id, [0, 0, 0])
                if not equipments:
                    equipments = [0, 0, 0]
                settings = data['settings'].get(id, 0)
                lock = data['lock'].get(id, 0)
                vehicles.append(InventoryVehicle(compactDescr=descriptor, id=id, crew=crew, shells=shells, ammoLayout=ammoLayout, repairCost=repairCost, health=health, lock=lock, equipments=equipments, equipmentsLayout=equipmentsLayout, settings=settings))

            return vehicles

    @staticmethod
    def parseTankmen(data):
        if data is None:
            return []
        else:
            tankmen = []
            for id, compDescr in data.get('compDescr', {}).items():
                descriptor = compDescr
                vehicleID = data['vehicle'].get(id, -1)
                tankmen.append(InventoryTankman(compactDescr=descriptor, id=id, vehicleID=vehicleID))

            return tankmen

    @staticmethod
    def parseModules(data, itemTypeID):
        if data is None:
            return []
        else:
            modules = []
            for descriptor, count in data.items():
                modules.append(InventoryItem(itemTypeName=ITEM_TYPE_NAMES[itemTypeID], compactDescr=descriptor, count=count))

            return modules

    @staticmethod
    def getParser(itemTypeID):
        if itemTypeID == 1:
            return InventoryParser.parseVehicles
        if itemTypeID == 8:
            return InventoryParser.parseTankmen
        return lambda data: InventoryParser.parseModules(data, itemTypeID)


class ShopParser(Parser):

    @staticmethod
    def parseVehicles(data, nationId):
        if data is None or not len(data):
            return []
        else:
            result = []
            parser = ShopDataParser(data)
            for intCD, price, isHidden, sellForGold in parser.getItemsIterator(nationId, GUI_ITEM_TYPE.VEHICLE):
                _, _, innationID = vehicles.parseIntCompactDescr(intCD)
                result.append(ShopItem(itemTypeName=ITEM_TYPE_NAMES[GUI_ITEM_TYPE.VEHICLE], compactDescr=innationID, priceOrder=price, nation=nationId, hidden=isHidden))

            return result

    @staticmethod
    def parseModules(data, itemTypeID, nationId):
        if data is None or not len(data):
            return []
        else:
            modules = []
            parser = ShopDataParser(data)
            for intCD, price, isHidden, sellForGold in parser.getItemsIterator(nationId, itemTypeID):
                modules.append(ShopItem(itemTypeName=ITEM_TYPE_NAMES[itemTypeID], compactDescr=intCD, priceOrder=price, nation=nationId, hidden=isHidden))

            return modules

    @staticmethod
    def getParser(itemTypeID):
        if itemTypeID == 1:
            return ShopParser.parseVehicles
        return lambda data, nationId: ShopParser.parseModules(data, itemTypeID, nationId)


class Requester(object):
    """
    Async requester of items @see: helpers.Scaleform.utils.items
    @param itemTypeName: item type to request @see: items.ITEM_TYPE_NAMES
    
    Example of usage:
    #Dont forget annotate function @process
    @process
    def updateGuns():
            #make request to inventory
            inventoryGuns = yield Requester('vehicleGun').getFromInventory()
            #continue after request complete
            #do somthing with guns list [InventoryItem, InventoryItem, ...]
    
            #make request to shop
            guns = yield Requester('vehicleGun').getFromShop()
            #continue after request complete
            #do somthing with guns list [ShopItem, ShopItem, ...]
    """
    PARSERS = {'inventory': InventoryParser,
     'shop': ShopParser}

    def __init__(self, itemTypeName):
        self._itemTypeId = ITEM_TYPE_INDICES[itemTypeName]
        self._callback = None
        self._requestsCount = 0
        self._responsesCount = 0
        self._response = []
        return

    @async
    def getAllPossible(self, callback):
        """
        Make request to inventory and shop
        return InventoryItems and ShopItems
        
        Example of usage:
        @process
        def updateGuns():
                guns = yield Requester('vehicleGun').getAllPossible()
                #continue after request complete
                #do somthing with guns list [InventoryItem, InventoryItem, ShopItem, ...]
        """
        self._callback = callback
        self._requestsCount = count(nations.INDICES) + 1
        self._requestInventory()
        for nationId in nations.INDICES.values():
            self._requestShop(nationId)

    @async
    def getFromInventory(self, callback):
        """
        Make request to inventory
        
        Example of usage:
        @process
        def updateGuns():
                guns = yield Requester('vehicleGun').getFromInventory()
                #continue after request complete
                #do somthing with guns list [InventoryItem, InventoryItem, ...]
        """
        self._callback = callback
        self._requestsCount = 1
        self._requestInventory()

    @async
    def getFromShop(self, callback, nation = None):
        """
        Make request to shop
        
        Example of usage:
        @process
        def updateGuns():
                guns = yield Requester('vehicleGun').getFromShop()
                #continue after request complete
                #do somthing with guns list [ShopItem, ShopItem, ...]
        """
        self._callback = callback
        if self._itemTypeId in _ARTEFACTS_ITEMS:
            self._requestsCount = 1
            self._requestShop(nation)
        elif nation is not None:
            self._requestsCount = 1
            self._requestShop(nation)
        else:
            self._requestsCount = len(nations.INDICES)
            for nationId in nations.INDICES.values():
                self._requestShop(nationId)

        return

    def _requestInventory(self):
        raise hasattr(BigWorld.player(), 'inventory') or AssertionError('Request from inventory is not possible')
        BigWorld.player().inventory.getItems(self._itemTypeId, self.__parseInventoryResponse)

    def __parseInventoryResponse(self, responseCode, data):
        listData = []
        if responseCode >= 0:
            listData = Requester.PARSERS['inventory'].getParser(self._itemTypeId)(data)
        else:
            LOG_ERROR('Server return error for inventory getItems request: responseCode=%s, itemTypeId=%s.' % (responseCode, self._itemTypeId))
        self._collectResponse(listData, 'inventory')

    def _requestShop(self, nationId):
        raise hasattr(BigWorld.player(), 'shop') or AssertionError('Request from shop is not possible')
        BigWorld.player().shop.getAllItems(lambda res, data, rev: self.__parseShopResponse(res, data, nationId))

    def __parseShopResponse(self, responseCode, data, nationId):
        listData = []
        if responseCode >= 0:
            listData = Requester.PARSERS['shop'].getParser(self._itemTypeId)(data, nationId)
        else:
            LOG_ERROR('Server return error for shop getItems request: responseCode=%s, itemTypeId=%s, nationId=%s, data=%s.' % (responseCode,
             self._itemTypeId,
             nationId,
             data))
        self._collectResponse(listData, 'shop')

    def _collectResponse(self, response, requestType):
        self._responsesCount += 1
        self._response.extend(response)
        if self._responsesCount == self._requestsCount:
            if self._callback is not None:
                self._callback(self._response)
        return


def getComponentsByType(vehDescr, itemTypeId, turretPID = 0):
    """
    Return list suitable modules for vehicle foloving structure:
    {
            compactDescriptor: (isCurrent, isDefault),
            ...
    }
    """
    descriptorsList = []
    current = []
    if itemTypeId == vehicles._CHASSIS:
        current = [vehDescr.chassis['compactDescr']]
        descriptorsList = vehDescr.type.chassis
    elif itemTypeId == vehicles._ENGINE:
        current = [vehDescr.engine['compactDescr']]
        descriptorsList = vehDescr.type.engines
    elif itemTypeId == vehicles._RADIO:
        current = [vehDescr.radio['compactDescr']]
        descriptorsList = vehDescr.type.radios
    elif itemTypeId == vehicles._FUEL_TANK:
        current = [vehDescr.fuelTank['compactDescr']]
        descriptorsList = vehDescr.type.fuelTanks
    elif itemTypeId == vehicles._TURRET:
        current = [vehDescr.turret['compactDescr']]
        descriptorsList = vehDescr.type.turrets[turretPID]
    elif itemTypeId == vehicles._OPTIONALDEVICE:
        descriptorsList = vehDescr.optionalDevices
    elif itemTypeId == vehicles._GUN:
        current = [vehDescr.gun['compactDescr']]
        for gun in vehDescr.turret['guns']:
            descriptorsList.append(gun)

        for turret in vehDescr.type.turrets[turretPID]:
            if turret is not vehDescr.turret:
                for gun in turret['guns']:
                    descriptorsList.append(gun)

    elif itemTypeId == vehicles._SHELL:
        for shot in vehDescr.gun['shots']:
            current.append(shot['shell']['compactDescr'])

        for gun in vehDescr.turret['guns']:
            for shot in gun['shots']:
                descriptorsList.append(shot['shell'])

        for turret in vehDescr.type.turrets[turretPID]:
            if turret is not vehDescr.turret:
                for gun in turret['guns']:
                    for shot in gun['shots']:
                        descriptorsList.append(shot['shell'])

    return (descriptorsList, current)


def _getComponentsByType(vehicle, itemTypeId, turretPID = 0):
    components = dict()
    descriptorsList, current = getComponentsByType(vehicle.descriptor, itemTypeId, turretPID)
    if itemTypeId == vehicles._EQUIPMENT:
        descriptorsList = [ (e.descriptor if e is not None else None) for e in vehicle.eqs ]
    if itemTypeId == vehicles._OPTIONALDEVICE:
        for index, item in enumerate(descriptorsList):
            if item:
                components[item['compactDescr']] = index

    elif itemTypeId == vehicles._EQUIPMENT:
        for index, item in enumerate(descriptorsList):
            if item:
                components[item] = index

    else:
        for item in descriptorsList:
            key = item['compactDescr']
            if key not in components:
                components[key] = item['compactDescr'] in current

    return components


class AvailableItemsRequester(Requester):

    def __init__(self, vehicle, itemTypeName):
        raise vehicle is not None or AssertionError
        Requester.__init__(self, itemTypeName)
        self._vehicle = vehicle
        return

    @async
    def request(self, callback):
        self._callback = callback
        self._requestsCount = 2
        self._requestInventory()
        if self._itemTypeId in _ARTEFACTS_ITEMS:
            self._requestShop(nations.NONE_INDEX)
        else:
            nationId, vehicleTypeId = self._vehicle.descriptor.type.id
            self._requestShop(nationId)

    def _collectResponse(self, response, requestType):
        self._responsesCount += 1
        if requestType == 'shop':
            for item1 in response:
                isIn = False
                for item2 in self._response:
                    if item1 == item2:
                        item2.priceOrder = item1.priceOrder
                        isIn = True
                        break

                if not isIn:
                    self._response.append(item1)

        else:
            for item1 in response:
                for item2 in self._response:
                    if item1 == item2:
                        item1.priceOrder = item2.priceOrder
                        self._response.remove(item2)
                        break

                self._response.append(item1)

        if self._responsesCount == self._requestsCount:
            values = []
            components = _getComponentsByType(self._vehicle, self._itemTypeId)
            descriptors = components.keys()
            for item in self._response:
                if self._itemTypeId not in _ARTEFACTS_ITEMS:
                    if item.compactDescr not in descriptors:
                        continue
                elif not item.descriptor.checkCompatibilityWithVehicle(self._vehicle.descriptor)[0]:
                    continue
                isCurrentOrIndex = components.get(item.compactDescr, False)
                isCurrent = isCurrentOrIndex if isinstance(isCurrentOrIndex, bool) else True
                if isCurrent and isinstance(item, ShopItem):
                    item = InventoryItem(itemTypeName=item.itemTypeName, compactDescr=item.compactDescr, priceOrder=item.priceOrder, count=1)
                item.isCurrent = isCurrent
                if not isinstance(isCurrentOrIndex, bool):
                    item.index = isCurrentOrIndex
                values.append(item)

            if self._callback is not None:
                self._callback(values)
        return


def responseIfNotAccount(*dargs, **dkwargs):

    def decorate(fn):

        def checkAccount(*fargs, **fkwargs):
            if not isPlayerAccount():
                LOG_NOTE('Server call "StatsRequester.%s" canceled: player is not account.' % fn.func_name)
                returnFurnc = dkwargs.get('func', None)
                if returnFurnc:
                    returnArgs = dkwargs.get('args', None)
                    if returnArgs:
                        return fkwargs['callback'](returnFurnc(returnArgs))
                    return fkwargs['callback'](returnFurnc())
                return fkwargs['callback'](*dargs, **dkwargs)
            else:
                fargs[0].setCallback(fkwargs['callback'])
                return fn(*fargs, **fkwargs)

        return checkAccount

    return decorate


class StatsRequester(object):

    def __init__(self):
        self.__callback = None
        return

    def setCallback(self, callback):
        self.__callback = callback

    @async
    @process
    def getClanEmblemTextureID(self, clanDBID, isBig, textureID, callback):
        import imghdr
        if clanDBID is not None and clanDBID != 0:
            clanEmblemUrl, clanEmblemFile = yield self.getFileFromServer(clanDBID, 'clan_emblems_small' if not isBig else 'clan_emblems_big')
            if clanEmblemFile and imghdr.what(None, clanEmblemFile) is not None:
                BigWorld.wg_addTempScaleformTexture(textureID, clanEmblemFile)
                callback(True)
                return
        callback(False)
        return

    @async
    @responseIfNotAccount(set())
    def getMultipliedXPVehicles(self, callback):
        BigWorld.player().stats.get('multipliedXPVehs', self.__valueResponse)

    @async
    @responseIfNotAccount(func=dossiers2.getAccountDossierDescr, args=('',))
    def getAccountDossier(self, callback):
        BigWorld.player().stats.get('dossier', self.__accountDossierResponse)

    @async
    @responseIfNotAccount(func=dossiers2.getVehicleDossierDescr, args=('',))
    def getVehicleDossier(self, vehTypeCompDescr, callback):
        BigWorld.player().dossierCache.get(constants.DOSSIER_TYPE.VEHICLE, vehTypeCompDescr, self.__vehicleDossierResponse)

    @async
    @responseIfNotAccount(func=dossiers2.getTankmanDossierDescr, args=('',))
    def getTankmanDossier(self, tankmanID, callback):
        BigWorld.player().inventory.getItems(_TANKMAN, partial(self.__tankmanDossierResponse, tankmanID))

    @async
    @responseIfNotAccount(0)
    def getCredits(self, callback):
        BigWorld.player().stats.get('credits', self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def getFreeXPToTManXPRate(self, callback):
        BigWorld.player().shop.getFreeXPToTManXPRate(self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def freeXPToTankman(self, tankmanId, freeXp, callback):
        BigWorld.player().inventory.freeXPToTankman(tankmanId, freeXp, lambda eStr, code: self.__callback((code >= 0, eStr)))

    @async
    @responseIfNotAccount(False)
    def isTeamKiller(self, callback):
        BigWorld.player().stats.get('tkillIsSuspected', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getRestrictions(self, callback):
        BigWorld.player().stats.get('restrictions', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getDenunciations(self, callback):
        BigWorld.player().stats.get('denunciationsLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getGold(self, callback):
        BigWorld.player().stats.get('gold', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getVehicleTypeExperiences(self, callback):
        BigWorld.player().stats.get('vehTypeXP', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getFreeExperience(self, callback):
        BigWorld.player().stats.get('freeXP', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getVehicleTypeLocks(self, callback):
        BigWorld.player().stats.get('vehTypeLocks', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getGlobalVehicleLocks(self, callback):
        BigWorld.player().stats.get('globalVehicleLocks', self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def exchange(self, gold, callback):
        BigWorld.player().stats.exchange(gold, self.__response)

    @async
    @responseIfNotAccount(0)
    def getAmmoSellPrice(self, ammo, callback):
        BigWorld.player().shop.getAmmoSellPrice(ammo, self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def getDailyXPFactor(self, callback):
        BigWorld.player().shop.getDailyXPFactor(self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def convertVehiclesXP(self, xp, vehTypeDescrs, callback):
        BigWorld.player().stats.convertToFreeXP(vehTypeDescrs, xp, self.__response)

    @async
    @responseIfNotAccount(set())
    def getUnlocks(self, callback):
        BigWorld.player().stats.get('unlocks', self.__valueResponse)

    @async
    @responseIfNotAccount(set())
    def getEliteVehicles(self, callback):
        BigWorld.player().stats.get('eliteVehicles', self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def upgradeToPremium(self, days, callback):
        BigWorld.player().stats.upgradeToPremium(days, self.__response)

    @async
    @responseIfNotAccount(False)
    def buySlot(self, callback):
        BigWorld.player().stats.buySlot(self.__response)

    @async
    @responseIfNotAccount(0)
    def getSlotsCount(self, callback):
        BigWorld.player().stats.get('slots', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getTankmenBerthsCount(self, callback):
        BigWorld.player().stats.get('berths', self.__valueResponse)

    @async
    @responseIfNotAccount([0, [0]])
    def getSlotsPrices(self, callback):
        BigWorld.player().shop.getSlotsPrices(self.__valueResponse)

    @async
    @responseIfNotAccount(dict())
    def getSteamGoldPackets(self, callback):
        BigWorld.player().shop.getGoldPackets(self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getPaidRemovalCost(self, callback):
        BigWorld.player().shop.getPaidRemovalCost(self.__valueResponse)

    @async
    @responseIfNotAccount([0, 1, [0]])
    def getBerthsPrices(self, callback):
        BigWorld.player().shop.getBerthsPrices(self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def buyBerths(self, callback):
        BigWorld.player().stats.buyBerths(self.__response)

    @async
    @responseIfNotAccount(tuple())
    def getTankmanCost(self, callback):
        BigWorld.player().shop.getTankmanCost(self.__valueResponse)

    @async
    @responseIfNotAccount(tuple())
    def getDropSkillsCost(self, callback):
        BigWorld.player().shop.getDropSkillsCost(self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getPassportChangeCost(self, callback):
        BigWorld.player().shop.getPassportChangeCost(self.__valueResponse)

    @async
    @responseIfNotAccount((0, 0))
    def getShellPrice(self, nationIdx, shellCompactDescr, callback):
        BigWorld.player().shop.getPrice(ITEM_TYPE_INDICES['shell'], nationIdx, shellCompactDescr, self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def getSellPriceModifiers(self, compDescr, callback):
        BigWorld.player().shop.getSellPriceModifiers(compDescr, self.__valueResponse)

    @async
    @responseIfNotAccount(1)
    def getExchangeRate(self, callback):
        BigWorld.player().shop.getExchangeRate(self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getFreeXPConversion(self, callback):
        BigWorld.player().shop.getFreeXPConversion(self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getPremiumCost(self, callback):
        BigWorld.player().shop.getPremiumCost(self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getAccountAttrs(self, callback):
        BigWorld.player().stats.get('attrs', self.__valueResponse)

    @async
    @responseIfNotAccount(0)
    def getPremiumExpiryTime(self, callback):
        BigWorld.player().stats.get('premiumExpiryTime', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getClanInfo(self, callback):
        BigWorld.player().stats.get('clanInfo', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getClanDBID(self, callback):
        BigWorld.player().stats.get('clanDBID', self.__valueResponse)

    @async
    @responseIfNotAccount((0, ''))
    def ebankGetBalance(self, callback):
        BigWorld.player().ebankGetBalance(lambda code, errStr, props: self.__callback((props.get('vcoinBalance', 0), errStr)))

    @async
    @responseIfNotAccount((0, ''))
    def ebankBuyGold(self, vcoin, callback):
        BigWorld.player().ebankBuyGold(vcoin, lambda code, errStr, props: self.__callback((code >= 0, errStr)))

    @async
    @responseIfNotAccount(1)
    def ebankGetExchangeRate(self, callback):
        BigWorld.player().shop.ebankVCoinExchangeRate(self.__valueResponse)

    @async
    @responseIfNotAccount(dict())
    def setAndFillLayouts(self, vehInvID, shellsLayout, eqsLayout, callback):
        BigWorld.player().inventory.setAndFillLayouts(vehInvID, shellsLayout, eqsLayout, lambda resID, errStr, value: self.__callback((resID, errStr, value)))

    @async
    @responseIfNotAccount(50)
    def ebankGetMinTransactionValue(self, callback):
        BigWorld.player().shop.ebankMinTransactionValue(self.__valueResponse)

    @async
    @responseIfNotAccount(500000)
    def ebankGetMaxTransactionValue(self, callback):
        BigWorld.player().shop.ebankMaxTransactionValue(self.__valueResponse)

    @async
    @responseIfNotAccount(dict())
    def getBattleResults(self, arenaUniqueID, callback):
        BigWorld.player().battleResultsCache.get(arenaUniqueID, self.__valueResponse)

    @async
    @responseIfNotAccount((None, None))
    def getFileFromServer(self, clanId, fileType, callback):
        if not BigWorld.player().serverSettings['file_server'].has_key(fileType):
            LOG_ERROR("Invalid server's file type: %s" % fileType)
            self.__valueResponse(0, (None, None))
            return None
        else:
            clan_emblems = BigWorld.player().serverSettings['file_server'][fileType]
            BigWorld.player().customFilesCache.get(clan_emblems['url_template'] % clanId, lambda url, file: self.__valueResponse(0, (url, file)), True)
            return None

    @async
    @responseIfNotAccount(None)
    def getUserClanInfo(self, userName, callback):
        BigWorld.player().requestPlayerClanInfo(userName, lambda resultID, str, clanDBID, clanInfo: self.__valueResponse(resultID, (clanDBID, clanInfo)))

    @async
    @responseIfNotAccount(False)
    def hasFinPassword(self, callback):
        BigWorld.player().stats.get('hasFinPassword', self.__valueResponse)

    @async
    @responseIfNotAccount({})
    def getVehiclesPrices(self, vehicles, callback):
        BigWorld.player().shop.getVehiclesSellPrices(vehicles, self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getFreeVehicleLeft(self, callback):
        BigWorld.player().stats.get('freeVehiclesLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getVehicleSellsLeft(self, callback):
        BigWorld.player().stats.get('vehicleSellsLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(None)
    def getFreeTankmanLeft(self, callback):
        BigWorld.player().stats.get('freeTMenLeft', self.__valueResponse)

    @async
    @responseIfNotAccount(False)
    def setEquipments(self, vehInvId, equipments, callback):
        BigWorld.player().inventory.equipEquipments(vehInvId, equipments, self.__response)

    @async
    @responseIfNotAccount({})
    def getTradeFees(self, callback):
        raise hasattr(BigWorld.player(), 'shop') or AssertionError('Request from shop is not possible')
        self.__callback = callback
        BigWorld.player().shop.getTradeFees(self.__valueResponse)

    def __accountDossierResponse(self, responseCode, dossierCompDescr = ''):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat account dossier request: responseCode=%s' % responseCode)
            return
        if self.__callback:
            dossierDescr = dossiers2.getAccountDossierDescr(dossierCompDescr)
            self.__callback(dossierDescr)

    def __vehicleDossierResponse(self, responseCode, vehTypeDossiers = ''):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat account dossier request: responseCode=%s' % responseCode)
            return
        else:
            if self.__callback:
                if vehTypeDossiers is not None:
                    self.__callback(dossiers2.getVehicleDossierDescr(vehTypeDossiers))
                self.__callback(dossiers2.getVehicleDossierDescr(''))
            return

    def __tankmanDossierResponse(self, tankmanID, resultID, data):
        if resultID < 0:
            LOG_ERROR('Server return error for inventory tankman dossier request: responseCode=%s' % resultID)
            return
        else:
            if self.__callback and data is not None:
                dossier = ''
                tankman = data.get('compDescr', None)
                if tankman is not None:
                    tmenCompDescr = tankman.get(tankmanID, None)
                    if tmenCompDescr is not None:
                        dossier = tankmen.TankmanDescr(tmenCompDescr).dossierCompactDescr
                self.__callback(dossiers2.getTankmanDossierDescr(dossier))
            return

    def _valueResponse(self, responseCode, value = None, revision = 0):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s' % responseCode)
            self.__dumpStack()
        elif self.__callback:
            self.__callback(value)

    def __valueResponse(self, responseCode, value = None, revision = 0):
        if responseCode < 0:
            if responseCode not in _SAFE_SERVER_ERROR_CODES:
                LOG_ERROR('Server return error for stat request: responseCode=%s' % responseCode)
                self.__dumpStack()
            else:
                LOG_WARNING('Server return error for stat request: responseCode=%s' % responseCode)
        if self.__callback:
            self.__callback(value)

    def __response(self, responseCode):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s.' % responseCode)
            self.__dumpStack()
        if self.__callback:
            self.__callback(responseCode >= 0)

    def __dumpStack(self):
        import inspect
        dump = 'frames stack dumping --------------'
        for frame, file, line, method, _, _ in inspect.stack():
            dump = '%s\n (%s, %d): %s' % (dump,
             str(file),
             line,
             str(method))

        LOG_ERROR(dump)


class VehicleItemsRequester(object):

    def __init__(self, vehicles):
        self.__vehicles = vehicles

    def getItems(self, types):
        items = {}
        for v in self.__vehicles:
            for type in types:
                currents = self.__getItemsByType(v, type)
                for current in currents:
                    if current:
                        current = items.setdefault(current, VehicleItem(compactDescr=current))
                        current.count += 1
                        current.vehicles.append(v)

        return items.values()

    def __getItemsByType(self, v, itemTypeName):
        vd = v.descriptor
        if itemTypeName == 'vehicleChassis':
            return [vd.chassis['compactDescr']]
        if itemTypeName == 'vehicleEngine':
            return [vd.engine['compactDescr']]
        if itemTypeName == 'vehicleRadio':
            return [vd.radio['compactDescr']]
        if itemTypeName == 'vehicleFuelTank':
            return [vd.fuelTank['compactDescr']]
        if itemTypeName == 'vehicleTurret':
            if v.hasTurrets:
                return [vd.turret['compactDescr']]
        if itemTypeName == 'vehicleGun':
            return [vd.gun['compactDescr']]
        if itemTypeName == 'optionalDevice':
            return [ od['compactDescr'] for od in vd.optionalDevices if od ]
        if itemTypeName == 'equipment':
            return v.equipments
        return []

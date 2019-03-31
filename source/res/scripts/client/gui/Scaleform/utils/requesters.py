# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/utils/requesters.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld, nations, time, constants, AccountCommands
from functools import partial
from adisp import async, process
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_NOTE
from gui_items import InventoryItem, ShopItem, InventoryVehicle, InventoryTankman, VehicleItem
from items import ITEM_TYPE_NAMES, ITEM_TYPE_INDICES
from Account import PlayerAccount
import dossiers, constants
from items import tankmen
g_suitableModules = None
g_suitableVehicles = None
_ARTEFACTS_ITEMS = (ITEM_TYPE_INDICES['optionalDevice'], ITEM_TYPE_INDICES['equipment'])
_TANKMAN = ITEM_TYPE_INDICES['tankman']

def code2str(code):
    if code == AccountCommands.RES_SUCCESS:
        return 'Request succedded'
    if code == AccountCommands.RES_STREAM:
        return 'Stream is sent to the client'
    if code == AccountCommands.RES_CACHE:
        return 'Data is taken from cache'
    if code == AccountCommands.RES_FAILURE:
        return 'Unknown reason'
    if code == AccountCommands.RES_WRONG_ARGS:
        return 'Wrong arguments'
    if code == AccountCommands.RES_NON_PLAYER:
        return 'Account become non player'
    if code == AccountCommands.RES_SHOP_DESYNC:
        return 'Shop cache is desynchronized'
    if code == AccountCommands.RES_COOLDOWN:
        return 'Identical requests cooldown'
    if code == AccountCommands.RES_HIDDEN_DOSSIER:
        return 'Player dossier is hidden'
    if code == AccountCommands.RES_CENTER_DISCONNECTED:
        return 'Dossiers are unavailable'


class RequestProcessor(object):

    def __init__(self, delay, callback):
        self.__callback = callback
        self.__fired = False
        self.__bwCallbackID = BigWorld.callback(delay, self.__cooldownCallback)

    @property
    def isFired(self):
        return self.__fired

    def cancel(self):
        if self.__bwCallbackID is not None:
            BigWorld.cancelCallback(self.__bwCallbackID)
            self.__bwCallbackID = None
        return

    def __cooldownCallback(self):
        self.cancel()
        self.__fired = True
        self.__callback()


class DossierRequester(object):
    __queue = []
    __lastResponseTime = 0
    __request = None

    def __init__(self, userName):
        self.userName = userName
        self.__cache = {'account': None,
         'vehicles': {},
         'clan': None,
         'hidden': False,
         'available': True}
        return

    def __setLastResponseTime(self):
        DossierRequester.__lastResponseTime = time.time()

    def __nextRequestTime(self):
        t = constants.REQUEST_COOLDOWN.PLAYER_DOSSIER - (time.time() - DossierRequester.__lastResponseTime)
        if t > 0:
            return t

    def __processQueue(self):
        if DossierRequester.__request is not None:
            return
        elif DossierRequester.__queue:
            DossierRequester.__request = RequestProcessor(self.__nextRequestTime(), DossierRequester.__queue.pop())
            return
        else:
            return

    def __requestPlayerInfo(self, callback):

        def proxyCallback(value):
            if value is not None and len(value) > 1:
                self.__cache['account'] = dossiers.getAccountDossierDescr(value[0])
                self.__cache['clan'] = value[1]
            callback(self.__cache['account'])
            return

        DossierRequester.__queue.append(lambda : BigWorld.player().requestPlayerInfo(self.userName, partial(lambda c, code, dossier, clanID, clanInfo: self.__processValueResponse(c, code, (dossier, (clanID, clanInfo))), proxyCallback)))
        self.__processQueue()

    def __requestAccountDossier(self, callback):

        def proxyCallback(dossier):
            self.__cache['account'] = dossiers.getAccountDossierDescr(dossier)
            callback(self.__cache['account'])

        DossierRequester.__queue.append(lambda : BigWorld.player().requestAccountDossier(self.userName, partial(lambda c, code, dossier: self.__processValueResponse(c, code, dossier), proxyCallback)))
        self.__processQueue()

    def __requestVehicleDossier(self, vehCompDescr, callback):

        def proxyCallback(dossier):
            self.__cache['vehicles'][vehCompDescr] = dossiers.getVehicleDossierDescr(dossier)
            callback(self.__cache['vehicles'][vehCompDescr])

        DossierRequester.__queue.append(lambda : BigWorld.player().requestVehicleDossier(self.userName, vehCompDescr, partial(lambda c, code, dossier: self.__processValueResponse(c, code, dossier), proxyCallback)))
        self.__processQueue()

    def __requestClanInfo(self, callback):

        def proxyCallback(value):
            self.__cache['clan'] = value
            callback(self.__cache['clan'])

        DossierRequester.__queue.append(lambda : BigWorld.player().requestPlayerClanInfo(self.userName, partial(lambda c, code, str, clanDBID, clanInfo: self.__processValueResponse(c, code, (clanDBID, clanInfo)), callback)))
        self.__processQueue()

    def __processValueResponse(self, callback, code, value):
        self.__setLastResponseTime()
        DossierRequester.__request = None
        if code < 0:
            LOG_ERROR('Error while server request (code=%s): %s' % (code, code2str(code)))
            if code == AccountCommands.RES_HIDDEN_DOSSIER:
                self.__cache['hidden'] = True
            elif code == AccountCommands.RES_CENTER_DISCONNECTED:
                self.__cache['available'] = False
            callback(None)
        else:
            callback(value)
        self.__processQueue()
        return

    @async
    def getAccountDossier(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('account') is None:
            if self.__cache.get('clan') is None:
                self.__requestPlayerInfo(callback)
            else:
                self.__requestAccountDossier(callback)
            return
        else:
            callback(self.__cache['account'])
            return

    @async
    def getClanInfo(self, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('clan') is None:
            self.__requestClanInfo(callback)
            return
        else:
            callback(self.__cache['clan'])
            return

    @async
    def getVehicleDossier(self, vehCompDescr, callback):
        if not self.isValid:
            callback(None)
        if self.__cache.get('vehicles', {}).get(vehCompDescr, None) is None:
            self.__requestVehicleDossier(vehCompDescr, callback)
            return
        else:
            callback(self.__cache['vehicles'][vehCompDescr])
            return

    @property
    def isHidden(self):
        return self.__cache.get('hidden', False)

    @property
    def isAvailable(self):
        return self.__cache.get('available', False)

    @property
    def isValid(self):
        return not self.isHidden and self.isAvailable


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
            vehicles = []
            for compactDescr, price in data[0].items():
                vehicles.append(ShopItem(itemTypeName=ITEM_TYPE_NAMES[1], compactDescr=compactDescr, priceOrder=price, nation=nationId, hidden=compactDescr in data[1]))

            return vehicles

    @staticmethod
    def parseModules(data, itemTypeID, nationId):
        if data is None or not len(data):
            return []
        else:
            modules = []
            for compactDescr, price in data[0].items():
                modules.append(ShopItem(itemTypeName=ITEM_TYPE_NAMES[itemTypeID], compactDescr=compactDescr, priceOrder=price, nation=nationId, hidden=compactDescr in data[1]))

            return modules

    @staticmethod
    def getParser(itemTypeID):
        if itemTypeID == 1:
            return ShopParser.parseVehicles
        return lambda data, nationId: ShopParser.parseModules(data, itemTypeID, nationId)


class Requester(object):
    """
    Async requester of gui_items @see: helpers.Scaleform.utils.gui_items
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
    def getFromShop(self, callback, nation=None):
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
            self._requestShop(nations.NONE_INDEX)
        elif nation is not None:
            self._requestsCount = 1
            self._requestShop(nation)
        else:
            self._requestsCount = len(nations.INDICES)
            for nationId in nations.INDICES.values():
                self._requestShop(nationId)

        return

    def _requestInventory(self):
        assert hasattr(BigWorld.player(), 'inventory'), 'Request from inventory is not possible'
        BigWorld.player().inventory.getItems(self._itemTypeId, self.__parseInventoryResponse)

    def __parseInventoryResponse(self, responseCode, data):
        listData = []
        if responseCode >= 0:
            listData = Requester.PARSERS['inventory'].getParser(self._itemTypeId)(data)
        else:
            LOG_ERROR('Server return error for inventory getItems request: responseCode=%s, itemTypeId=%s.' % (responseCode, self._itemTypeId))
        self._collectResponse(listData, 'inventory')

    def _requestShop(self, nationId):
        assert hasattr(BigWorld.player(), 'shop'), 'Request from shop is not possible'
        BigWorld.player().shop.getItems(self._itemTypeId, nationId, lambda responseCode, data, shopRev: self.__parseShopResponse(responseCode, data, nationId))

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


def _getComponentsByType(vehicle, itemTypeId, turretPID=0):
    """
    Return list suitable modules for vehicle foloving structure:
    {
            compactDescriptor: (isCurrent, isDefault),
            ...
    }
    """
    vd = vehicle.descriptor
    components = {}
    descriptorsList = []
    current = None
    if itemTypeId == ITEM_TYPE_INDICES['vehicleChassis']:
        current = vd.chassis
        descriptorsList = vd.type.chassis
    if itemTypeId == ITEM_TYPE_INDICES['vehicleEngine']:
        current = vd.engine
        descriptorsList = vd.type.engines
    if itemTypeId == ITEM_TYPE_INDICES['vehicleRadio']:
        current = vd.radio
        descriptorsList = vd.type.radios
    if itemTypeId == ITEM_TYPE_INDICES['vehicleFuelTank']:
        current = vd.fuelTank
        descriptorsList = vd.type.fuelTanks
    if itemTypeId == ITEM_TYPE_INDICES['vehicleTurret']:
        current = vd.turret
        descriptorsList = vd.type.turrets[turretPID]
    if itemTypeId == ITEM_TYPE_INDICES['optionalDevice']:
        descriptorsList = vd.optionalDevices
    if itemTypeId == ITEM_TYPE_INDICES['equipment']:
        descriptorsList = vehicle.equipments
    if itemTypeId == ITEM_TYPE_INDICES['vehicleGun']:
        current = vd.gun
        for gun in vd.turret['guns']:
            descriptorsList.append(gun)

        for turret in vd.type.turrets[turretPID]:
            if turret is not vd.turret:
                for gun in turret['guns']:
                    descriptorsList.append(gun)

    if itemTypeId == ITEM_TYPE_INDICES['optionalDevice']:
        for index, item in enumerate(descriptorsList):
            if item:
                components[item['compactDescr']] = index

    elif itemTypeId == ITEM_TYPE_INDICES['equipment']:
        for index, item in enumerate(descriptorsList):
            if item:
                components[item] = index

    else:
        for item in descriptorsList:
            key = item['compactDescr']
            if not components.has_key(key):
                components[key] = item is current

    return components


class AvailableItemsRequester(Requester):

    def __init__(self, vehicle, itemTypeName):
        assert vehicle is not None
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


class CurrentVehicleRequester(object):

    def __init__(self):
        self.__callback = None
        return

    @async
    def get(self, callback):
        assert hasattr(BigWorld.player(), 'stats'), 'Request from stats is not possible'
        self.__callback = callback
        BigWorld.player().stats.get('currentVehInvID', self.__getResponse)

    @async
    def set(self, vehicleId, callback):
        assert hasattr(BigWorld.player(), 'stats'), 'Request from stats is not possible'
        self.__callback = callback
        BigWorld.player().stats.setCurrentVehicle(vehicleId, lambda code: self.__setResponse(code, vehicleId))

    @async
    def getMyVehicleInfo(self, vehicleId, callback):
        assert hasattr(BigWorld.player(), 'inventory'), 'Request from inventory is not possible'
        self.__callback = callback
        BigWorld.player().inventory.getVehicleInfo(vehicleId, lambda code, data: self.__parseVehicleResponse(code, data, vehicleId))

    def __parseVehicleResponse(self, responseCode, data, id):
        vehicleData = None
        if responseCode >= 0:
            vehicleData = InventoryVehicle(data[0], id, (0, 0), data[1], data[2], data[4], data[5])
        else:
            LOG_ERROR('Server return error for inventory getVehicleInfo request: responseCode=%s, itemTypeId=%s.' % (responseCode, self._itemTypeId))
        if self.__callback:
            self.__callback(vehicleData)
        return

    def __getResponse(self, responseCode, vehicleId):
        if responseCode < 0:
            LOG_ERROR('Server return error for statr get currentVehicleInvID request: responseCode=%s, vehicleId=%s.' % (responseCode, vehicleId))
        if self.__callback:
            self.__callback(vehicleId)

    def __setResponse(self, responseCode, vehicleId):
        if responseCode < 0:
            LOG_ERROR('Server return error for statr get currentVehicleInvID request: responseCode=%s, vehicleId=%s.' % (responseCode, vehicleId))
        if self.__callback:
            self.__callback(responseCode)


def responseIfNotAccount(*dargs, **dkwargs):

    def decorate(fn):

        def checkAccount(*fargs, **fkwargs):
            if not isinstance(BigWorld.player(), PlayerAccount):
                LOG_NOTE('Server call "StatsRequester.%s" canceled? player is not account.' % fn.func_name)
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
    @responseIfNotAccount(set())
    def getMultipliedXPVehicles(self, callback):
        BigWorld.player().stats.get('multipliedXPVehs', self.__valueResponse)

    @async
    @responseIfNotAccount(func=dossiers.getAccountDossierDescr, args=('',))
    def getAccountDossier(self, callback):
        BigWorld.player().stats.get('dossier', self.__accountDossierResponse)

    @async
    @responseIfNotAccount(func=dossiers.getVehicleDossierDescr, args=('',))
    def getVehicleDossier(self, vehTypeCompDescr, callback):
        BigWorld.player().dossierCache.get(constants.DOSSIER_TYPE.VEHICLE, vehTypeCompDescr, self.__vehicleDossierResponse)

    @async
    @responseIfNotAccount(func=dossiers.getTankmanDossierDescr, args=('',))
    def getTankmanDossier(self, tankmanID, callback):
        BigWorld.player().inventory.getItems(_TANKMAN, partial(self.__tankmanDossierResponse, tankmanID))

    @async
    @responseIfNotAccount(0)
    def getCredits(self, callback):
        BigWorld.player().stats.get('credits', self.__valueResponse)

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
    @responseIfNotAccount(False)
    def exchange(self, gold, callback):
        BigWorld.player().stats.exchange(gold, self.__response)

    @async
    @responseIfNotAccount(False)
    def convertToFreeXP(self, xp, vehTypeDescr, callback):
        BigWorld.player().stats.convertToFreeXP([vehTypeDescr], xp, self.__response)

    @async
    @responseIfNotAccount(0)
    def getAmmoSellPrice(self, ammo, callback):
        BigWorld.player().shop.getAmmoSellPrice(ammo, self.__valueResponse)

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
    def getDropSkillCost(self, callback):
        BigWorld.player().shop.getDropSkillCost(self.__valueResponse)

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
    def getSellPriceModifiers(self, callback):
        BigWorld.player().shop.getSellPriceModifiers(self.__valueResponse)

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
    @responseIfNotAccount(None)
    def getFileFromServer(self, clanId, fileType, callback):
        if not BigWorld.player().serverSettings['file_server'].has_key(fileType):
            LOG_ERROR("Invalid server's file type: %s" % fileType)
            self.__valueResponse(0, (None, None))
            return None
        else:
            try:
                clan_emblems = BigWorld.player().serverSettings['file_server'][fileType]
                BigWorld.player().customFilesCache.get(clan_emblems['url_template'] % clanId, clan_emblems['cache_life_time'], lambda url, file: self.__valueResponse(0, (url, file)))
            except:
                self.__valueResponse(0, (None, None))
                return None

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
        assert hasattr(BigWorld.player(), 'shop'), 'Request from shop is not possible'
        self.__callback = callback
        BigWorld.player().shop.getTradeFees(self.__valueResponse)

    def __accountDossierResponse(self, responseCode, dossierCompDescr=''):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat account dossier request: responseCode=%s' % responseCode)
            return
        if self.__callback:
            import dossiers
            dossierDescr = dossiers.getAccountDossierDescr(dossierCompDescr)
            self.__callback(dossierDescr)

    def __vehicleDossierResponse(self, responseCode, vehTypeDossiers=''):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat account dossier request: responseCode=%s' % responseCode)
            return
        else:
            if self.__callback:
                import dossiers
                if vehTypeDossiers is not None:
                    self.__callback(dossiers.getVehicleDossierDescr(vehTypeDossiers))
                self.__callback(dossiers.getVehicleDossierDescr(''))
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
                self.__callback(dossiers.getTankmanDossierDescr(dossier))
            return

    def _valueResponse(self, responseCode, value=None, revision=0):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s' % responseCode)
        elif self.__callback:
            self.__callback(value)

    def __valueResponse(self, responseCode, value=None, revision=0):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s' % responseCode)
        elif self.__callback:
            self.__callback(value)

    def __response(self, responseCode):
        if responseCode < 0:
            LOG_ERROR('Server return error for stat request: responseCode=%s.' % responseCode)
        if self.__callback:
            self.__callback(responseCode >= 0)


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
            if v.type not in ('AT-SPG', 'SPG'):
                return [vd.turret['compactDescr']]
        if itemTypeName == 'vehicleGun':
            return [vd.gun['compactDescr']]
        if itemTypeName == 'optionalDevice':
            return [ od['compactDescr'] for od in vd.optionalDevices if od ]
        if itemTypeName == 'equipment':
            return v.equipments
        return []

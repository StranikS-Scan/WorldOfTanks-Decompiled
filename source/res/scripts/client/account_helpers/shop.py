# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/Shop.py
import cPickle
import zlib
from math import ceil
from itertools import izip
import items
import AccountCommands
from debug_utils import LOG_DEBUG, LOG_ERROR
from items import vehicles, tankmen
from AccountCommands import BUY_VEHICLE_FLAG
from account_shared import AmmoIterator
from items.item_price import getNextSlotPrice, getNextBerthPackPrice
from persistent_caches import SimpleCache
from SyncController import SyncController
from PlayerEvents import g_playerEvents as events
from soft_exception import SoftException
_VEHICLE = items.ITEM_TYPE_INDICES['vehicle']
_CHASSIS = items.ITEM_TYPE_INDICES['vehicleChassis']
_TURRET = items.ITEM_TYPE_INDICES['vehicleTurret']
_GUN = items.ITEM_TYPE_INDICES['vehicleGun']
_ENGINE = items.ITEM_TYPE_INDICES['vehicleEngine']
_FUEL_TANK = items.ITEM_TYPE_INDICES['vehicleFuelTank']
_RADIO = items.ITEM_TYPE_INDICES['vehicleRadio']
_TANKMAN = items.ITEM_TYPE_INDICES['tankman']
_OPTIONALDEVICE = items.ITEM_TYPE_INDICES['optionalDevice']
_SHELL = items.ITEM_TYPE_INDICES['shell']
_EQUIPMENT = items.ITEM_TYPE_INDICES['equipment']

class Shop(object):

    def __init__(self):
        self.__account = None
        self.__syncController = None
        self.__cache = {}
        self.__persistentCache = SimpleCache('account_caches', 'shop')
        self.__ignore = True
        self.__isSynchronizing = False
        self.__syncID = 0
        self.__isFirstSync = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False
        self.__isFirstSync = True
        self.synchronize()

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True
        self.__isSynchronizing = False

    def setAccount(self, account):
        self.__account = account
        self.__persistentCache.setAccount(account)
        if self.__syncController is not None:
            self.__syncController.destroy()
            self.__syncController = None
        if account is not None:
            self.__syncController = SyncController(account, self.__sendSyncRequest, self.__onSyncResponse, self.__onSyncComplete)
        return

    def synchronize(self, serverCacheRev=None):
        LOG_DEBUG('Shop.synchronize: cli_rev=%s, serv_rev=%s' % (self.__getCacheRevision(), serverCacheRev))
        if self.__ignore:
            return
        elif self.__getCacheRevision() == serverCacheRev:
            return
        elif self.__isSynchronizing:
            return
        else:
            self.__isSynchronizing = True
            if not self.__isFirstSync:
                events.onShopResyncStarted()
            self.__syncController.request(self.__getNextSyncID(), None)
            return

    def resynchronize(self):
        LOG_DEBUG('resynchronize')
        if self.__ignore:
            return
        else:
            self.__cache.clear()
            self.__persistentCache.clear()
            self.__isSynchronizing = True
            self.__isFirstSync = False
            events.onShopResyncStarted()
            self.__syncController.request(self.__getNextSyncID(), None)
            return

    def waitForSync(self, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        elif not self.__isSynchronizing:
            callback(AccountCommands.RES_CACHE, self.__getCacheRevision())
            return
        else:
            proxy = lambda resultID, data: callback(resultID, self.__getCacheRevision())
            self.__syncController.request(self.__syncID, proxy)
            return

    def getCache(self, callback):
        self.__getValue(None, callback)
        return

    def getAllItems(self, callback):
        self.__getValue('items', callback)

    def getSellPriceModifiers(self, compDescr, callback):
        proxy = lambda resultID, _data, rev: self.__onGetSellPriceModifiers(resultID, compDescr, callback)
        self.__getValue('sellPriceModif', proxy)

    def getSellPrice(self, buyPrice, sellPriceModifiers, itemTypeID):
        shopRev, exchangeRate, exchangeRateForShellsAndEqs, _, sellPriceFactor, sellForGold = sellPriceModifiers
        if shopRev != self.__getCacheRevision():
            raise SoftException('Shop cache is not actual')
        if itemTypeID in (_SHELL, _EQUIPMENT):
            exchangeRate = exchangeRateForShellsAndEqs
        if sellForGold:
            sellPrice = (int(ceil(sellPriceFactor * buyPrice[0])), int(ceil(sellPriceFactor * buyPrice[1])))
        else:
            sellPrice = (int(ceil(sellPriceFactor * (buyPrice[0] + buyPrice[1] * exchangeRate))), 0)
        crystalPrice = buyPrice.get('crystal')
        if crystalPrice:
            crystalExchangeRate = self.__cache['crystalExchangeRate']
            sellPrice = (sellPrice[0] + int(ceil(sellPriceFactor * crystalExchangeRate * crystalPrice)), sellPrice[1])
        return sellPrice

    def getPrice(self, typeCompDescr, callback):
        proxy = lambda resultID, items, rev: self.__onGetPriceResponse(resultID, typeCompDescr, callback)
        self.__getValue('items', proxy)

    def getRentPackets(self, typeCompDescr, callback):
        proxy = lambda resultID, packets, rev: self.__onGetRentPacketsResponse(resultID, typeCompDescr, callback)
        self.__getValue('items', proxy)

    def getVehiclePrice(self, vehCompDescr, callback):
        proxy = lambda resultID, items, rev: self.__onGetVehiclePriceResponse(resultID, vehCompDescr, False, callback)
        self.__getValue('items', proxy)

    def getVehicleSellPrice(self, vehCompDescr, callback):
        proxy = lambda resultID, items, rev: self.__onGetVehiclePriceResponse(resultID, vehCompDescr, True, callback)
        self.__getValue('items', proxy)

    def getVehiclesSellPrices(self, vehCompDescrs, callback):
        proxy = lambda resultID, items, rev: self.__onGetVehiclesSellPriceResponse(resultID, vehCompDescrs, callback)
        self.__getValue('items', proxy)

    def getComponentPrice(self, compDescr, callback):
        proxy = lambda resultID, items, rev: self.__onGetComponentPriceResponse(resultID, compDescr, False, callback)
        self.__getValue('items', proxy)

    def getComponentSellPrice(self, compDescr, callback):
        proxy = lambda resultID, items, rev: self.__onGetComponentPriceResponse(resultID, compDescr, True, callback)
        self.__getValue('items', proxy)

    def getComponentsSellPrice(self, compDescrs, callback):
        proxy = lambda resultID, items, rev: self.__onGetComponentsPriceResponse(resultID, compDescrs, callback)
        self.__getValue('items', proxy)

    def getAmmoSellPrice(self, ammo, callback):
        proxy = lambda resultID, items, rev: self.__onGetAmmoSellPriceResponse(resultID, ammo, callback)
        self.__getValue('items', proxy)

    def getDailyXPFactor(self, callback):
        self.__getValue('dailyXPFactor', callback)

    def getSlotsPrices(self, callback):
        self.__getValue('slotsPrices', callback)

    def getNextSlotPrice(self, slots, slotsPrices):
        return getNextSlotPrice(slots, slotsPrices)

    def getBerthsPrices(self, callback):
        self.__getValue('berthsPrices', callback)

    def getNextBerthPackPrice(self, berths, berthsPrices):
        return getNextBerthPackPrice(berths, berthsPrices)

    def getExchangeRate(self, callback):
        self.__getValue('exchangeRate', callback)

    def getExchangeRateForShellsAndEqs(self, callback):
        self.__getValue('exchangeRateForShellsAndEqs', callback)

    def isEnabledBuyingGoldShellsForCredits(self, callback):
        self.__getValue('isEnabledBuyingGoldShellsForCredits', callback)

    def isEnabledBuyingGoldEqsForCredits(self, callback):
        self.__getValue('isEnabledBuyingGoldEqsForCredits', callback)

    def getFreeXPToTManXPRate(self, callback):
        self.__getValue('freeXPToTManXPRate', callback)

    def getFreeXPConversion(self, callback):
        self.__getValue('freeXPConversion', callback)

    def getPremiumCost(self, callback):
        self.__getValue('premiumCost', callback)

    def getTankmanCost(self, callback):
        self.__getValue('tankmanCost', callback)

    def getChangeRoleCost(self, callback):
        self.__getValue('changeRoleCost', callback)

    def getDropSkillsCost(self, callback):
        self.__getValue('dropSkillsCost', callback)

    def getPaidRemovalCost(self, callback):
        self.__getValue('paidRemovalCost', callback)

    def getCamouflageCost(self, callback):
        self.__getValue('camouflageCost', callback)

    def getPlayerEmblemCost(self, callback):
        self.__getValue('playerEmblemCost', callback)

    def getPlayerInscriptionCost(self, callback):
        self.__getValue('playerInscriptionCost', callback)

    def buy(self, itemTypeIdx, nationIdx, itemShopID, count, goldForCredits, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, {})
            return
        elif itemTypeIdx == _VEHICLE:
            self.buyVehicle(nationIdx, itemShopID, False, True, 0, -1, callback)
            return
        else:
            count = int(round(count))
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_BUY_ITEM, self.__getCacheRevision(), itemShopID, count, goldForCredits, proxy)
            return

    def buyAndEquipItem(self, vehInvID, compDescr, slotIdx, isPaidRemoval, gunCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, '', {})
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
            else:
                proxy = None
            arr = [self.__getCacheRevision(),
             compDescr,
             vehInvID,
             slotIdx,
             isPaidRemoval,
             gunCompDescr]
            self.__account._doCmdIntArr(AccountCommands.CMD_BUY_AND_EQUIP_ITEM, arr, proxy)
            return

    def buyAndEquipTankman(self, vehInvID, slot, tmanCostTypeIdx, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, '', {})
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_BUY_AND_EQUIP_TMAN, self.__getCacheRevision(), vehInvID, slot, tmanCostTypeIdx, proxy)
            return

    def buyVehicle(self, nationIdx, innationIdx, buyShells, recruitCrew, tmanCostTypeIdx, rentPeriod, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, {})
            return
        else:
            typeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', nationIdx, innationIdx)
            flags = BUY_VEHICLE_FLAG.NONE
            if buyShells:
                flags |= BUY_VEHICLE_FLAG.SHELLS
            if recruitCrew:
                flags |= BUY_VEHICLE_FLAG.CREW
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            arr = [self.__getCacheRevision(),
             typeCompDescr,
             flags,
             tmanCostTypeIdx,
             rentPeriod]
            self.__account._doCmdIntArr(AccountCommands.CMD_BUY_VEHICLE, arr, proxy)
            return

    def tradeInVehicle(self, vehInvID, nationIdx, innationIdx, buyShells, recruitCrew, tmanCostTypeIdx, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, {})
            return
        else:
            typeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', nationIdx, innationIdx)
            flags = BUY_VEHICLE_FLAG.NONE
            if buyShells:
                flags |= BUY_VEHICLE_FLAG.SHELLS
            if recruitCrew:
                flags |= BUY_VEHICLE_FLAG.CREW
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            arr = [self.__getCacheRevision(),
             vehInvID,
             typeCompDescr,
             flags,
             tmanCostTypeIdx]
            self.__account._doCmdIntArr(AccountCommands.CMD_VEHICLE_TRADE_IN, arr, proxy)
            return

    def buyTankman(self, nationIdx, innationIdx, role, tmanCostTypeIdx, callback):
        vehTypeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', nationIdx, innationIdx)
        roleIdx = tankmen.SKILL_INDICES[role]
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('tmanInvID', None), ext.get('tmanCompDescr', None))
        else:
            proxy = None
        self.__account._doCmdInt4(AccountCommands.CMD_BUY_TMAN, self.__getCacheRevision(), vehTypeCompDescr, roleIdx, tmanCostTypeIdx, proxy)
        return

    def buyTokenTankman(self, nationIdx, innationIdx, role, tokenName, callback):
        vehTypeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', nationIdx, innationIdx)
        roleIdx = tankmen.SKILL_INDICES[role]
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext.get('tmanInvID', None), ext.get('tmanCompDescr', None))
        else:
            proxy = None
        self.__account._doCmdInt2Str(AccountCommands.CMD_TMAN_RECRUIT, vehTypeCompDescr, roleIdx, tokenName, proxy)
        return

    def buyGoodie(self, goodieID, count, forGold, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, {})
            return
        else:
            count = int(round(count))
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_BUY_GOODIE, self.__getCacheRevision(), goodieID, count, forGold, proxy)
            return

    def buyAndEquipOutfit(self, vehInvID, season, outfitDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            intArr = [self.__getCacheRevision(), vehInvID, season]
            strArr = [outfitDescr]
            self.__account._doCmdIntArrStrArr(AccountCommands.CMD_VEH_APPLY_OUTFIT, intArr, strArr, proxy)
            return

    def buyAndEquipStyle(self, vehInvID, styleID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_VEH_APPLY_STYLE, self.__getCacheRevision(), vehInvID, styleID, proxy)
            return

    def buyCustomizations(self, vehInvID, itemsCount, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            intArr = [self.__getCacheRevision(), vehInvID]
            for intCD, count in itemsCount.iteritems():
                intArr.extend((intCD, count))

            self.__account._doCmdIntArr(AccountCommands.CMD_BUY_C11N_ITEMS, intArr, proxy)
            return

    def sellCustomizations(self, vehInvID, itemCD, count, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_SELL_C11N_ITEMS, self.__getCacheRevision(), itemCD, count, vehInvID, proxy)
            return

    def resetC11nItemsNovelty(self, itemsList, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, [])
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            intArr = [self.__getCacheRevision()]
            for item in itemsList:
                intArr.extend(item)

            self.__account._doCmdIntArr(AccountCommands.CMD_RESET_C11N_ITEMS_NOVELTY, intArr, proxy)
            return

    def __onSyncResponse(self, syncID, resultID, ext=None):
        ext = ext or {}
        if resultID == AccountCommands.RES_NON_PLAYER:
            return
        if syncID != self.__syncID:
            return
        if resultID < 0:
            LOG_ERROR('Shop synchronization failed. Repeating')
            self.resynchronize()
            return
        if resultID == AccountCommands.RES_CACHE:
            try:
                data = cPickle.loads(zlib.decompress(self.__persistentCache.getData()))
            except Exception:
                self.resynchronize()
                return

            self.__onSyncDataReceived(data)
        elif resultID == AccountCommands.RES_SUCCESS:
            if self.__isFirstSync:
                self.__isFirstSync = False
            else:
                events.onShopResync()
        self.__isSynchronizing = False

    def __onSyncComplete(self, syncID, data):
        if syncID != self.__syncID:
            return
        elif data is None:
            return
        else:
            streamData = self.__account.lastStreamData
            self.__persistentCache.save((streamData.origPacketLen, streamData.origCrc32), streamData.data)
            self.__onSyncDataReceived(data)
            return

    def __onSyncDataReceived(self, data):
        data['sellPriceModif'] = data['sellPriceFactor']
        self.__cache = data
        self.__isSynchronizing = False
        if self.__isFirstSync:
            self.__isFirstSync = False
        else:
            events.onShopResync()

    def __onGetItemsResponse(self, resultID, itemTypeIdx, nationIdx, callback):
        if resultID < 0:
            result = None
        else:
            result = self.__cache.get('items', {}).get(nationIdx, {}).get(itemTypeIdx, None)
        if callback is not None:
            callback(resultID, result, self.__getCacheRevision())
        return

    def __onGetValueResponse(self, resultID, key, callback):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None, self.__getCacheRevision())
            return
        elif self.__isSynchronizing:
            self.__getValue(key, callback)
            return
        else:
            value = self.__cache if key is None else self.__cache.get(key, None)
            if callback is not None:
                callback(resultID, value, self.__getCacheRevision())
            return

    def __onGetPriceResponse(self, resultID, typeCompDescr, callback):
        if resultID < 0:
            price = None
        else:
            price = self.__getPriceFromCache(typeCompDescr)
        if callback is not None:
            callback(resultID, price, self.__getCacheRevision())
        return

    def __onGetRentPacketsResponse(self, resultID, typeCompDescr, callback):
        if resultID < 0:
            packets = None
        else:
            packets = self.__getRentPacketsFromCache(typeCompDescr)
        if callback is not None:
            callback(resultID, packets, self.__getCacheRevision())
        return

    def __onGetVehiclePriceResponse(self, resultID, vehCompDescr, isSellPrice, callback):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None, self.__getCacheRevision())
            return
        else:
            price = self.__getVehiclePriceFromCache(vehCompDescr, None)
            if isSellPrice and price is not None:
                typeCompDescr = vehicles.getVehicleTypeCompactDescr(vehCompDescr)
                price = self.getSellPrice(price, self.__getSellPriceModifiersFromCache(typeCompDescr), _VEHICLE)
            if callback is not None:
                callback(resultID, price, self.__getCacheRevision())
            return

    def __onGetVehiclesSellPriceResponse(self, resultID, vehCompDescrs, callback):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None, self.__getCacheRevision())
            return
        else:
            prices = []
            for vehCompDescr in vehCompDescrs:
                price = self.__getVehiclePriceFromCache(vehCompDescr, None)
                if price is None:
                    prices = None
                    break
                prices.append(self.getSellPrice(price, self.__getSellPriceModifiersFromCache(vehCompDescr), _VEHICLE))

            if callback is not None:
                callback(resultID, prices, self.__getCacheRevision())
            return

    def __onGetComponentPriceResponse(self, resultID, compDescr, isSellPrice, callback):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None, self.__getCacheRevision())
            return
        else:
            itemTypeIdx, _, _ = vehicles.parseIntCompactDescr(compDescr)
            price = self.__getPriceFromCache(compDescr)
            if isSellPrice:
                price = self.getSellPrice(price, self.__getSellPriceModifiersFromCache(compDescr), itemTypeIdx)
            if callback is not None:
                callback(resultID, price, self.__getCacheRevision())
            return

    def __onGetComponentsPriceResponse(self, resultID, compDescrs, callback):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None, self.__getCacheRevision())
            return
        else:
            prices = []
            for compDescr in compDescrs:
                itemTypeIdx, _, _ = vehicles.parseIntCompactDescr(compDescr)
                if itemTypeIdx == _VEHICLE:
                    continue
                price = self.__getPriceFromCache(compDescr, None)
                if price is None:
                    prices = None
                    break
                prices.append(self.getSellPrice(price, self.__getSellPriceModifiersFromCache(compDescr), itemTypeIdx))

            if callback is not None:
                callback(resultID, prices, self.__getCacheRevision())
            return

    def __onGetAmmoSellPriceResponse(self, resultID, ammo, callback):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None, self.__getCacheRevision())
            return
        else:
            price = 0
            for shellCompDescr, count in AmmoIterator(ammo):
                if count == 0:
                    continue
                shellPrice = self.__getPriceFromCache(shellCompDescr)
                shellSellPrice = self.getSellPrice(shellPrice, self.__getSellPriceModifiersFromCache(shellCompDescr), _SHELL)
                price += shellSellPrice * count

            if callback is not None:
                callback(resultID, price, self.__getCacheRevision())
            return

    def __onGetSellPriceModifiers(self, resultID, compDescr, callback):
        callback(resultID, self.__getSellPriceModifiersFromCache(compDescr))

    def __getNextSyncID(self):
        self.__syncID += 1
        if self.__syncID > 30000:
            self.__syncID = 1
        return self.__syncID

    def __sendSyncRequest(self, syncID, proxy):
        if self.__ignore:
            return
        clientRev = self.__getCacheRevision()
        descr = self.__persistentCache.getDescr()
        dataLen, dataCrc = descr if descr else (0, 0)
        self.__account._doCmdInt3(AccountCommands.CMD_SYNC_SHOP, clientRev, dataLen, dataCrc, proxy)

    def __getCacheRevision(self):
        return self.__cache.get('rev', 0)

    def __getPriceFromCache(self, typeCompDescr, default=(0, 0)):
        vehPrices = self.__cache.get('items', {}).get('itemPrices', {})
        return vehPrices.get(typeCompDescr, default)

    def __getRentPacketsFromCache(self, vehTypeCompDescr):
        packets = self.__cache.get('items', {}).get('vehiclesRentPrices', {})
        return packets.get(vehTypeCompDescr, {})

    def __getVehiclePriceFromCache(self, vehCompDescr, default=(0, 0)):
        typeCompDescr = vehicles.getVehicleTypeCompactDescr(vehCompDescr)
        price = self.__getPriceFromCache(typeCompDescr, None)
        if price is None:
            return default
        else:
            vehDescr = vehicles.VehicleDescr(compactDescr=vehCompDescr)
            devices = vehDescr.getDevices()
            for defCompDescr, instCompDescr in izip(devices[0], devices[1]):
                if defCompDescr == instCompDescr:
                    continue
                compPrice = self.__getPriceFromCache(defCompDescr, None)
                if compPrice is None:
                    return default
                price = _subtractPrices(price, compPrice)
                compPrice = self.__getPriceFromCache(instCompDescr, None)
                if compPrice is None:
                    return default
                price = _summPrices(price, compPrice)

            for optDevCompDescr in devices[2]:
                compPrice = self.__getPriceFromCache(optDevCompDescr, None)
                if compPrice is None:
                    return default
                price = _summPrices(price, compPrice)

            return price

    def __getSellPriceModifiersFromCache(self, typeCompDescr):
        cache = self.__cache
        result = cache.get('items', {})
        sellPriceModif = cache.get('sellPriceModif', 0)
        sellPriceFactors = result.get('vehicleSellPriceFactors', {})
        sellForGold = result.get('vehiclesToSellForGold', {})
        return (self.__getCacheRevision(),
         cache.get('exchangeRate', 0),
         cache.get('exchangeRateForShellsAndEqs', 0),
         sellPriceModif,
         sellPriceFactors.get(typeCompDescr, sellPriceModif),
         typeCompDescr in sellForGold)

    def __getValue(self, key, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None, self.__getCacheRevision())
            return
        elif not self.__isSynchronizing:
            self.__onGetValueResponse(AccountCommands.RES_CACHE, key, callback)
            return
        else:
            proxy = lambda resultID, data: self.__onGetValueResponse(resultID, key, callback)
            self.__syncController.request(self.__syncID, proxy)
            return


def _summPrices(price1, price2):
    return (price1[0] + price2[0], price1[1] + price2[1])


def _subtractPrices(price1, price2):
    return (price1[0] - price2[0], price1[1] - price2[1])

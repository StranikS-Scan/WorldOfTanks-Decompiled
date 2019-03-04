# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/Inventory.py
import collections
from array import array
from functools import partial
from itertools import chain
import logging
import AccountCommands
import items
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from items import vehicles, tankmen
_logger = logging.getLogger(__name__)
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

def getAmmoAsDict(ammo):
    ammoAsDict = collections.defaultdict(int)
    for i in xrange(len(ammo) / 2):
        ammoAsDict[ammo[2 * i]] += ammo[2 * i + 1]

    return ammoAsDict


class Inventory(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        invDiff = diff.get('inventory', None)
        if invDiff is not None:
            for itemTypeIdx, itemInvDiff in invDiff.iteritems():
                synchronizeDicts(itemInvDiff, self.__cache.setdefault(itemTypeIdx, {}))

        cacheDiff = diff.get('cache', None)
        if cacheDiff is not None:
            vehsLockDiff = cacheDiff.get('vehsLock', None)
            if vehsLockDiff is not None:
                itemInvCache = self.__cache.setdefault(_VEHICLE, {})
                synchronizeDicts(vehsLockDiff, itemInvCache.setdefault('lock', {}))
        return

    def getCache(self, callback):
        self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))

    def getItems(self, itemTypeIdx, callback):
        self.__syncData.waitForSync(partial(self.__onGetItemsResponse, itemTypeIdx, callback))

    def sell(self, itemTypeIdx, itemInvID, count, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        elif itemTypeIdx == _VEHICLE:
            self.sellVehicle(itemInvID, True, [], [], [], callback)
            return
        elif itemTypeIdx == _TANKMAN:
            if callback is not None:
                callback(AccountCommands.RES_WRONG_ARGS)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellItem_onShopSynced, itemTypeIdx, itemInvID, count, callback))
            return

    def sellMultiple(self, itemList, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellMultipleItems_onShopSynced, itemList, callback))
            return

    def sellVehicle(self, vehInvID, dismissCrew, itemsFromVehicle, itemsFromInventory, customizationItems, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellVehicle_onShopSynced, vehInvID, dismissCrew, itemsFromVehicle, itemsFromInventory, customizationItems, callback))
            return

    def dismissTankman(self, tmanInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_DISMISS_TMAN, tmanInvID, 0, 0, proxy)
            return

    def equipCrewSkin(self, tmanInvID, skinID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__account._doCmdInt3(AccountCommands.CMD_TMAN_EQUIP_CREW_SKIN, tmanInvID, skinID, 0, proxy)
            return

    def unequipCrewSkin(self, tmanInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__account._doCmdInt3(AccountCommands.CMD_TMAN_UNEQUIP_CREW_SKIN, tmanInvID, 0, 0, proxy)
            return

    def equip(self, vehInvID, itemCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0, [])
            return
        else:
            itemTypeIdx = vehicles.parseIntCompactDescr(itemCompDescr)[0]
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_EQUIP, vehInvID, itemCompDescr, 0, proxy)
            return

    def equipTurret(self, vehInvID, turretCompDescr, gunCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0, [])
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_EQUIP, vehInvID, turretCompDescr, gunCompDescr, proxy)
            return

    def equipOptionalDevice(self, vehInvID, deviceCompDescr, slotIdx, isPaidRemoval, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0, [])
            return
        else:
            self.__account.shop.waitForSync(partial(self.__equipOptionDevice_onShopSynced, vehInvID, deviceCompDescr, slotIdx, isPaidRemoval, callback))
            return

    def equipShells(self, vehInvID, shells, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, [])
            return
        else:
            arr = [vehInvID] + [ int(s) for s in shells ]
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_EQUIP_SHELLS, arr, proxy)
            return

    def equipEquipments(self, vehInvID, eqs, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, [])
            return
        else:
            arr = [vehInvID] + [ int(e) for e in eqs ]
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_EQUIP_EQS, arr, proxy)
            return

    def setAndFillLayouts(self, vehInvID, shellsLayout, eqsLayout, equipmentType, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, '', {})
            return
        else:
            self.__account.shop.waitForSync(partial(self.__setAndFillLayouts_onShopSynced, vehInvID, shellsLayout, equipmentType, eqsLayout, callback))
            return

    def equipTankman(self, vehInvID, slot, tmanInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, [])
            return
        else:
            if tmanInvID is None:
                tmanInvID = -1
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_EQUIP_TMAN, vehInvID, slot, tmanInvID, proxy)
            return

    def returnCrew(self, vehInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, [])
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_RETURN_CREW, vehInvID, 0, 0, proxy)
            return

    def repair(self, vehInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_REPAIR, vehInvID, 0, 0, proxy)
            return

    def addTankmanSkill(self, tmanInvID, skillName, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            skillIdx = tankmen.SKILL_INDICES[skillName]
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_TMAN_ADD_SKILL, tmanInvID, skillIdx, 0, proxy)
            return

    def dropTankmanSkills(self, tmanInvID, dropSkillsCostIdx, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__dropSkillsTman_onShopSynced, tmanInvID, dropSkillsCostIdx, callback))
            return

    def respecTankman(self, tmanInvID, vehTypeCompDescr, tmanCostTypeIdx, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if vehTypeCompDescr is None:
                vehTypeCompDescr = 0
            self.__account.shop.waitForSync(partial(self.__respecTman_onShopSynced, tmanInvID, vehTypeCompDescr, tmanCostTypeIdx, callback))
            return

    def multiRespecTankman(self, tmenInvIDsAndCostTypeIdx, vehTypeCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if vehTypeCompDescr is None:
                vehTypeCompDescr = 0
            self.__account.shop.waitForSync(partial(self.__multiRespecTman_onShopSynced, tmenInvIDsAndCostTypeIdx, vehTypeCompDescr, callback))
            return

    def changeTankmanRole(self, tmanInvID, roleIdx, vehTypeCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if vehTypeCompDescr is None:
                vehTypeCompDescr = 0
            self.__account.shop.waitForSync(partial(self.__changeTankmanRole_onShopSynced, tmanInvID, roleIdx, vehTypeCompDescr, callback))
            return

    def replacePassport(self, tmanInvID, isPremium, isFemale, fnGroupID, firstNameID, lnGroupID, lastNameID, iGroupID, iconID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__replacePassport_onShopSynced, tmanInvID, isPremium, isFemale, fnGroupID, firstNameID, lnGroupID, lastNameID, iGroupID, iconID, callback))
            return

    def freeXPToTankman(self, tmanInvID, freeXP, callback):
        if self.__ignore:
            if callback is not None:
                callback('', AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__freeXPToTankman_onShopSynced, tmanInvID, freeXP, callback))
            return

    def changeVehicleSetting(self, vehInvID, setting, isOn, source, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            isOn = 1 if isOn else 0
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_VEH_SETTINGS, vehInvID, setting, isOn, source, proxy)
            return

    def addTankmanExperience(self, tmanInvID, xp, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_ADD_TMAN_XP, tmanInvID, xp, 0, proxy)
            return

    def addCrewSkin(self, skinsDict, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            skinList = []
            for k, v in skinsDict.items():
                skinList.extend([k, v])

            self.__account._doCmdIntArr(AccountCommands.CMD_TMAN_ADD_CREW_SKIN, skinList, proxy)
            return

    def getProviderForVehInvId(self, vehInvId, serverSettings):
        if not self.__cache:
            _logger.warning('Local cache is empty, cannot get provider name.')
            return ''
        elif 'telecomOrders' not in self.__cache:
            _logger.warning('telecomOrders key is missing.')
            return ''
        foundBundleId = None
        telecomOrders = self.__cache['telecomOrders']
        for bundle in telecomOrders.itervalues():
            bundleId, vehInvIds = bundle
            if vehInvId in vehInvIds:
                foundBundleId = bundleId
                break

        if foundBundleId is None:
            _logger.warning('Cannot find bundleId for vehicle with invId=%d.', vehInvId)
            return ''
        else:
            return serverSettings.telecomConfig.getInternetProvider(foundBundleId)

    def __onGetItemsResponse(self, itemTypeIdx, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache.get(itemTypeIdx, None))
            return

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def __sellItem_onShopSynced(self, itemTypeIdx, itemInvID, count, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_SELL_ITEM, shopRev, itemTypeIdx, itemInvID, count, proxy)
            return

    def __sellMultipleItems_onShopSynced(self, itemList, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            intArr = array('i', [shopRev] + list(chain(*itemList)))
            self.__account._doCmdIntArr(AccountCommands.CMD_SELL_MULTIPLE_ITEMS, intArr, proxy)
            return

    def __sellVehicle_onShopSynced(self, vehInvID, flags, itemsFromVehicle, itemsFromInventory, customizationItems, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            arr = [shopRev,
             vehInvID,
             flags,
             len(itemsFromVehicle)] + itemsFromVehicle
            arr += [len(itemsFromInventory)] + itemsFromInventory
            arr += [len(customizationItems)] + customizationItems
            self.__account._doCmdIntArr(AccountCommands.CMD_SELL_VEHICLE, arr, proxy)
            return

    def __dropSkillsTman_onShopSynced(self, tmanInvID, dropSkillsCostIdx, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_TMAN_DROP_SKILLS, shopRev, tmanInvID, dropSkillsCostIdx, proxy)
            return

    def __respecTman_onShopSynced(self, tmanInvID, vehTypeCompDescr, tmanCostTypeIdx, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_TMAN_RESPEC, shopRev, tmanInvID, tmanCostTypeIdx, vehTypeCompDescr, proxy)
            return

    def __multiRespecTman_onShopSynced(self, tmenInvIDsAndCostTypeIdx, vehTypeCompDescr, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            arr = [shopRev, vehTypeCompDescr]
            for tmanInvID, tmanCostTypeIdx in tmenInvIDsAndCostTypeIdx:
                arr.append(tmanInvID)
                arr.append(tmanCostTypeIdx)

            self.__account._doCmdIntArr(AccountCommands.CMD_TMAN_MULTI_RESPEC, arr, proxy)
            return

    def __changeTankmanRole_onShopSynced(self, tmanInvID, roleIdx, vehTypeCompDescr, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_TMAN_CHANGE_ROLE, shopRev, tmanInvID, roleIdx, vehTypeCompDescr, proxy)
            return

    def __replacePassport_onShopSynced(self, tmanInvID, isPremium, isFemale, fnGroupID, firstNameID, lnGroupID, lastNameID, iGroupID, iconID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            arr = [shopRev, tmanInvID, isPremium]
            if isFemale is None:
                arr.append(-1)
            elif isFemale:
                arr.append(1)
            else:
                arr.append(0)
            arr.append(fnGroupID)
            arr.append(firstNameID if firstNameID is not None else -1)
            arr.append(lnGroupID)
            arr.append(lastNameID if lastNameID is not None else -1)
            arr.append(iGroupID)
            arr.append(iconID if iconID is not None else -1)
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_TMAN_PASSPORT, arr, proxy)
            return

    def __freeXPToTankman_onShopSynced(self, tmanInvID, freeXP, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback('', resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(errorStr, resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_TRAINING_TMAN, shopRev, tmanInvID, freeXP, proxy)
            return

    def __setAndFillLayouts_onShopSynced(self, vehInvID, shellsLayout, equipmentType, eqsLayout, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID, '', {})
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
            else:
                proxy = None
            arr = [shopRev, vehInvID]
            if shellsLayout is not None:
                arr.append(len(shellsLayout))
                arr += shellsLayout
            else:
                arr.append(0)
            arr.append(equipmentType)
            if eqsLayout is not None:
                arr.append(len(eqsLayout))
                arr += eqsLayout
            else:
                arr.append(0)
            self.__account._doCmdIntArr(AccountCommands.CMD_SET_AND_FILL_LAYOUTS, arr, proxy)
            return

    def __equipOptionDevice_onShopSynced(self, vehInvID, deviceCompDescr, slotIdx, isPaidRemoval, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            arr = [shopRev,
             vehInvID,
             deviceCompDescr,
             slotIdx,
             int(isPaidRemoval)]
            self.__account._doCmdIntArr(AccountCommands.CMD_EQUIP_OPTDEV, arr, proxy)
            return

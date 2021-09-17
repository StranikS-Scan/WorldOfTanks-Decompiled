# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/Inventory.py
import collections
import logging
import typing
from array import array
from functools import partial
from itertools import chain
import AccountCommands
import items
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from items import vehicles, tankmen
from account_helpers.abilities import AbilitiesHelper
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

    def __init__(self, syncData, clientCommandsProxy):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__ignore = True
        self.__commandsProxy = clientCommandsProxy
        self.abilities = AbilitiesHelper()
        return

    def onAccountBecomePlayer(self):
        self.__ignore = False
        self.abilities.onAccountBecomePlayer()

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True
        self.abilities.onAccountBecomeNonPlayer()

    def setAccount(self, account):
        self.__account = account
        self.abilities.setAccount(account)

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
            self.sellVehicle([(itemInvID,
              True,
              [],
              [],
              [],
              [])], callback)
            return
        elif itemTypeIdx == _TANKMAN:
            if callback is not None:
                callback(AccountCommands.RES_WRONG_ARGS)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellItemOnShopSynced, itemTypeIdx, itemInvID, count, callback))
            return

    def sellMultiple(self, itemList, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellMultipleItemsOnShopSynced, itemList, callback))
            return

    def sellVehicle(self, vehiclesSellData, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellVehicleOnShopSynced, vehiclesSellData, callback))
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

    def useCrewBook(self, crewBookCD, vehInvID, tmanInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__account._doCmdInt3(AccountCommands.CMD_LEARN_CREW_BOOK, crewBookCD, vehInvID, tmanInvID, proxy)
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

    def equipOptionalDevice(self, vehInvID, deviceCompDescr, slotIdx, isAllSetups, isPaidRemoval, callback, useDemountKit):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0, [])
            return
        else:
            self.__account.shop.waitForSync(partial(self.__equipOptionDeviceOnShopSynced, vehInvID, deviceCompDescr, slotIdx, isAllSetups, isPaidRemoval, callback, useDemountKit))
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
            self.__account.shop.waitForSync(partial(self.__setAndFillLayoutsOnShopSynced, vehInvID, shellsLayout, equipmentType, eqsLayout, callback))
            return

    def changeVehicleSetupGroup(self, vehInvID, groupID, layoutIdx, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__commandsProxy.perform(AccountCommands.CMD_SWITCH_LAYOUT, vehInvID, groupID, layoutIdx, proxy)
            return

    def switchPrebattleAmmoPanelAvailability(self, vehInvID, groupID, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__commandsProxy.perform(AccountCommands.CMD_TOGGLE_SWITCH_LAYOUT, vehInvID, groupID, proxy)
            return

    def discardPostProgressionPairs(self, vehIntCD, stepIDs, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__commandsProxy.perform(AccountCommands.CMD_VPP_DISCARD_PAIRS, [vehIntCD] + stepIDs, proxy)
            return

    def purchasePostProgressionPair(self, vehIntCD, stepID, pairType, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__commandsProxy.perform(AccountCommands.CMD_VPP_SELECT_PAIR, vehIntCD, stepID, pairType, proxy)
            return

    def purchasePostProgressionSteps(self, vehIntCD, stepIDs, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext=(): callback(resultID, ext)
            self.__commandsProxy.perform(AccountCommands.CMD_VPP_UNLOCK_ITEMS, [vehIntCD] + stepIDs, proxy)
            return

    def setEquipmentSlotType(self, vehInvID, slotID, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__setEquipmentSlotTypeOnShopSynched, vehInvID, slotID, callback))
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
            self.__account.shop.waitForSync(partial(self.__dropSkillsTmanOnShopSynced, tmanInvID, dropSkillsCostIdx, callback))
            return

    def respecTankman(self, tmanInvID, vehTypeCompDescr, tmanCostTypeIdx, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if vehTypeCompDescr is None:
                vehTypeCompDescr = 0
            self.__account.shop.waitForSync(partial(self.__respecTmanOnShopSynced, tmanInvID, vehTypeCompDescr, tmanCostTypeIdx, callback))
            return

    def multiRespecTankman(self, tmenInvIDsAndCostTypeIdx, vehTypeCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if vehTypeCompDescr is None:
                vehTypeCompDescr = 0
            self.__account.shop.waitForSync(partial(self.__multiRespecTmanOnShopSynced, tmenInvIDsAndCostTypeIdx, vehTypeCompDescr, callback))
            return

    def changeTankmanRole(self, tmanInvID, roleIdx, vehTypeCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if vehTypeCompDescr is None:
                vehTypeCompDescr = 0
            self.__account.shop.waitForSync(partial(self.__changeTankmanRoleOnShopSynced, tmanInvID, roleIdx, vehTypeCompDescr, callback))
            return

    def replacePassport(self, tmanInvID, isPremium, isFemale, fnGroupID, firstNameID, lnGroupID, lastNameID, iGroupID, iconID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__replacePassportOnShopSynced, tmanInvID, isPremium, isFemale, fnGroupID, firstNameID, lnGroupID, lastNameID, iGroupID, iconID, callback))
            return

    def freeXPToTankman(self, tmanInvID, freeXP, callback):
        if self.__ignore:
            if callback is not None:
                callback('', AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__freeXPToTankmanOnShopSynced, tmanInvID, freeXP, callback))
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

    def upgradeOptDev(self, optDevID, vehInvID, setupIdx, slotIdx, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__upgradeOptDevOnShopSynced, optDevID, vehInvID, setupIdx, slotIdx, callback))
            return

    def switchNation(self, itemName, nextItemName, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:

            def _selectVehicle(resultID, ext, cacheResultID, cacheData=None):
                vhTypeID = ext.get('switchToVhInvID', 0)
                if vhTypeID:
                    from CurrentVehicle import g_currentVehicle
                    if not g_currentVehicle.item.activeInNationGroup:
                        g_currentVehicle.selectVehicle(vhTypeID)
                callback(resultID)

            def _waitForDossier(resultID, ext):
                self.__account.dossierCache.waitForSync(partial(_selectVehicle, resultID, ext))

            proxy = lambda requestID, resultID, errorStr, ext={}: _waitForDossier(resultID, ext)
            arr = [itemName, nextItemName]
            self.__account._doCmdStrArr(AccountCommands.CMD_VEHICLE_CHANGE_NATION, arr, proxy)
            return

    def obtainAll(self, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt2(AccountCommands.CMD_OBTAIN_ALL, 0, 0, proxy)
            return

    def obtainVehicle(self, name, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdStr(AccountCommands.CMD_OBTAIN_VEHICLE, name, proxy)
            return

    def equipOptDevsSequence(self, vehInvID, devices, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, '', {})
            return
        else:
            self.__account.shop.waitForSync(partial(self.__equipOptDevsSequenceOnShopSynced, vehInvID, devices, callback))
            return

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

    def __sellItemOnShopSynced(self, itemTypeIdx, itemInvID, count, callback, resultID, shopRev):
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

    def __sellMultipleItemsOnShopSynced(self, itemList, callback, resultID, shopRev):
        chunkSize = 80
        chunks = [ itemList[i:i + chunkSize] for i in xrange(0, len(itemList), chunkSize) ]
        results = {}
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:

                def proxy(requestID, resultID, errorStr, ext=None):
                    _logger.debug('sellMultipleItems callback(requestID=%d, resultID=%d, errorStr=%s', requestID, resultID, errorStr)
                    results[requestID] = resultID
                    if all((res is not None for res in results.itervalues())):
                        if all((AccountCommands.isCodeValid(res) for res in results.itervalues())):
                            callback(AccountCommands.RES_SUCCESS)
                        else:
                            callback(AccountCommands.RES_FAILURE)

            else:
                proxy = None
            for chunk in chunks:
                intArr = array('i', [shopRev] + list(chain(*chunk)))
                requestID = self.__account._doCmdIntArr(AccountCommands.CMD_SELL_MULTIPLE_ITEMS, intArr, proxy)
                results[requestID] = None
                _logger.debug('sellMultipleItems requestID: %d', requestID)

            return

    def __sellVehicleOnShopSynced(self, vehiclesSellData, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errStr=errorStr) if resultID < 0 else callback(resultID)
            else:
                proxy = None
            arr = [shopRev]
            for data in vehiclesSellData:
                vehInvID, flags, itemsFromVehicle, itemsFromInventory, customizationItems, itemsForDemountKit = data
                arr += [vehInvID, flags, len(itemsFromVehicle)] + itemsFromVehicle
                arr += [len(itemsFromInventory)] + itemsFromInventory
                arr += [len(customizationItems)] + customizationItems
                arr += [len(itemsForDemountKit)] + itemsForDemountKit

            self.__account._doCmdIntArr(AccountCommands.CMD_SELL_VEHICLE, arr, proxy)
            return

    def __dropSkillsTmanOnShopSynced(self, tmanInvID, dropSkillsCostIdx, callback, resultID, shopRev):
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

    def __respecTmanOnShopSynced(self, tmanInvID, vehTypeCompDescr, tmanCostTypeIdx, callback, resultID, shopRev):
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

    def __multiRespecTmanOnShopSynced(self, tmenInvIDsAndCostTypeIdx, vehTypeCompDescr, callback, resultID, shopRev):
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

    def __changeTankmanRoleOnShopSynced(self, tmanInvID, roleIdx, vehTypeCompDescr, callback, resultID, shopRev):
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

    def __replacePassportOnShopSynced(self, tmanInvID, isPremium, isFemale, fnGroupID, firstNameID, lnGroupID, lastNameID, iGroupID, iconID, callback, resultID, shopRev):
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

    def __freeXPToTankmanOnShopSynced(self, tmanInvID, freeXP, callback, resultID, shopRev):
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

    def __setAndFillLayoutsOnShopSynced(self, vehInvID, shellsLayout, equipmentType, eqsLayout, callback, resultID, shopRev):
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

    def __equipOptionDeviceOnShopSynced(self, vehInvID, deviceCompDescr, slotIdx, isAllSetups, isPaidRemoval, callback, useDemountKit, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext=None: callback(resultID, ext)
            else:
                proxy = None
            arr = [shopRev,
             vehInvID,
             deviceCompDescr,
             slotIdx,
             int(isAllSetups),
             int(isPaidRemoval),
             int(useDemountKit)]
            self.__account._doCmdIntArr(AccountCommands.CMD_EQUIP_OPTDEV, arr, proxy)
            return

    def __upgradeOptDevOnShopSynced(self, optDevID, vehInvID, setupIdx, slotIdx, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            arr = [shopRev,
             optDevID,
             vehInvID,
             setupIdx,
             slotIdx]
            self.__commandsProxy.perform(AccountCommands.CMD_UPGRADE_OPTDEV, arr, proxy)
            return

    def __equipOptDevsSequenceOnShopSynced(self, vehInvID, devices, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext=None: callback(resultID, ext)
            else:
                proxy = None
            arr = [shopRev, vehInvID, len(devices)]
            arr.extend(devices)
            self.__account._doCmdIntArr(AccountCommands.CMD_EQUIP_OPT_DEVS_SEQUENCE, arr, proxy)
            return

    def __setEquipmentSlotTypeOnShopSynched(self, vehInvID, slotID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__commandsProxy.perform(AccountCommands.CMD_SET_CUSTOM_ROLE_SLOT, shopRev, vehInvID, slotID, proxy)
            return

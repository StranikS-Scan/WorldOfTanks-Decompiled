# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/Inventory.py
# Compiled at: 2011-10-26 18:53:08
import AccountCommands
import items
import dossiers
import collections
from functools import partial
from AccountSyncData import synchronizeDicts
from PlayerEvents import g_playerEvents as events
from items import vehicles, tankmen
from constants import DOSSIER_TYPE
from AccountCommands import LOCK_REASON, SELL_VEHICLE_FLAG, VEHICLE_SETTINGS_FLAG
from debug_utils import *
from account_shared import AmmoIterator, getAmmoDiff
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

    def getItems(self, itemTypeIdx, callback):
        self.__syncData.waitForSync(partial(self.__onGetItemsResponse, itemTypeIdx, callback))

    def sell(self, itemTypeIdx, itemInvID, count, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        elif itemTypeIdx == _VEHICLE:
            self.sellVehicle(itemInvID, False, False, False, False, True, callback)
            return
        elif itemTypeIdx == _TANKMAN:
            if callback is not None:
                callback(AccountCommands.RES_WRONG_ARGS)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellItem_onShopSynced, itemTypeIdx, itemInvID, count, callback))
            return

    def sellVehicle(self, vehInvID, sellShells, sellEquipments, sellRmOptDevs, dismantleNonRmOptDevs, dismissCrew, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            flags = SELL_VEHICLE_FLAG.NONE
            if dismissCrew:
                flags |= SELL_VEHICLE_FLAG.CREW
            if sellShells:
                flags |= SELL_VEHICLE_FLAG.SHELLS
            if sellEquipments:
                flags |= SELL_VEHICLE_FLAG.EQS
            if sellRmOptDevs:
                flags |= SELL_VEHICLE_FLAG.RM_OPTIONAL_DEVICES
            if dismantleNonRmOptDevs:
                flags |= SELL_VEHICLE_FLAG.NONRM_OPTIONAL_DEVICES
            self.__account.shop.waitForSync(partial(self.__sellVehicle_onShopSynced, vehInvID, flags, callback))
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

    def equip(self, vehInvID, itemCompDescr, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0, [])
            return
        else:
            itemTypeIdx = vehicles.parseIntCompactDescr(itemCompDescr)[0]
            assert itemTypeIdx in (_CHASSIS,
             _GUN,
             _ENGINE,
             _FUEL_TANK,
             _RADIO)
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
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_EQUIP_OPTDEV, vehInvID, deviceCompDescr, slotIdx, int(isPaidRemoval), proxy)
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

    def dropTankmanSkill(self, tmanInvID, skillName, dropSkillCostIdx, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            skillIdx = tankmen.SKILL_INDICES[skillName]
            self.__account.shop.waitForSync(partial(self.__dropSkillTman_onShopSynced, tmanInvID, skillIdx, dropSkillCostIdx, callback))
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

    def replacePassport(self, tmanInvID, isFemale, firstNameID, lastNameID, iconID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__replacePassport_onShopSynced, tmanInvID, isFemale, firstNameID, lastNameID, iconID, callback))
            return

    def changeVehicleSetting(self, vehInvID, setting, isOn, callback):
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
            self.__account._doCmdInt3(AccountCommands.CMD_VEH_SETTINGS, vehInvID, setting, isOn, proxy)
            return

    def changeVehicleCamouflage(self, vehInvID, camouflageID, periodDays, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__changeVehCamouflage_onShopSynced, vehInvID, camouflageID, periodDays, callback))
            return

    def changeVehicleHorn(self, vehInvID, hornID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__changeVehHorn_onShopSynced, vehInvID, hornID, callback))
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

    def __onGetItemsResponse(self, itemTypeIdx, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            items = self.__cache.get(itemTypeIdx, None)
            if callback is not None:
                callback(resultID, items)
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

    def __sellVehicle_onShopSynced(self, vehInvID, flags, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_SELL_VEHICLE, shopRev, vehInvID, flags, proxy)
            return

    def __dropSkillTman_onShopSynced(self, tmanInvID, skillIdx, tmanCostTypeIdx, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_TMAN_DROP_SKILL, shopRev, tmanInvID, skillIdx, tmanCostTypeIdx, proxy)
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

    def __replacePassport_onShopSynced(self, tmanInvID, isFemale, firstNameID, lastNameID, iconID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            arr = [shopRev, tmanInvID]
            if isFemale is None:
                arr.append(-1)
            elif isFemale:
                arr.append(1)
            else:
                arr.append(0)
            arr.append(firstNameID if firstNameID is not None else -1)
            arr.append(lastNameID if lastNameID is not None else -1)
            arr.append(iconID if iconID is not None else -1)
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdIntArr(AccountCommands.CMD_TMAN_PASSPORT, arr, proxy)
            return

    def __changeVehCamouflage_onShopSynced(self, vehInvID, camouflageID, periodDays, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_VEH_CAMOUFLAGE, shopRev, vehInvID, camouflageID, periodDays, proxy)
            return

    def __changeVehHorn_onShopSynced(self, vehInvID, hornID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_VEH_HORN, shopRev, vehInvID, hornID, proxy)
            return

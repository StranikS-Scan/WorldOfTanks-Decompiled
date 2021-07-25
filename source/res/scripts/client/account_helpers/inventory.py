# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/Inventory.py
import collections
from array import array
from functools import partial
from itertools import chain
import logging
import typing
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

    def sellVehicle(self, vehiclesSellData, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__sellVehicle_onShopSynced, vehiclesSellData, callback))
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

    def equipCrewSkin(self, detInvID, skinID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__account._doCmdInt2(AccountCommands.CMD_DET_EQUIP_CREW_SKIN, detInvID, skinID, proxy)
            return

    def unequipCrewSkin(self, detInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__account._doCmdInt(AccountCommands.CMD_DET_UNEQUIP_CREW_SKIN, detInvID, proxy)
            return

    def useCrewBook(self, crewBookCD, detInvID, bookCount, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            self.__account._doCmdInt3(AccountCommands.CMD_LEARN_CREW_BOOK, crewBookCD, detInvID, bookCount, proxy)
            return

    def learnPerks(self, detachmentID, perks, dropMode, useRecertificationForm, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__learnPerks_onShopSynced, detachmentID, perks, dropMode, useRecertificationForm, callback))
            return

    def removeInstructorFromDetachment(self, detachmentID, slotID, optionID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__removeInstructorFromDetachment_onShopSynced, detachmentID, slotID, optionID, callback))
            return

    def recoverInstructor(self, instructorID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__recoverInstructor_onShopSynced, instructorID, callback))
            return

    def addInstructorToSlot(self, detachmentID, instructorID, slotID, isActive, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_ADD_INSTRUCTOR_TO_SLOT, detachmentID, instructorID, slotID, isActive, proxy)
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

    def equipOptionalDevice(self, vehInvID, deviceCompDescr, slotIdx, isPaidRemoval, callback, useDemountKit):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 0, [])
            return
        else:
            self.__account.shop.waitForSync(partial(self.__equipOptionDevice_onShopSynced, vehInvID, deviceCompDescr, slotIdx, isPaidRemoval, callback, useDemountKit))
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

    def loadCrew(self, vehInvID, crew, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, [])
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            availableRecruits = [ (slot, tman) for slot, tman in enumerate(crew) if tman is not None ]
            crewData = [vehInvID] + [ slotInfo for slot in availableRecruits for slotInfo in slot ]
            self.__account._doCmdIntArr(AccountCommands.CMD_SET_CREW, crewData, proxy)
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

    def freeXPToDetachment(self, detInvID, freeXP, callback):
        if self.__ignore:
            if callback is not None:
                callback('', AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__freeXPToDetachment_onShopSynced, detInvID, freeXP, callback))
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

            self.__account._doCmdIntArr(AccountCommands.CMD_DET_ADD_CREW_SKIN, skinList, proxy)
            return

    def upgradeOptDev(self, optDevID, vehInvID, slotIdx, callback=None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__upgradeOptDev_onShopSynced, optDevID, vehInvID, slotIdx, callback))
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

    def addOldTankmen(self):
        if self.__ignore:
            return
        else:
            self.__account._doCmdInt(AccountCommands.CMD_DBG_ADD_OLD_TANKMEN, 0, None)
            return

    def generateOldCrew(self, vehInvID, roleLevel):
        if self.__ignore:
            return
        else:
            self.__account._doCmdInt2(AccountCommands.CMD_DBG_GENERATE_OLD_CREW, vehInvID, roleLevel, None)
            return

    def resetDetachmentSellLimit(self):
        if self.__ignore:
            return
        else:
            self.__account._doCmdInt(AccountCommands.CMD_DBG_RESET_DETACHMENT_SELL_LIMIT, 0, None)
            return

    def addInstructorToken(self, presetName):
        if self.__ignore:
            return
        else:
            args = [1, -1, 0]
            self.__account._doCmdIntArrStrArr(AccountCommands.CMD_DBG_CREATED_INST_BY_PRESET, args, [presetName], None)
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
            self.__account.shop.waitForSync(partial(self.__equipOptDevsSequence_onShopSynced, vehInvID, devices, callback))
            return

    def createDetachment(self, vehInvID, assignToVehicle, detCompDescr, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt2Str(AccountCommands.CMD_CREATE_DETACHMENT_BY_VEHICLE, vehInvID, assignToVehicle, detCompDescr or '', proxy)
        return

    def demobilizeDetachment(self, detInvID, allowRemove, freeExcludeInstructors, callback):
        if self.__ignore:
            if callback is not None:
                callback('', AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__demobilizeDetachment_onShopSynced, detInvID, allowRemove, freeExcludeInstructors, callback))
            return

    def restoreDetachment(self, detInvID, clientSpecialTerm, callback):
        if self.__ignore:
            if callback is not None:
                callback('', AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__restoreDetachment_onShopSynced, detInvID, clientSpecialTerm, callback))
            return

    def specializeVehicleSlot(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, {})
            return
        else:
            self.__account.shop.waitForSync(partial(self.__specializeVehicleSlot_onShopSynced, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, callback))
            return

    def unlockVehicleSlot(self, detInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback('', AccountCommands.RES_NON_PLAYER)
            return
        else:
            self.__account.shop.waitForSync(partial(self.__unlockVehicleSlot_onShopSynced, detInvID, callback))
            return

    def specializeVehicleSlotAndAssign(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, {})
            return
        else:
            self.__account.shop.waitForSync(partial(self.__specializeVehicleSlotAndAssign_onShopSynced, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID, callback))
            return

    def unlockSpecializeVehicleSlotAndAssign(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID, callback):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, {})
            return
        else:
            self.__account.shop.waitForSync(partial(self.__unlockSpecializeVehicleSlotAndAssign_onShopSynced, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID, callback))
            return

    def convertVehicleCrewIntoDetachment(self, vehInvID, skinID, detCompDescr, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
        else:
            proxy = None
        self.__account._doCmdInt2Str(AccountCommands.CMD_CREW_CONVERT_INTO_DETACHMENT, vehInvID, skinID, detCompDescr, proxy)
        return

    def convertRecruitsIntoDetachment(self, recruitsInvIDs, skinID, vehCompDescr, detCompDescr, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
        else:
            proxy = None
        intArr = recruitsInvIDs + [skinID]
        strArr = [vehCompDescr, detCompDescr]
        self.__account._doCmdIntArrStrArr(AccountCommands.CMD_CONVERT_RECRUITS_INTO_DETACHMENT, intArr, strArr, proxy)
        return

    def changeDetachmentPassport(self, detInvID, gender, nameID, secondNameID, iconID, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        arr = [detInvID,
         gender,
         nameID,
         secondNameID,
         iconID]
        self.__account._doCmdIntArr(AccountCommands.CMD_CHANGE_CMDR_PASSPORT, arr, proxy)
        return

    def unpackedInstructor(self, instrInvID, nationID, professionID, perksIDs, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        intArr = [instrInvID, nationID, professionID]
        intArr.extend(perksIDs)
        self.__account._doCmdIntArr(AccountCommands.CMD_UNPACK_INSTRUCTOR, intArr, proxy)
        return

    def assignDetachmentToVehicle(self, detInvID, vehInvID, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt2(AccountCommands.CMD_ASSIGN_DETACHMENT_TO_VEHICLE, detInvID, vehInvID, proxy)
        return

    def detachmentResetVehicleLink(self, detInvID, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt(AccountCommands.CMD_RESET_DET_VEH_LINK, detInvID, proxy)
        return

    def detachmentSwapVehicleSlots(self, detInvID, slot1, slot2, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt3(AccountCommands.CMD_SWAP_DET_VEH_SLOTS, detInvID, slot1, slot2, proxy)
        return

    def moveInstructor(self, detInvID, slotID, steps, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt3(AccountCommands.CMD_MOVE_INSTRUCTOR, detInvID, slotID, steps, proxy)
        return

    def setActiveInstructorInDetachment(self, detInvID, instSlotId, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.__account._doCmdInt2(AccountCommands.CMD_SET_ACTIVE_INSTRUCTOR, detInvID, instSlotId, proxy)
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

    def __sellVehicle_onShopSynced(self, vehiclesSellData, callback, resultID, shopRev):
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
                vehInvID, isDismiss, allowRemove, freeExcInstructors, itemsFromVehicle, itemsFromInventory, customizationItems, itemsForDemountKit = data
                arr += [vehInvID,
                 isDismiss,
                 allowRemove,
                 freeExcInstructors,
                 len(itemsFromVehicle)] + itemsFromVehicle
                arr += [len(itemsFromInventory)] + itemsFromInventory
                arr += [len(customizationItems)] + customizationItems
                arr += [len(itemsForDemountKit)] + itemsForDemountKit

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

    def __freeXPToDetachment_onShopSynced(self, detInvID, freeXP, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback('', resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(errorStr, resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_TRAINING_DETACHMENT, shopRev, detInvID, freeXP, proxy)
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

    def __equipOptionDevice_onShopSynced(self, vehInvID, deviceCompDescr, slotIdx, isPaidRemoval, callback, useDemountKit, resultID, shopRev):
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
             int(isPaidRemoval),
             int(useDemountKit)]
            self.__account._doCmdIntArr(AccountCommands.CMD_EQUIP_OPTDEV, arr, proxy)
            return

    def __upgradeOptDev_onShopSynced(self, optDevID, vehInvID, slotIdx, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            proxy = None
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr)
            self.__commandsProxy.perform(AccountCommands.CMD_UPGRADE_OPTDEV, shopRev, optDevID, vehInvID, slotIdx, proxy)
            return

    def __equipOptDevsSequence_onShopSynced(self, vehInvID, devices, callback, resultID, shopRev):
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

    def __demobilizeDetachment_onShopSynced(self, detInvID, allowRemove, freeExcludeInstructors, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_DISSOLVE_DETACHMENT, shopRev, detInvID, int(allowRemove), int(freeExcludeInstructors), proxy)
            return

    def __restoreDetachment_onShopSynced(self, detInvID, clientSpecialTerm, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt3(AccountCommands.CMD_RESTORE_DETACHMENT, shopRev, detInvID, clientSpecialTerm, proxy)
            return

    def __specializeVehicleSlot_onShopSynced(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            else:
                proxy = None
            intArr = [shopRev,
             detInvID,
             slotIdx,
             vehCD,
             paymentOptionIdx,
             resetSkills]
            self.__account._doCmdIntArr(AccountCommands.CMD_SPECIALIZE_VEHICLE_SLOT, intArr, proxy)
            return

    def __learnPerks_onShopSynced(self, detachmentID, perks, dropMode, useRecertificationForm, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            perksArgs = [shopRev,
             detachmentID,
             dropMode,
             int(useRecertificationForm)]
            perksArgs.extend((item for pair in perks.iteritems() for item in pair))
            self.__account._doCmdIntArr(AccountCommands.CMD_ADD_PERK_TO_DETACHMENT, perksArgs, proxy)
            return

    def __unlockVehicleSlot_onShopSynced(self, detInvID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt2(AccountCommands.CMD_UNLOCK_VEHICLE_SLOT, shopRev, detInvID, proxy)
            return

    def __specializeVehicleSlotAndAssign_onShopSynced(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            else:
                proxy = None
            intArr = [shopRev,
             detInvID,
             slotIdx,
             vehCD,
             paymentOptionIdx,
             resetSkills,
             vehInvID]
            self.__account._doCmdIntArr(AccountCommands.CMD_SPECIALIZE_VEHICLE_SLOT_AND_ASSIGN, intArr, proxy)
            return

    def __unlockSpecializeVehicleSlotAndAssign_onShopSynced(self, detInvID, slotIdx, vehCD, paymentOptionIdx, resetSkills, vehInvID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, ext)
            else:
                proxy = None
            intArr = [shopRev,
             detInvID,
             slotIdx,
             vehCD,
             paymentOptionIdx,
             resetSkills,
             vehInvID]
            self.__account._doCmdIntArr(AccountCommands.CMD_UNLOCK_SPECIALIZE_VEHICLE_SLOT_AND_ASSIGN, intArr, proxy)
            return

    def __recoverInstructor_onShopSynced(self, instructorID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt2(AccountCommands.CMD_RECOVER_INSTRUCTOR, shopRev, instructorID, proxy)
            return

    def __removeInstructorFromDetachment_onShopSynced(self, detachmentID, slotID, optionID, callback, resultID, shopRev):
        if resultID < 0:
            if callback is not None:
                callback(resultID)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.__account._doCmdInt4(AccountCommands.CMD_REMOVE_INSTRUCTOR_FROM_SLOT, shopRev, detachmentID, slotID, optionID, proxy)
            return

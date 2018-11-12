# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/tankman.py
import BigWorld
from constants import EQUIP_TMAN_CODE
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.shared.formatters import formatPrice, formatPriceForCurrency, text_styles, icons
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman
from gui.shared.gui_items.processors import Processor, ItemProcessor, makeI18nSuccess, makeSuccess, makeI18nError, plugins
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from helpers import dependency
from gui import makeHtmlString
from items import tankmen, makeIntCompactDescrByID
from items.tankmen import SKILL_INDICES, SKILL_NAMES, getSkillsConfig
from skeletons.gui.game_control import IRestoreController

def _getSysMsgType(price):
    return CURRENCY_TO_SM_TYPE.get(price.getCurrency(byWeight=False), SM_TYPE.Information)


class TankmanDismiss(ItemProcessor):
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, tankman):
        vehicle = None
        if tankman.vehicleInvID > 0:
            vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
        confirmator = plugins.TankmanOperationConfirmator('protectedDismissTankman', tankman)
        super(TankmanDismiss, self).__init__(tankman, [plugins.TankmanLockedValidator(tankman), confirmator, plugins.VehicleValidator(vehicle, isEnabled=tankman.vehicleInvID > 0)])
        deletedTankmen = self.restore.getTankmenBeingDeleted()
        if deletedTankmen and tankman.isRestorable():
            self.addPlugin(plugins.BufferOverflowConfirmator({'dismissed': tankman,
             'deleted': deletedTankmen[0]}))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('dismiss_tankman/%s' % errStr, defaultSysMsgKey='dismiss_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('dismiss_tankman/success', type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to dismiss tankman:', self.item)
        BigWorld.player().inventory.dismissTankman(self.item.invID, lambda code: self._response(code, callback))


class TankmanRecruit(Processor):

    def __init__(self, nationID, vehTypeID, role, tmanCostTypeIdx):
        super(TankmanRecruit, self).__init__([plugins.VehicleCrewLockedValidator(self.itemsCache.items.getItemByCD(makeIntCompactDescrByID('vehicle', nationID, vehTypeID))),
         plugins.MoneyValidator(self.__getRecruitPrice(tmanCostTypeIdx)),
         plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0),
         plugins.BarracksSlotsValidator(),
         plugins.IsLongDisconnectedFromCenter()])
        self.nationID = nationID
        self.vehTypeID = vehTypeID
        self.role = role
        self.tmanCostTypeIdx = tmanCostTypeIdx

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('recruit_window/%s' % errStr, defaultSysMsgKey='recruit_window/server_error', auxData=ctx)

    def _successHandler(self, code, ctx=None):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        return makeI18nSuccess('recruit_window/financial_success', price=formatPrice(tmanCost), type=self.__getSysMsgType(), auxData=ctx) if tmanCost else makeI18nSuccess('recruit_window/success', type=self.__getSysMsgType(), auxData=ctx)

    def _request(self, callback):
        LOG_DEBUG('Make server request to recruit tankman:', self.nationID, self.vehTypeID, self.role, self.tmanCostTypeIdx)
        BigWorld.player().shop.buyTankman(self.nationID, self.vehTypeID, self.role, self.tmanCostTypeIdx, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))

    def __getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = self.itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return Money(credits=upgradeCost[Currency.CREDITS])
        return Money(gold=upgradeCost[Currency.GOLD]) if tmanCostTypeIdx == 2 else MONEY_UNDEFINED

    def __getSysMsgType(self):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        return CURRENCY_TO_SM_TYPE.get(tmanCost.getCurrency(byWeight=False), SM_TYPE.Information)


class TankmanTokenRecruit(Processor):

    def __init__(self, nationID, vehTypeID, role, tokenName, tokenData):
        vehicle = self.itemsCache.items.getItemByCD(makeIntCompactDescrByID('vehicle', nationID, vehTypeID))
        super(TankmanTokenRecruit, self).__init__([plugins.VehicleCrewLockedValidator(vehicle), plugins.IsLongDisconnectedFromCenter()])
        self.nationID = nationID
        self.vehTypeID = vehTypeID
        self.role = role
        self.tokenName = tokenName
        self.recruitInfo = tokenData
        self.vehicleName = vehicle.shortUserName

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('recruit_window/%s' % errStr, defaultSysMsgKey='recruit_window/server_error', auxData=ctx)

    def _successHandler(self, code, ctx=None):
        html = makeHtmlString(path='html_templates:lobby/processors/system_messages', key='recruit', ctx={'fullName': self.recruitInfo.getFullUserName(),
         'rank': Tankman.getRankUserName(self.nationID, self.recruitInfo.getRankID()),
         'role': getSkillsConfig().getSkill(self.role).userString,
         'vehicleName': self.vehicleName,
         'roleLevel': self.recruitInfo.getRoleLevel()})
        return makeSuccess(html, msgType=SM_TYPE.Information, auxData=ctx)

    def _request(self, callback):
        LOG_DEBUG('Make server request to recruit notrecruit tankman (by token):', self.nationID, self.vehTypeID, self.role)
        BigWorld.player().shop.buyTokenTankman(self.nationID, self.vehTypeID, self.role, self.tokenName, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))


class TankmanEquip(Processor):

    def __init__(self, tankman, vehicle, slot):
        super(TankmanEquip, self).__init__()
        self.tankman = tankman
        self.vehicle = vehicle
        self.slot = slot
        self.isReequip = False
        anotherTankman = dict(vehicle.crew).get(slot)
        if tankman is not None and anotherTankman is not None and anotherTankman.invID != tankman.invID:
            self.isReequip = True
        self.addPlugins((plugins.TankmanLockedValidator(tankman),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}),
         plugins.ModuleValidator(tankman),
         plugins.ModuleTypeValidator(tankman, (GUI_ITEM_TYPE.TANKMAN,))))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        prefix = self.__getSysMsgPrefix()
        return makeI18nError('%s/%s' % (prefix, errStr), defaultSysMsgKey='%s/server_error' % prefix)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('%s/success' % self.__getSysMsgPrefix(), type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to equip tankman:', self.tankman, self.vehicle, self.slot, self.isReequip)
        tmanInvID = None
        if self.tankman is not None:
            tmanInvID = self.tankman.invID
        BigWorld.player().inventory.equipTankman(self.vehicle.invID, self.slot, tmanInvID, lambda code: self._response(code, callback))
        return

    def __getSysMsgPrefix(self):
        return 'equip_tankman' if not self.isReequip else 'reequip_tankman'


class TankmanRecruitAndEquip(Processor):

    def __init__(self, vehicle, slot, tmanCostTypeIdx):
        super(TankmanRecruitAndEquip, self).__init__()
        self.vehicle = vehicle
        self.slot = slot
        self.tmanCostTypeIdx = tmanCostTypeIdx
        self.isReplace = dict(vehicle.crew).get(slot) is not None
        self.addPlugins((plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.MoneyValidator(self.__getRecruitPrice(tmanCostTypeIdx)),
         plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0),
         plugins.BarracksSlotsValidator(isEnabled=self.isReplace)))
        return

    def _request(self, callback):
        LOG_DEBUG('Make server request to buy and equip tankman:', self.vehicle, self.slot, self.tmanCostTypeIdx)
        BigWorld.player().shop.buyAndEquipTankman(self.vehicle.invID, self.slot, self.tmanCostTypeIdx, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))

    def _errorHandler(self, code, errStr='', ctx=None):
        prefix = self.__getSysMsgPrefix()
        return makeI18nError('%s/%s' % (prefix, errStr), defaultSysMsgKey='%s/server_error' % prefix, auxData=ctx)

    def _successHandler(self, code, ctx=None):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        prefix = self.__getSysMsgPrefix()
        sysMsgType = _getSysMsgType(tmanCost)
        return makeI18nSuccess('%s/financial_success' % prefix, price=formatPrice(tmanCost), type=sysMsgType, auxData=ctx) if tmanCost else makeI18nSuccess('%s/success' % prefix, type=sysMsgType, auxData=ctx)

    def __getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = self.itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return Money(credits=upgradeCost[Currency.CREDITS])
        return Money(gold=upgradeCost[Currency.GOLD]) if tmanCostTypeIdx == 2 else MONEY_UNDEFINED

    def __getSysMsgPrefix(self):
        return 'buy_and_equip_tankman' if not self.isReplace else 'buy_and_reequip_tankman'


class TankmanUnload(Processor):

    def __init__(self, vehicle, slot=-1):
        super(TankmanUnload, self).__init__()
        self.vehicle = vehicle
        self.slot = slot
        berthsNeeded = 1
        if slot == -1:
            berthsNeeded = len([ item for item in vehicle.crew if item[1] is not None ])
        self.__sysMsgPrefix = 'unload_tankman' if berthsNeeded == 1 else 'unload_crew'
        self.addPlugins([plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}), plugins.VehicleCrewLockedValidator(vehicle), plugins.BarracksSlotsValidator(berthsNeeded)])
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('%s/%s' % (self.__sysMsgPrefix, errStr), defaultSysMsgKey='%s/server_error' % self.__sysMsgPrefix)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('%s/success' % self.__sysMsgPrefix, type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Trying to unload tankman', self.vehicle, self.slot)
        BigWorld.player().inventory.equipTankman(self.vehicle.invID, self.slot, None, lambda code: self._response(code, callback))
        return


class TankmanReturn(Processor):

    def __init__(self, vehicle):
        self.__prefix = 'return_crew'
        self.__vehicle = vehicle
        super(TankmanReturn, self).__init__((plugins.VehicleValidator(self.__vehicle, False, prop={'isLocked': True}), plugins.VehicleCrewLockedValidator(vehicle)))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('%s/success' % self.__prefix, type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('%s/%s' % (self.__prefix, errStr), defaultSysMsgKey='%s/server_error' % self.__prefix)

    def _request(self, callback):
        LOG_DEBUG('Make server request to return crew. VehicleItem :', self.__vehicle)
        BigWorld.player().inventory.returnCrew(self.__vehicle.invID, lambda code: self._response(code, callback))


class TankmanRetraining(ItemProcessor):

    def __init__(self, tankman, vehicle, tmanCostTypeIdx):
        hasUndistributedExp = False
        isGoldPrice = tmanCostTypeIdx == 2
        if not isGoldPrice:
            canLearnSkills, lastSkillLevel = tankman.newSkillCount
            hasUndistributedExp = lastSkillLevel > 0 or canLearnSkills > 1
        self.vehicle = vehicle
        self.tmanCostTypeIdx = tmanCostTypeIdx
        self.tmanCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        ctx = {'tankname': vehicle.userName}
        if isGoldPrice:
            ctx['price'] = formatPrice(self.tmanCost, reverse=True, useIcon=True, useStyle=True)
        super(TankmanRetraining, self).__init__(tankman, (plugins.VehicleValidator(vehicle, False),
         plugins.TankmanLockedValidator(tankman),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleByGold', ctx=ctx, isEnabled=vehicle.isInInventory and isGoldPrice),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicleByGold', ctx=ctx, isEnabled=not vehicle.isInInventory and isGoldPrice),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicle', ctx=ctx, isEnabled=not vehicle.isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/undistributedExp', ctx=ctx, isEnabled=hasUndistributedExp)))

    def _getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = self.itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return Money(credits=upgradeCost[Currency.CREDITS])
        return Money(gold=upgradeCost[Currency.GOLD]) if tmanCostTypeIdx == 2 else MONEY_UNDEFINED

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('retraining_tankman/%s' % errStr, defaultSysMsgKey='retraining_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        sysMsgType = _getSysMsgType(self.tmanCost)
        return makeI18nSuccess('retraining_tankman/financial_success', price=formatPrice(self.tmanCost), type=sysMsgType, auxData=ctx) if self.tmanCost else makeI18nSuccess('retraining_tankman/success', type=sysMsgType, auxData=ctx)

    def _request(self, callback):
        LOG_DEBUG('Make server request to retrain Crew:', self.item, self.vehicle, self.tmanCostTypeIdx)
        BigWorld.player().inventory.respecTankman(self.item.invID, self.vehicle.intCD, self.tmanCostTypeIdx, lambda code: self._response(code, callback))


class TankmanCrewRetraining(Processor):

    def __init__(self, tmen, vehicle, tmanCostTypeIdx):
        hasUndistributedExp = False
        isGoldPrice = tmanCostTypeIdx == 2
        if not isGoldPrice:
            for tmanInvID in tmen:
                canLearnSkills, lastSkillLevel = self.itemsCache.items.getTankman(tmanInvID).newSkillCount
                hasUndistributedExp = lastSkillLevel > 0 or canLearnSkills > 1
                if hasUndistributedExp:
                    break

        self.tankmen = tmen
        self.vehicle = vehicle
        self.tmanCostTypeIdx = tmanCostTypeIdx
        ctx = {'tankname': vehicle.userName}
        if isGoldPrice:
            ctx['price'] = formatPrice(Money(gold=self.itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]['gold'] * len(self.tankmen)), reverse=True, useIcon=True, useStyle=True)
        super(TankmanCrewRetraining, self).__init__((plugins.VehicleValidator(vehicle, False),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.GroupOperationsValidator(tmen, tmanCostTypeIdx),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleByGold/pack', ctx=ctx, isEnabled=isGoldPrice and len(tmen) > 1),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleByGold', ctx=ctx, isEnabled=isGoldPrice and len(tmen) == 1),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicle', ctx=ctx, isEnabled=not vehicle.isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/undistributedExp', ctx=ctx, isEnabled=hasUndistributedExp)))

    def _errorHandler(self, code, errStr='', ctx=None):
        crewMembersCount = len(self.tankmen)
        messagePrefix = 'retraining_crew'
        if crewMembersCount == 1:
            messagePrefix = 'retraining_tankman'
        return makeI18nError('%s/%s' % (messagePrefix, errStr), defaultSysMsgKey='%s/server_error' % messagePrefix)

    def _successHandler(self, code, ctx=None):
        crewMembersCount = len(self.tankmen)
        messagePrefix = 'retraining_crew'
        if crewMembersCount == 1:
            messagePrefix = 'retraining_tankman'
        crewRetrainingCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        sysMsgType = _getSysMsgType(crewRetrainingCost)
        return makeI18nSuccess('%s/financial_success' % messagePrefix, type=sysMsgType, auxData=ctx, price=formatPrice(crewRetrainingCost)) if crewRetrainingCost else makeI18nSuccess('%s/success' % messagePrefix, type=sysMsgType, auxData=ctx)

    def _request(self, callback):
        LOG_DEBUG('Make server request to retrain Crew:', self.tankmen, self.vehicle, self.tmanCostTypeIdx)
        tMenInvIDsAndCostTypeIdx = []
        for tManInvID in self.tankmen:
            tMenInvIDsAndCostTypeIdx.append((tManInvID, self.tmanCostTypeIdx))

        BigWorld.player().inventory.multiRespecTankman(tMenInvIDsAndCostTypeIdx, self.vehicle.intCD, lambda code: self._response(code, callback))

    def _getRecruitPrice(self, tmanCostTypeIdx):
        crewMembersCount = len(self.tankmen)
        upgradeCost = self.itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        return crewMembersCount * Money(**upgradeCost)


class TankmanFreeToOwnXpConvertor(Processor):

    def __init__(self, tankman, selectedXpForConvert):
        super(TankmanFreeToOwnXpConvertor, self).__init__(())
        self.__tankman = tankman
        self.__selectedXpForConvert = selectedXpForConvert

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('free_xp_to_tman_skill/error/%s' % errStr, defaultSysMsgKey='free_xp_to_tman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('free_xp_to_tman_skill/success', freeXP=BigWorld.wg_getIntegralFormat(self.__selectedXpForConvert), type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Attempt to request server to exchange Free user XP to tankman XP', self.__tankman, self.__selectedXpForConvert)
        BigWorld.player().inventory.freeXPToTankman(self.__tankman.invID, self.__selectedXpForConvert, lambda errStr, code: self._response(code, callback, errStr=errStr))


class TankmanAddSkill(ItemProcessor):

    def __init__(self, tankman, skillName):
        super(TankmanAddSkill, self).__init__(tankman, (plugins.TankmanAddSkillValidator(tankman.descriptor, skillName),))
        self.skillName = skillName

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('add_tankman_skill/%s' % errStr, defaultSysMsgKey='add_tankman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('add_tankman_skill/success', type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to add tankman skill:', self.item, self.skillName)
        BigWorld.player().inventory.addTankmanSkill(self.item.invID, self.skillName, lambda code: self._response(code, callback))


class TankmanChangeRole(ItemProcessor):

    def __init__(self, tankman, role, vehTypeCompDescr):
        self.__roleIdx = SKILL_INDICES[role]
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__changeRoleCost = self.itemsCache.items.shop.changeRoleCost
        vehicle = self.itemsCache.items.getItemByCD(self.__vehTypeCompDescr)
        super(TankmanChangeRole, self).__init__(tankman, (plugins.TankmanLockedValidator(tankman),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.MessageConfirmator('tankmanChageRole/unknownVehicle', ctx={'tankname': vehicle.userName}, isEnabled=not vehicle.isInInventory),
         plugins.VehicleValidator(vehicle, False),
         plugins.VehicleRoleValidator(vehicle, role, tankman),
         plugins.MoneyValidator(Money(gold=self.__changeRoleCost))))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('change_tankman_role/%s' % errStr, defaultSysMsgKey='change_tankman_role/server_error')

    def _successHandler(self, code, ctx=None):
        msgType = SM_TYPE.FinancialTransactionWithGold
        vehicle = self.itemsCache.items.getItemByCD(self.__vehTypeCompDescr)
        if ctx == EQUIP_TMAN_CODE.OK:
            auxData = makeI18nSuccess('change_tankman_role/installed', vehicle=vehicle.shortUserName)
        elif ctx == EQUIP_TMAN_CODE.NO_FREE_SLOT:
            roleStr = Tankman.getRoleUserName(SKILL_NAMES[self.__roleIdx])
            auxData = makeI18nSuccess('change_tankman_role/slot_is_taken', vehicle=vehicle.shortUserName, role=roleStr)
        else:
            auxData = makeI18nSuccess('change_tankman_role/no_vehicle')
        return makeI18nSuccess('change_tankman_role/success', money=formatPrice(Money(gold=self.__changeRoleCost)), type=msgType, auxData=auxData)

    def _request(self, callback):
        LOG_DEBUG('Make server request to change tankman role:', self.item, self.__roleIdx, self.__vehTypeCompDescr)
        BigWorld.player().inventory.changeTankmanRole(self.item.invID, self.__roleIdx, self.__vehTypeCompDescr, lambda code, ext: self._response(code, callback, ctx=ext))


class TankmanDropSkills(ItemProcessor):

    def __init__(self, tankman, dropSkillCostIdx):
        super(TankmanDropSkills, self).__init__(tankman, (plugins.MessageConfirmator('dropSkill'), plugins.TankmanDropSkillValidator(tankman, True)))
        self.dropSkillCostIdx = dropSkillCostIdx

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('drop_tankman_skill/%s' % errStr, defaultSysMsgKey='drop_tankman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        msgType = self.__getTankmanSysMsgType(self.dropSkillCostIdx)
        price = self.itemsCache.items.shop.dropSkillsCost.get(self.dropSkillCostIdx)
        return makeI18nSuccess('drop_tankman_skill/success', money=formatPrice(Money(**price)), type=msgType)

    def _request(self, callback):
        LOG_DEBUG('Make server request to drop tankman skills:', self.item, self.dropSkillCostIdx)
        BigWorld.player().inventory.dropTankmanSkills(self.item.invID, self.dropSkillCostIdx, lambda code: self._response(code, callback))

    def __getTankmanSysMsgType(self, dropSkillCostIdx):
        if dropSkillCostIdx == 1:
            return SM_TYPE.FinancialTransactionWithCredits
        return SM_TYPE.FinancialTransactionWithGold if dropSkillCostIdx == 2 else SM_TYPE.Information


class TankmanChangePassport(ItemProcessor):

    def __init__(self, tankman, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):
        hasUniqueData = self.__hasUniqueData(tankman, firstNameID, lastNameID, iconID)
        isFemale = tankman.descriptor.isFemale
        if isFemale:
            price = self.itemsCache.items.shop.passportFemaleChangeCost
        else:
            price = self.itemsCache.items.shop.passportChangeCost
        super(TankmanChangePassport, self).__init__(tankman, (plugins.TankmanChangePassportValidator(tankman), plugins.MessageConfirmator('replacePassport/unique' if hasUniqueData else 'replacePassportConfirmation', ctx={Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(BigWorld.wg_getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})))
        self.firstNameID = firstNameID
        self.firstNameGroup = firstNameGroup
        self.lastNameID = lastNameID
        self.lastNameGroup = lastNameGroup
        self.iconID = iconID
        self.iconGroup = iconGroup
        self.isFemale = isFemale
        self.isPremium = tankman.descriptor.isPremium
        self.price = price

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('replace_tankman/%s' % errStr, defaultSysMsgKey='replace_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('replace_tankman/success', money=formatPrice(Money(gold=self.price)), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        LOG_DEBUG('Make server request to change tankman passport:', self.item.invID, self.isPremium, self.isFemale, self.firstNameGroup, self.firstNameID, self.lastNameGroup, self.lastNameID)
        BigWorld.player().inventory.replacePassport(self.item.invID, self.isPremium, self.isFemale, self.firstNameGroup, self.firstNameID, self.lastNameGroup, self.lastNameID, self.iconGroup, self.iconID, lambda code: self._response(code, callback))

    @classmethod
    def __hasUniqueData(cls, tankman, firstNameID, lastNameID, iconID):
        tDescr = tankman.descriptor
        nationConfig = tankmen.getNationConfig(tankman.nationID)
        for group in nationConfig.normalGroups:
            if group.notInShop:
                if tDescr.firstNameID != firstNameID and firstNameID is not None and tDescr.firstNameID in group.firstNamesList or tDescr.lastNameID != lastNameID and lastNameID is not None and tDescr.lastNameID in group.lastNamesList or tDescr.iconID != iconID and iconID is not None and tDescr.iconID in group.iconsList:
                    return True

        return False


class TankmanRestore(ItemProcessor):

    def __init__(self, tankman):
        self.__tankman = tankman
        restorePrice, _ = getTankmenRestoreInfo(tankman)
        super(TankmanRestore, self).__init__(tankman, (plugins.TankmanLockedValidator(tankman),
         plugins.TankmanOperationConfirmator('restoreTankman', tankman),
         plugins.BarracksSlotsValidator(berthsNeeded=1),
         plugins.MoneyValidator(restorePrice),
         plugins.IsLongDisconnectedFromCenter()))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('restore_tankman/%s' % errStr, defaultSysMsgKey='restore_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        restorePrice, _ = getTankmenRestoreInfo(self.__tankman)
        if restorePrice:
            currency = restorePrice.getCurrency()
            return makeI18nSuccess('restore_tankman/financial_success', type=_getSysMsgType(restorePrice), money=formatPriceForCurrency(restorePrice, currency))
        return makeI18nSuccess('restore_tankman/success', type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to restore tankman:', self.item)
        BigWorld.player().recycleBin.restoreTankman(abs(self.item.invID), lambda code, errStr: self._response(code, callback, errStr=errStr))

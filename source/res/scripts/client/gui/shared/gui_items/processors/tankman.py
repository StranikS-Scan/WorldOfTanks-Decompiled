# Embedded file name: scripts/client/gui/shared/gui_items/processors/tankman.py
import BigWorld
from constants import EQUIP_TMAN_CODE
from debug_utils import LOG_DEBUG
from items import tankmen
from items.tankmen import SKILL_INDICES, getSkillsConfig, SKILL_NAMES
from gui.SystemMessages import SM_TYPE
from gui.shared import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman
from gui.shared.gui_items.processors import Processor, ItemProcessor, makeI18nSuccess, makeI18nError, plugins
from gui.shared.formatters import formatPrice

class TankmanDismiss(ItemProcessor):

    def __init__(self, tankman):
        vehicle = None
        if tankman.vehicleInvID > 0:
            vehicle = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
        confirmatorType = plugins.DismissTankmanConfirmator('protectedDismissTankman', tankman)
        raise confirmatorType or AssertionError
        super(TankmanDismiss, self).__init__(tankman, [confirmatorType, plugins.VehicleValidator(vehicle, isEnabled=tankman.vehicleInvID > 0)])
        return

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('dismiss_tankman/%s' % errStr)
        return makeI18nError('dismiss_tankman/server_error')

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('dismiss_tankman/success', type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to dismiss tankman:', self.item)
        BigWorld.player().inventory.dismissTankman(self.item.invID, lambda code: self._response(code, callback))


class TankmanRecruit(Processor):

    def __init__(self, nationID, vehTypeID, role, tmanCostTypeIdx):
        super(TankmanRecruit, self).__init__([plugins.MoneyValidator(self.__getRecruitPrice(tmanCostTypeIdx)), plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0), plugins.BarracksSlotsValidator()])
        self.nationID = nationID
        self.vehTypeID = vehTypeID
        self.role = role
        self.tmanCostTypeIdx = tmanCostTypeIdx

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('recruit_window/%s' % errStr)
        return makeI18nError('recruit_window/server_error', auxData=ctx)

    def _successHandler(self, code, ctx = None):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        if tmanCost[0] > 0 or tmanCost[1] > 0:
            return makeI18nSuccess('recruit_window/financial_success', price=formatPrice(tmanCost), type=self.__getSysMsgType(), auxData=ctx)
        return makeI18nSuccess('recruit_window/success', type=self.__getSysMsgType(), auxData=ctx)

    def _request(self, callback):
        LOG_DEBUG('Make server request to recruit tankman:', self.nationID, self.vehTypeID, self.role, self.tmanCostTypeIdx)
        BigWorld.player().shop.buyTankman(self.nationID, self.vehTypeID, self.role, self.tmanCostTypeIdx, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))

    def __getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = g_itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return (upgradeCost['credits'], 0)
        if tmanCostTypeIdx == 2:
            return (0, upgradeCost['gold'])
        return (0, 0)

    def __getSysMsgType(self):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        if tmanCost[0] > 0:
            return SM_TYPE.PurchaseForCredits
        if tmanCost[1] > 0:
            return SM_TYPE.PurchaseForGold
        return SM_TYPE.Information


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
        self.addPlugins([plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}), plugins.ModuleValidator(tankman), plugins.ModuleTypeValidator(tankman, (GUI_ITEM_TYPE.TANKMAN,))])
        return

    def _errorHandler(self, code, errStr = '', ctx = None):
        prefix = self.__getSysMsgPrefix()
        if len(errStr):
            return makeI18nError('%s/%s' % (prefix, errStr))
        return makeI18nError('%s/server_error' % prefix)

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('%s/success' % self.__getSysMsgPrefix(), type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to equip tankman:', self.tankman, self.vehicle, self.slot, self.isReequip)
        tmanInvID = None
        if self.tankman is not None:
            tmanInvID = self.tankman.invID
        BigWorld.player().inventory.equipTankman(self.vehicle.invID, self.slot, tmanInvID, lambda code: self._response(code, callback))
        return

    def __getSysMsgPrefix(self):
        if not self.isReequip:
            return 'equip_tankman'
        return 'reequip_tankman'


class TankmanRecruitAndEquip(Processor):

    def __init__(self, vehicle, slot, tmanCostTypeIdx):
        super(TankmanRecruitAndEquip, self).__init__()
        self.vehicle = vehicle
        self.slot = slot
        self.tmanCostTypeIdx = tmanCostTypeIdx
        self.isReplace = dict(vehicle.crew).get(slot) is not None
        self.addPlugins([plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}),
         plugins.MoneyValidator(self.__getRecruitPrice(tmanCostTypeIdx)),
         plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0),
         plugins.BarracksSlotsValidator(isEnabled=self.isReplace)])
        return

    def _request(self, callback):
        LOG_DEBUG('Make server request to buy and equip tankman:', self.vehicle, self.slot, self.tmanCostTypeIdx)
        BigWorld.player().shop.buyAndEquipTankman(self.vehicle.invID, self.slot, self.tmanCostTypeIdx, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))

    def _errorHandler(self, code, errStr = '', ctx = None):
        prefix = self.__getSysMsgPrefix()
        if len(errStr):
            return makeI18nError('%s/%s' % (prefix, errStr))
        return makeI18nError('%s/server_error' % prefix, auxData=ctx)

    def _successHandler(self, code, ctx = None):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        prefix = self.__getSysMsgPrefix()
        if tmanCost[0] > 0 or tmanCost[1] > 0:
            return makeI18nSuccess('%s/financial_success' % prefix, price=formatPrice(tmanCost), type=self.__getSysMsgType(), auxData=ctx)
        return makeI18nSuccess('%s/success' % prefix, type=self.__getSysMsgType(), auxData=ctx)

    def __getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = g_itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return (upgradeCost['credits'], 0)
        if tmanCostTypeIdx == 2:
            return (0, upgradeCost['gold'])
        return (0, 0)

    def __getSysMsgType(self):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        if tmanCost[0] > 0:
            return SM_TYPE.PurchaseForCredits
        if tmanCost[1] > 0:
            return SM_TYPE.PurchaseForGold
        return SM_TYPE.Information

    def __getSysMsgPrefix(self):
        if not self.isReplace:
            return 'buy_and_equip_tankman'
        return 'buy_and_reequip_tankman'


class TankmanUnload(Processor):

    def __init__(self, vehicle, slot = -1):
        """
        Ctor.
        
        @param vehicle: vehicle to unload tankman
        @param slot:    slot in given vehicle to unload. -1 by default,
                                        that means - unload all tankmen from vehicle.
        """
        super(TankmanUnload, self).__init__()
        self.vehicle = vehicle
        self.slot = slot
        berthsNeeded = 1
        if slot == -1:
            berthsNeeded = len(filter(lambda (role, t): t is not None, vehicle.crew))
        self.__sysMsgPrefix = 'unload_tankman' if berthsNeeded == 1 else 'unload_crew'
        self.addPlugins([plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}), plugins.BarracksSlotsValidator(berthsNeeded)])

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('%s/%s' % (self.__sysMsgPrefix, errStr))
        return makeI18nError('%s/server_error' % self.__sysMsgPrefix)

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('%s/success' % self.__sysMsgPrefix, type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to unload tankman:', self.vehicle, self.slot)
        BigWorld.player().inventory.equipTankman(self.vehicle.invID, self.slot, None, lambda code: self._response(code, callback))
        return


class TankmanReturn(Processor):

    def __init__(self, vehicle):
        self.__prefix = 'return_crew'
        self.__vehicle = vehicle
        super(TankmanReturn, self).__init__([plugins.VehicleValidator(self.__vehicle, False, prop={'isLocked': True})])

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('%s/success' % self.__prefix, type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('%s/%s' % (self.__prefix, errStr))
        return makeI18nError('%s/server_error' % self.__prefix)

    def _request(self, callback):
        LOG_DEBUG('Make server request to return crew. VehicleItem :', self.__vehicle)
        BigWorld.player().inventory.returnCrew(self.__vehicle.invID, lambda code: self._response(code, callback))


class TankmanRetraining(ItemProcessor):

    def __init__(self, tankman, vehicle, tmanCostTypeIdx):
        super(TankmanRetraining, self).__init__(tankman, (plugins.VehicleValidator(vehicle, False), plugins.MessageConfirmator('tankmanRetraining/unknownVehicle', ctx={'tankname': vehicle.userName}, isEnabled=not vehicle.isInInventory)))
        self.vehicle = vehicle
        self.tmanCostTypeIdx = tmanCostTypeIdx

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            makeI18nError('retraining_tankman/%s' % errStr)
        return makeI18nError('retraining_tankman/server_error')

    def _successHandler(self, code, ctx = None):
        tmanCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        if tmanCost[0] > 0 or tmanCost[1] > 0:
            return makeI18nSuccess('retraining_tankman/financial_success', price=formatPrice(tmanCost), type=self._getSysMsgType(), auxData=ctx)
        return makeI18nSuccess('retraining_tankman/success', type=self._getSysMsgType(), auxData=ctx)

    def _getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = g_itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return (upgradeCost['credits'], 0)
        if tmanCostTypeIdx == 2:
            return (0, upgradeCost['gold'])
        return (0, 0)

    def _getSysMsgType(self):
        tmanCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        if tmanCost[0] > 0:
            return SM_TYPE.PurchaseForCredits
        if tmanCost[1] > 0:
            return SM_TYPE.PurchaseForGold
        return SM_TYPE.Information

    def _request(self, callback):
        LOG_DEBUG('Make server request to retrain Crew:', self.item, self.vehicle, self.tmanCostTypeIdx)
        BigWorld.player().inventory.respecTankman(self.item.invID, self.vehicle.intCD, self.tmanCostTypeIdx, lambda code: self._response(code, callback))


class TankmanCrewRetraining(Processor):

    def __init__(self, tankmen, vehicle, tmanCostTypeIdx):
        super(TankmanCrewRetraining, self).__init__((plugins.VehicleValidator(vehicle, False), plugins.GroupOperationsValidator(tankmen, tmanCostTypeIdx), plugins.MessageConfirmator('tankmanRetraining/unknownVehicle', ctx={'tankname': vehicle.userName}, isEnabled=not vehicle.isInInventory)))
        self.tankmen = tankmen
        self.vehicle = vehicle
        self.tmanCostTypeIdx = tmanCostTypeIdx

    def _errorHandler(self, code, errStr = '', ctx = None):
        crewMembersCount = len(self.tankmen)
        messagePrefix = 'retraining_crew'
        if crewMembersCount == 1:
            messagePrefix = 'retraining_tankman'
        if len(errStr):
            return makeI18nError('%s/%s' % (messagePrefix, errStr))
        return makeI18nError('%s/server_error' % messagePrefix)

    def _successHandler(self, code, ctx = None):
        crewMembersCount = len(self.tankmen)
        messagePrefix = 'retraining_crew'
        if crewMembersCount == 1:
            messagePrefix = 'retraining_tankman'
        crewRetrainingCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        if crewRetrainingCost[0] > 0 or crewRetrainingCost[1] > 0:
            return makeI18nSuccess('%s/financial_success' % messagePrefix, type=self._getSysMsgType(), auxData=ctx, price=formatPrice(crewRetrainingCost))
        return makeI18nSuccess('%s/success' % messagePrefix, type=self._getSysMsgType(), auxData=ctx)

    def _request(self, callback):
        LOG_DEBUG('Make server request to retrain Crew:', self.tankmen, self.vehicle, self.tmanCostTypeIdx)
        tMenInvIDsAndCostTypeIdx = []
        for tManInvID in self.tankmen:
            tMenInvIDsAndCostTypeIdx.append((tManInvID, self.tmanCostTypeIdx))

        BigWorld.player().inventory.multiRespecTankman(tMenInvIDsAndCostTypeIdx, self.vehicle.intCD, lambda code: self._response(code, callback))

    def _getRecruitPrice(self, tmanCostTypeIdx):
        crewMembersCount = len(self.tankmen)
        upgradeCost = g_itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        return (upgradeCost['credits'] * crewMembersCount, upgradeCost['gold'] * crewMembersCount)

    def _getSysMsgType(self):
        tmanCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        if tmanCost[0] > 0:
            return SM_TYPE.PurchaseForCredits
        if tmanCost[1] > 0:
            return SM_TYPE.PurchaseForGold
        return SM_TYPE.Information


class TankmanFreeToOwnXpConvertor(Processor):

    def __init__(self, tankman, selectedXpForConvert):
        super(TankmanFreeToOwnXpConvertor, self).__init__([])
        self.__tankman = tankman
        self.__selectedXpForConvert = selectedXpForConvert

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('free_xp_to_tman_skill/error/%s' % errStr)
        return makeI18nError('free_xp_to_tman_skill/server_error')

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('free_xp_to_tman_skill/success', freeXP=BigWorld.wg_getIntegralFormat(self.__selectedXpForConvert), type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Attempt to request server to exchange Free user XP to tankman XP', self.__tankman, self.__selectedXpForConvert)
        BigWorld.player().inventory.freeXPToTankman(self.__tankman.invID, self.__selectedXpForConvert, lambda errStr, code: self._response(code, callback, errStr=errStr))


class TankmanAddSkill(ItemProcessor):

    def __init__(self, tankman, skillName):
        super(TankmanAddSkill, self).__init__(tankman)
        self.skillName = skillName

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('add_tankman_skill/%s' % errStr)
        return makeI18nError('add_tankman_skill/server_error')

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('add_tankman_skill/success', type=SM_TYPE.Information)

    def _request(self, callback):
        LOG_DEBUG('Make server request to add tankman skill:', self.item, self.skillName)
        BigWorld.player().inventory.addTankmanSkill(self.item.invID, self.skillName, lambda code: self._response(code, callback))


class TankmanChangeRole(ItemProcessor):

    def __init__(self, tankman, role, vehTypeCompDescr):
        self.__roleIdx = SKILL_INDICES[role]
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__changeRoleCost = g_itemsCache.items.shop.changeRoleCost
        vehicle = g_itemsCache.items.getItemByCD(self.__vehTypeCompDescr)
        super(TankmanChangeRole, self).__init__(tankman, [plugins.MessageConfirmator('tankmanChageRole/unknownVehicle', ctx={'tankname': vehicle.userName}, isEnabled=not vehicle.isInInventory),
         plugins.VehicleValidator(vehicle, False),
         plugins.VehicleRoleValidator(vehicle, role),
         plugins.MoneyValidator((0, self.__changeRoleCost))])

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('change_tankman_role/%s' % errStr)
        return makeI18nError('change_tankman_role/server_error')

    def _successHandler(self, code, ctx = None):
        msgType = SM_TYPE.FinancialTransactionWithGold
        vehicle = g_itemsCache.items.getItemByCD(self.__vehTypeCompDescr)
        if ctx == EQUIP_TMAN_CODE.OK:
            auxData = makeI18nSuccess('change_tankman_role/installed', vehicle=vehicle.shortUserName)
        elif ctx == EQUIP_TMAN_CODE.NO_FREE_SLOT:
            roleStr = Tankman.getRoleUserName(SKILL_NAMES[self.__roleIdx])
            auxData = makeI18nSuccess('change_tankman_role/slot_is_taken', vehicle=vehicle.shortUserName, role=roleStr)
        else:
            auxData = makeI18nSuccess('change_tankman_role/no_vehicle')
        return makeI18nSuccess('change_tankman_role/success', money=formatPrice((0, self.__changeRoleCost)), type=msgType, auxData=auxData)

    def _request(self, callback):
        LOG_DEBUG('Make server request to change tankman role:', self.item, self.__roleIdx, self.__vehTypeCompDescr)
        BigWorld.player().inventory.changeTankmanRole(self.item.invID, self.__roleIdx, self.__vehTypeCompDescr, lambda code, ext: self._response(code, callback, ctx=ext))


class TankmanDropSkills(ItemProcessor):

    def __init__(self, tankman, dropSkillCostIdx):
        super(TankmanDropSkills, self).__init__(tankman, (plugins.MessageConfirmator('dropSkill'),))
        self.dropSkillCostIdx = dropSkillCostIdx

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('drop_tankman_skill/%s' % errStr)
        return makeI18nError('drop_tankman_skill/server_error')

    def _successHandler(self, code, ctx = None):
        msgType = self.__getTankmanSysMsgType(self.dropSkillCostIdx)
        price = g_itemsCache.items.shop.dropSkillsCost.get(self.dropSkillCostIdx)
        return makeI18nSuccess('drop_tankman_skill/success', money=formatPrice((price['credits'], price['gold'])), type=msgType)

    def _request(self, callback):
        LOG_DEBUG('Make server request to drop tankman skills:', self.item, self.dropSkillCostIdx)
        BigWorld.player().inventory.dropTankmanSkills(self.item.invID, self.dropSkillCostIdx, lambda code: self._response(code, callback))

    def __getTankmanSysMsgType(self, dropSkillCostIdx):
        if dropSkillCostIdx == 1:
            return SM_TYPE.FinancialTransactionWithCredits
        if dropSkillCostIdx == 2:
            return SM_TYPE.FinancialTransactionWithGold
        return SM_TYPE.Information


class TankmanChangePassport(ItemProcessor):

    def __init__(self, tankman, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):
        hasUniqueData = self.__hasUniqueData(tankman, firstNameID, lastNameID, iconID)
        super(TankmanChangePassport, self).__init__(tankman, (plugins.MessageConfirmator('replacePassport/unique' if hasUniqueData else 'replacePassportConfirmation'),))
        self.firstNameID = firstNameID
        self.firstNameGroup = firstNameGroup
        self.lastNameID = lastNameID
        self.lastNameGroup = lastNameGroup
        self.iconID = iconID
        self.iconGroup = iconGroup
        self.isFemale = tankman.descriptor.isFemale
        self.isPremium = tankman.descriptor.isPremium

    def _errorHandler(self, code, errStr = '', ctx = None):
        return makeI18nError('replace_tankman/server_error')

    def _successHandler(self, code, ctx = None):
        if self.isFemale:
            goldPrice = g_itemsCache.items.shop.passportFemaleChangeCost
        else:
            goldPrice = g_itemsCache.items.shop.passportChangeCost
        return makeI18nSuccess('replace_tankman/success', money=formatPrice((0, goldPrice)), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        LOG_DEBUG('Make server request to change tankman passport:', self.item.invID, self.isPremium, self.isFemale, self.firstNameGroup, self.firstNameID, self.lastNameGroup, self.lastNameID)
        BigWorld.player().inventory.replacePassport(self.item.invID, self.isPremium, self.isFemale, self.firstNameGroup, self.firstNameID, self.lastNameGroup, self.lastNameID, self.iconGroup, self.iconID, lambda code: self._response(code, callback))

    @classmethod
    def __hasUniqueData(cls, tankman, firstNameID, lastNameID, iconID):
        tDescr = tankman.descriptor
        nationConfig = tankmen.getNationConfig(tankman.nationID)
        for group in nationConfig['normalGroups']:
            if group.get('notInShop'):
                if tDescr.firstNameID != firstNameID and firstNameID is not None and tDescr.firstNameID in group['firstNamesList'] or tDescr.lastNameID != lastNameID and lastNameID is not None and tDescr.lastNameID in group['lastNamesList'] or tDescr.iconID != iconID and iconID is not None and tDescr.iconID in group['iconsList']:
                    return True

        return False

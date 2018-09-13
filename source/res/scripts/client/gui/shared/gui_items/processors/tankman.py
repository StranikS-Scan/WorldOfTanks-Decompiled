# Embedded file name: scripts/client/gui/shared/gui_items/processors/tankman.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui.SystemMessages import SM_TYPE
from gui.shared import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import Processor, ItemProcessor, makeI18nSuccess, makeI18nError, plugins
from gui.shared.utils.gui_items import formatPrice

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


class TankmanReturn(TankmanUnload):

    def __init__(self, vehicle):
        self.__prefix = 'return_crew'
        super(TankmanReturn, self).__init__(vehicle, -1)
        self.addPlugins([plugins.VehicleValidator(vehicle, False, prop={'isLocked': True})])

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('%s/success' % self.__prefix, type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('%s/%s' % (self.__prefix, errStr))
        return makeI18nError('%s/server_error' % self.__prefix)

    def _request(self, callback):
        LOG_DEBUG('Make server request to return crew:', self.vehicle, self.slot)
        BigWorld.player().inventory.returnCrew(self.vehicle.invID, lambda code: self._response(code, callback))


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

    def __init__(self, tankman, firstNameID, lastNameID, iconID, isFemale = False):
        super(TankmanChangePassport, self).__init__(tankman, (plugins.MessageConfirmator('replacePassportConfirmation'),))
        self.firstNameID = firstNameID
        self.lastNameID = lastNameID
        self.iconID = iconID
        self.isFemale = isFemale

    def _errorHandler(self, code, errStr = '', ctx = None):
        return makeI18nError('replace_tankman/server_error')

    def _successHandler(self, code, ctx = None):
        goldPrice = g_itemsCache.items.shop.passportChangeCost
        return makeI18nSuccess('replace_tankman/success', money=formatPrice((0, goldPrice)), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        LOG_DEBUG('Make server request to change tankman passport:', self.item, self.firstNameID, self.lastNameID, self.iconID, self.isFemale)
        BigWorld.player().inventory.replacePassport(self.item.invID, self.isFemale, self.firstNameID, self.lastNameID, self.iconID, lambda code: self._response(code, callback))

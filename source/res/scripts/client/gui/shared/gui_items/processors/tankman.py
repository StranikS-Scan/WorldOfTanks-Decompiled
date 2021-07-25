# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/tankman.py
import logging
import BigWorld
from gui.impl import backport
from CurrentVehicle import g_currentVehicle
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.shared.formatters import formatPrice, formatPriceForCurrency
from gui.shared.gui_items import GUI_ITEM_TYPE, Tankman
from gui.shared.gui_items.processors import Processor, ItemProcessor, makeI18nSuccess, makeSuccess, makeI18nError, plugins
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from helpers import dependency
from gui import makeHtmlString
from items import tankmen, makeIntCompactDescrByID
from items.tankmen import SKILL_INDICES, getSkillsConfig
from skeletons.gui.game_control import IRestoreController
_logger = logging.getLogger(__name__)

def _getSysMsgType(price):
    return CURRENCY_TO_SM_TYPE.get(price.getCurrency(byWeight=False), SM_TYPE.Information)


class TankmanDismiss(ItemProcessor):
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, tankman):
        vehicle = None
        if tankman.vehicleInvID > 0:
            vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
        confirmator = plugins.TankmanOperationConfirmator('protectedDismissTankman', tankman)
        super(TankmanDismiss, self).__init__(tankman, [plugins.Development(),
         plugins.TankmanLockedValidator(tankman),
         confirmator,
         plugins.VehicleValidator(vehicle, isEnabled=tankman.vehicleInvID > 0)])
        deletedTankmen = self.restore.getTankmenBeingDeleted()
        if deletedTankmen and tankman.isRestorable():
            self.addPlugin(plugins.BufferOverflowConfirmator({'dismissed': tankman,
             'deleted': deletedTankmen[0]}))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='dismiss_tankman/{}'.format(errStr), defaultSysMsgKey='dismiss_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('dismiss_tankman/success', type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to dismiss tankman: %s', self.item)
        BigWorld.player().inventory.dismissTankman(self.item.invID, lambda code: self._response(code, callback))


class TankmanRecruit(Processor):

    def __init__(self, nationID, vehTypeID, role, tmanCostTypeIdx):
        super(TankmanRecruit, self).__init__([plugins.Development(),
         plugins.VehicleCrewLockedValidator(self.itemsCache.items.getItemByCD(makeIntCompactDescrByID('vehicle', nationID, vehTypeID))),
         plugins.MoneyValidator(self.__getRecruitPrice(tmanCostTypeIdx)),
         plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0),
         plugins.IsLongDisconnectedFromCenter()])
        self.nationID = nationID
        self.vehTypeID = vehTypeID
        self.role = role
        self.tmanCostTypeIdx = tmanCostTypeIdx

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='recruit_window/{}'.format(errStr), defaultSysMsgKey='recruit_window/server_error', auxData=ctx)

    def _successHandler(self, code, ctx=None):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        return makeI18nSuccess(sysMsgKey='recruit_window/financial_success', auxData=ctx, price=formatPrice(tmanCost), type=self.__getSysMsgType()) if tmanCost else makeI18nSuccess('recruit_window/success', type=self.__getSysMsgType(), auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to recruit tankman: %s, %s, %s, %s', self.nationID, self.vehTypeID, self.role, self.tmanCostTypeIdx)
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
        super(TankmanTokenRecruit, self).__init__([plugins.Development(), plugins.VehicleCrewLockedValidator(vehicle), plugins.IsLongDisconnectedFromCenter()])
        self.nationID = nationID
        self.vehTypeID = vehTypeID
        self.role = role
        self.tokenName = tokenName
        self.recruitInfo = tokenData
        self.vehicleName = vehicle.shortUserName

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='recruit_window/{}'.format(errStr), defaultSysMsgKey='recruit_window/server_error', auxData=ctx)

    def _successHandler(self, code, ctx=None):
        html = makeHtmlString(path='html_templates:lobby/processors/system_messages', key='recruit', ctx={'fullName': self.recruitInfo.getFullUserName(),
         'rank': Tankman.getRankUserName(self.nationID, self.recruitInfo.getRankID()),
         'role': getSkillsConfig().getSkill(self.role).userString,
         'vehicleName': self.vehicleName,
         'roleLevel': self.recruitInfo.getRoleLevel()})
        return makeSuccess(html, msgType=SM_TYPE.Information, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to recruit notrecruit tankman (by token): %s, %s, %s', self.nationID, self.vehTypeID, self.role)
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
        return makeI18nError(sysMsgKey='{}/{}'.format(prefix, errStr), defaultSysMsgKey='{}/server_error'.format(prefix))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self.__getSysMsgPrefix()), type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to equip tankman: %s, %s, %s, %s', self.tankman, self.vehicle, self.slot, self.isReequip)
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
        self.addPlugins((plugins.Development(),
         plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.MoneyValidator(self.__getRecruitPrice(tmanCostTypeIdx)),
         plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0)))
        return

    def _request(self, callback):
        _logger.debug('Make server request to buy and equip tankman: %s, %s, %s', self.vehicle, self.slot, self.tmanCostTypeIdx)
        BigWorld.player().shop.buyAndEquipTankman(self.vehicle.invID, self.slot, self.tmanCostTypeIdx, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))

    def _errorHandler(self, code, errStr='', ctx=None):
        prefix = self.__getSysMsgPrefix()
        return makeI18nError(sysMsgKey='{}/{}'.format(prefix, errStr), defaultSysMsgKey='{}/server_error'.format(prefix), auxData=ctx)

    def _successHandler(self, code, ctx=None):
        tmanCost = self.__getRecruitPrice(self.tmanCostTypeIdx)
        prefix = self.__getSysMsgPrefix()
        sysMsgType = _getSysMsgType(tmanCost)
        return makeI18nSuccess(sysMsgKey='{}/financial_success'.format(prefix), auxData=ctx, price=formatPrice(tmanCost, useStyle=True), type=sysMsgType) if tmanCost else makeI18nSuccess(sysMsgKey='{}/success'.format(prefix), auxData=ctx, type=sysMsgType)

    def __getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = self.itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return Money(credits=upgradeCost[Currency.CREDITS])
        return Money(gold=upgradeCost[Currency.GOLD]) if tmanCostTypeIdx == 2 else MONEY_UNDEFINED

    def __getSysMsgPrefix(self):
        return 'buy_and_equip_tankman' if not self.isReplace else 'buy_and_reequip_tankman'


class CrewSkinsProcessorBase(Processor):

    def __init__(self, tmanInvID):
        super(CrewSkinsProcessorBase, self).__init__()
        self._tmanInvID = tmanInvID

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='crewSkinsNotification/SkinChanged', type=SM_TYPE.Information)


class CrewSkinUnequip(CrewSkinsProcessorBase):

    def _request(self, callback):
        detInvID = g_currentVehicle.item.getLinkedDetachmentID()
        _logger.debug('Make server request to equip crewSkin: %d', detInvID)
        BigWorld.player().inventory.unequipCrewSkin(detInvID, lambda code: self._response(code, callback))


class CrewSkinEquip(CrewSkinsProcessorBase):

    def __init__(self, tmanInvID, skinID):
        super(CrewSkinEquip, self).__init__(tmanInvID)
        self.__skinID = skinID

    def _request(self, callback):
        detInvID = g_currentVehicle.item.getLinkedDetachmentID()
        _logger.debug('Make server request to equip crewSkin : %d, %d', detInvID, self.__skinID)
        BigWorld.player().inventory.equipCrewSkin(detInvID, self.__skinID, lambda code: self._response(code, callback))


class TankmanUnload(Processor):

    def __init__(self, vehicle, slot=-1):
        super(TankmanUnload, self).__init__()
        self.vehicle = vehicle
        self.slot = slot
        self.__sysMsgPrefix = 'unload_tankman' if self.slot != -1 else 'unload_crew'
        self.addPlugins([plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}), plugins.VehicleCrewLockedValidator(vehicle)])

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/{}'.format(self.__sysMsgPrefix, errStr), defaultSysMsgKey='{}/server_error'.format(self.__sysMsgPrefix))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self.__sysMsgPrefix), type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Trying to unload recruit(s): %s, %s', self.vehicle, self.slot)
        BigWorld.player().inventory.equipTankman(self.vehicle.invID, self.slot, None, lambda code: self._response(code, callback))
        return


class TankmanReturn(Processor):

    def __init__(self, vehicle):
        super(TankmanReturn, self).__init__()
        self.__prefix = 'return_crew'
        self.__vehicle = vehicle
        self.addPlugins([plugins.VehicleValidator(self.__vehicle, False, prop={'isLocked': True}), plugins.VehicleCrewLockedValidator(vehicle)])

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self.__prefix), type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/{}'.format(self.__prefix, errStr), defaultSysMsgKey='{}/server_error'.format(self.__prefix))

    def _request(self, callback):
        _logger.debug('Make server request to return crew. VehicleItem: %s', self.__vehicle)
        BigWorld.player().inventory.returnCrew(self.__vehicle.invID, lambda code: self._response(code, callback))


class TankmanLoad(Processor):

    def __init__(self, vehicle, crew, isNative):
        super(TankmanLoad, self).__init__()
        self.__prefix = 'tankman_load/native' if isNative else 'tankman_load'
        self.__vehicle = vehicle
        self.__crew = crew
        self.addPlugins([plugins.VehicleValidator(self.__vehicle, False, prop={'isLocked': True}), plugins.VehicleCrewLockedValidator(vehicle)])

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self.__prefix), type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/{}'.format(self.__prefix, errStr), defaultSysMsgKey='{}/server_error'.format(self.__prefix))

    def _request(self, callback):
        _logger.debug('Make server request to return crew. VehicleItem: %s', self.__vehicle)
        BigWorld.player().inventory.loadCrew(self.__vehicle.invID, self.__crew, lambda code: self._response(code, callback))


class TankmanRetraining(ItemProcessor):

    def __init__(self, tankman, vehicle, tmanCostTypeIdx):
        isPaid = tmanCostTypeIdx != 0
        self.vehicle = vehicle
        self.tmanCostTypeIdx = tmanCostTypeIdx
        self.tmanCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        ctx = {'vehicle': vehicle.userName}
        if isPaid:
            ctx['price'] = formatPrice(self.tmanCost, reverse=True, useIcon=True, useStyle=True)
        isInInventory = vehicle.isInInventory
        super(TankmanRetraining, self).__init__(tankman, (plugins.MoneyValidator(self._getRecruitPrice(tmanCostTypeIdx)),
         plugins.VehicleValidator(vehicle, False),
         plugins.TankmenLockedValidator([tankman]),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleByMoney', ctx=ctx, isEnabled=isPaid and isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicleByMoney', ctx=ctx, isEnabled=isPaid and not isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleFree', ctx=ctx, isEnabled=not isPaid and isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicleFree', ctx=ctx, isEnabled=not isPaid and not isInInventory)))

    def _getRecruitPrice(self, tmanCostTypeIdx):
        upgradeCost = self.itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
        if tmanCostTypeIdx == 1:
            return Money(credits=upgradeCost[Currency.CREDITS])
        return Money(gold=upgradeCost[Currency.GOLD]) if tmanCostTypeIdx == 2 else MONEY_UNDEFINED

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='retraining_tankman/{}'.format(errStr), defaultSysMsgKey='retraining_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        sysMsgType = _getSysMsgType(self.tmanCost)
        return makeI18nSuccess(sysMsgKey='retraining_tankman/financial_success', auxData=ctx, type=sysMsgType, price=formatPrice(self.tmanCost, ignoreZeros=True)) if self.tmanCost else makeI18nSuccess(sysMsgKey='retraining_tankman/success', auxData=ctx, type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to retrain Crew: %s, %s, %s', self.item, self.vehicle, self.tmanCostTypeIdx)
        BigWorld.player().inventory.respecTankman(self.item.invID, self.vehicle.intCD, self.tmanCostTypeIdx, lambda code: self._response(code, callback))


class TankmanCrewRetraining(Processor):

    def __init__(self, tmen, vehicle, tmanCostTypeIdx):
        isPaid = tmanCostTypeIdx != 0
        self.tankmen = tmen
        self.vehicle = vehicle
        self.tmanCostTypeIdx = tmanCostTypeIdx
        ctx = {'vehicle': vehicle.userName}
        if isPaid:
            ctx['price'] = formatPrice(self._getRecruitPrice(self.tmanCostTypeIdx), reverse=True, useIcon=True, useStyle=True, ignoreZeros=True)
        isInInventory = vehicle.isInInventory
        super(TankmanCrewRetraining, self).__init__((plugins.MoneyValidator(self._getRecruitPrice(tmanCostTypeIdx)),
         plugins.VehicleValidator(vehicle, False),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.GroupOperationsValidator(tmen, tmanCostTypeIdx),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleByMoney/pack', ctx=ctx, isEnabled=len(tmen) > 1 and isPaid and isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleByMoney', ctx=ctx, isEnabled=len(tmen) == 1 and isPaid and isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleFree/pack', ctx=ctx, isEnabled=len(tmen) > 1 and not isPaid and isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/knownVehicleFree', ctx=ctx, isEnabled=len(tmen) == 1 and not isPaid and isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicleByMoney/pack', ctx=ctx, isEnabled=len(tmen) > 1 and isPaid and not isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicleByMoney', ctx=ctx, isEnabled=len(tmen) == 1 and isPaid and not isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicleFree/pack', ctx=ctx, isEnabled=len(tmen) > 1 and not isPaid and not isInInventory),
         plugins.MessageConfirmator('tankmanRetraining/unknownVehicleFree', ctx=ctx, isEnabled=len(tmen) == 1 and not isPaid and not isInInventory)))

    def _errorHandler(self, code, errStr='', ctx=None):
        crewMembersCount = len(self.tankmen)
        messagePrefix = 'retraining_crew'
        if crewMembersCount == 1:
            messagePrefix = 'retraining_tankman'
        return makeI18nError(sysMsgKey='{}/{}'.format(messagePrefix, errStr), defaultSysMsgKey='{}/server_error'.format(messagePrefix))

    def _successHandler(self, code, ctx=None):
        crewMembersCount = len(self.tankmen)
        messagePrefix = 'retraining_crew'
        if crewMembersCount == 1:
            messagePrefix = 'retraining_tankman'
        crewRetrainingCost = self._getRecruitPrice(self.tmanCostTypeIdx)
        sysMsgType = _getSysMsgType(crewRetrainingCost)
        return makeI18nSuccess(sysMsgKey='{}/financial_success'.format(messagePrefix), auxData=ctx, type=sysMsgType, price=formatPrice(crewRetrainingCost, ignoreZeros=True)) if crewRetrainingCost else makeI18nSuccess('{}/success'.format(messagePrefix), type=SM_TYPE.Information, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to retrain Crew: %s, %s, %s', self.tankmen, self.vehicle, self.tmanCostTypeIdx)
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
        super(TankmanFreeToOwnXpConvertor, self).__init__((plugins.Development(),))
        self.__tankman = tankman
        self.__selectedXpForConvert = selectedXpForConvert

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='free_xp_to_tman_skill/error/{}'.format(errStr), defaultSysMsgKey='free_xp_to_tman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='free_xp_to_tman_skill/success', freeXP=backport.getIntegralFormat(self.__selectedXpForConvert), type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Attempt to request server to exchange Free user XP to tankman XP: %s, %s', self.__tankman, self.__selectedXpForConvert)
        BigWorld.player().inventory.freeXPToTankman(self.__tankman.invID, self.__selectedXpForConvert, lambda errStr, code: self._response(code, callback, errStr=errStr))


class TankmanAddSkill(ItemProcessor):

    def __init__(self, tankman, skillName):
        super(TankmanAddSkill, self).__init__(tankman, (plugins.Development(), plugins.TankmanAddSkillValidator(tankman.descriptor, skillName)))
        self.skillName = skillName

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='add_tankman_skill/{}'.format(errStr), defaultSysMsgKey='add_tankman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='add_tankman_skill/success', type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to add tankman skill: %s, %s', self.item, self.skillName)
        BigWorld.player().inventory.addTankmanSkill(self.item.invID, self.skillName, lambda code: self._response(code, callback))


class TankmanChangeRole(ItemProcessor):

    def __init__(self, tankman, role, vehTypeCompDescr):
        self.__roleIdx = SKILL_INDICES[role]
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__changeRoleCost = self.itemsCache.items.shop.changeRoleCost
        vehicle = self.itemsCache.items.getItemByCD(self.__vehTypeCompDescr)
        self.__withRetraining = tankman.vehicleNativeDescr.type.compactDescr != vehicle.intCD
        ctx = {'vehicle': vehicle.userName,
         'price': formatPrice(Money(gold=self.__changeRoleCost), reverse=True, useIcon=True, useStyle=True)}
        super(TankmanChangeRole, self).__init__(tankman, (plugins.VehicleValidator(vehicle, False),
         plugins.TankmenLockedValidator([tankman]),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.MessageConfirmator('tankmanChageRole/unknownVehicle', ctx=ctx, isEnabled=not vehicle.isInInventory),
         plugins.MessageConfirmator('tankmanChageRole/knownVehicle', ctx=ctx, isEnabled=vehicle.isInInventory),
         plugins.MoneyValidator(Money(gold=self.__changeRoleCost))))

    def _errorHandler(self, code, errStr='', ctx=None):
        sysMsgKey = 'change_tankman_role'
        if self.__withRetraining:
            sysMsgKey += '/with_retraining'
        sysMsgKey += '/' + errStr
        return makeI18nError(sysMsgKey=sysMsgKey, defaultSysMsgKey='change_tankman_role/server_error')

    def _successHandler(self, code, ctx=None):
        sysMsgKey = 'change_tankman_role'
        if self.__withRetraining:
            sysMsgKey += '/with_retraining'
        if self.__changeRoleCost:
            msgType = SM_TYPE.FinancialTransactionWithGold
            sysMsgKey += '/financial_success'
        else:
            msgType = SM_TYPE.Information
            sysMsgKey = '/success'
        return makeI18nSuccess(sysMsgKey, money=formatPrice(Money(gold=self.__changeRoleCost)), type=msgType)

    def _request(self, callback):
        _logger.debug('Make server request to change recruit role: %s, %s, %s', self.item, self.__roleIdx, self.__vehTypeCompDescr)
        BigWorld.player().inventory.changeTankmanRole(self.item.invID, self.__roleIdx, self.__vehTypeCompDescr, lambda code, ext: self._response(code, callback, ctx=ext))


class TankmanDropSkills(ItemProcessor):

    def __init__(self, tankman, dropSkillCostIdx):
        super(TankmanDropSkills, self).__init__(tankman, (plugins.Development(), plugins.MessageConfirmator('dropSkill'), plugins.TankmanDropSkillValidator(tankman, True)))
        self.dropSkillCostIdx = dropSkillCostIdx

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='drop_tankman_skill/{}'.format(errStr), defaultSysMsgKey='drop_tankman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        msgType = self.__getTankmanSysMsgType(self.dropSkillCostIdx)
        price = self.itemsCache.items.shop.dropSkillsCost.get(self.dropSkillCostIdx)
        return makeI18nSuccess(sysMsgKey='drop_tankman_skill/success', money=formatPrice(Money(**price)), type=msgType)

    def _request(self, callback):
        _logger.debug('Make server request to drop tankman skills: %s, %s', self.item, self.dropSkillCostIdx)
        BigWorld.player().inventory.dropTankmanSkills(self.item.invID, self.dropSkillCostIdx, lambda code: self._response(code, callback))

    def __getTankmanSysMsgType(self, dropSkillCostIdx):
        if dropSkillCostIdx == 1:
            return SM_TYPE.FinancialTransactionWithCredits
        return SM_TYPE.FinancialTransactionWithGold if dropSkillCostIdx == 2 else SM_TYPE.Information


class TankmanChangePassport(ItemProcessor):

    def __init__(self, tankman, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):
        super(TankmanChangePassport, self).__init__(tankman, (plugins.Development(), plugins.TankmanChangePassportValidator(tankman)))
        self.firstNameID = firstNameID
        self.firstNameGroup = firstNameGroup
        self.lastNameID = lastNameID
        self.lastNameGroup = lastNameGroup
        self.iconID = iconID
        self.iconGroup = iconGroup
        self.isFemale = tankman.descriptor.isFemale
        self.isPremium = tankman.descriptor.isPremium

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='replace_tankman/success', type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='replace_tankman/{}'.format(errStr), defaultSysMsgKey='replace_tankman/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to change tankman passport: %s, %s, %s, %s, %s, %s, %s', self.item.invID, self.isPremium, self.isFemale, self.firstNameGroup, self.firstNameID, self.lastNameGroup, self.lastNameID)
        BigWorld.player().inventory.replacePassport(self.item.invID, self.isPremium, self.isFemale, self.firstNameGroup, self.firstNameID, self.lastNameGroup, self.lastNameID, self.iconGroup, self.iconID, lambda code: self._response(code, callback))

    @classmethod
    def __hasUniqueData(cls, tankman, firstNameID, lastNameID, iconID):
        tDescr = tankman.descriptor
        nationConfig = tankmen.getNationConfig(tankman.nationID)
        for group in nationConfig.normalGroups.itervalues():
            if group.notInShop:
                if tDescr.firstNameID != firstNameID and firstNameID is not None and tDescr.firstNameID in group.firstNamesList or tDescr.lastNameID != lastNameID and lastNameID is not None and tDescr.lastNameID in group.lastNamesList or tDescr.iconID != iconID and iconID is not None and tDescr.iconID in group.iconsList:
                    return True

        return False


class TankmanRestore(ItemProcessor):

    def __init__(self, tankman):
        self.__tankman = tankman
        restorePrice, _ = getTankmenRestoreInfo(tankman)
        super(TankmanRestore, self).__init__(tankman, (plugins.TankmanLockedValidator(tankman), plugins.MoneyValidator(restorePrice), plugins.IsLongDisconnectedFromCenter()))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='restore_tankman/{}'.format(errStr), defaultSysMsgKey='restore_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        restorePrice, _ = getTankmenRestoreInfo(self.__tankman)
        if restorePrice:
            currency = restorePrice.getCurrency()
            return makeI18nSuccess(sysMsgKey='restore_tankman/financial_success', type=_getSysMsgType(restorePrice), money=formatPriceForCurrency(restorePrice, currency))
        return makeI18nSuccess(sysMsgKey='restore_tankman/success', type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to restore tankman: %s', self.item)
        BigWorld.player().recycleBin.restoreTankman(self.item.invID, lambda code, errStr: self._response(code, callback, errStr=errStr))

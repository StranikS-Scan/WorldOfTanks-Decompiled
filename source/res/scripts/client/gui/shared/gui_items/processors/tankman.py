# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/tankman.py
import logging
import BigWorld
from gui import makeHtmlString, GUI_NATIONS_ORDER_INDEX
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import formatPrice, formatPriceValue
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.Tankman import NO_SLOT, getTankmanSkill
from gui.shared.gui_items.processors import Processor, ItemProcessor, GroupedRequestProcessor, makeI18nSuccess, makeSuccess, makeI18nError, plugins
from gui.shared.money import Money, Currency
from helpers import dependency
from items import tankmen, makeIntCompactDescrByID
from items.tankmen import SKILL_INDICES, getSkillsConfig
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from gui import SystemMessages
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.event_dispatcher import showConversionAwardsView
import time
_logger = logging.getLogger(__name__)

def _getSysMsgType(price):
    currency = price.getCurrency(byWeight=False)
    amount = price.get(currency, default=0)
    return CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.Information) if amount > 0 else SM_TYPE.Information


def _getFinancialTransactionSysMsgType(price):
    currency = price.getCurrency(byWeight=False)
    if currency == Currency.CREDITS:
        return SM_TYPE.FinancialTransactionWithCredits
    return SM_TYPE.FinancialTransactionWithGold if currency == Currency.GOLD else SM_TYPE.Information


class TankmanDismiss(ItemProcessor):
    restore = dependency.descriptor(IRestoreController)

    def __init__(self, tankman):
        vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
        super(TankmanDismiss, self).__init__(tankman, [plugins.TankmanLockedValidator(tankman), plugins.VehicleValidator(vehicle, isEnabled=tankman.vehicleInvID > 0)])

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='dismiss_tankman/{}'.format(errStr), defaultSysMsgKey='dismiss_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        additionalMsgs = []
        return makeI18nSuccess('dismiss_tankman/success', type=SM_TYPE.Information, auxData=additionalMsgs)

    def _request(self, callback):
        _logger.debug('Make server request to dismiss tankman: %s', self.item)
        BigWorld.player().inventory.dismissTankman(self.item.invID, lambda code: self._response(code, callback))


def _getRecruitPrice(tmanCostTypeIdx):
    itemsCache = dependency.instance(IItemsCache)
    upgradeCost = itemsCache.items.shop.tankmanCost[tmanCostTypeIdx]
    return Money(**upgradeCost)


class TankmanRecruit(Processor):

    def __init__(self, nationID, vehTypeID, role, tmanCostTypeIdx):
        self.vehicle = self.itemsCache.items.getItemByCD(makeIntCompactDescrByID('vehicle', nationID, vehTypeID))
        super(TankmanRecruit, self).__init__([plugins.VehicleCrewLockedValidator(self.vehicle),
         plugins.MoneyValidator(_getRecruitPrice(tmanCostTypeIdx)),
         plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0),
         plugins.BarracksSlotsValidator(),
         plugins.IsLongDisconnectedFromCenter()])
        self.nationID = nationID
        self.vehTypeID = vehTypeID
        self.role = role
        self.tmanCostTypeIdx = tmanCostTypeIdx

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='recruit_window/{}'.format(errStr), defaultSysMsgKey='recruit_window/server_error', auxData=ctx)

    def _successHandler(self, code, ctx=None):
        tmanCost = _getRecruitPrice(self.tmanCostTypeIdx)
        return makeI18nSuccess(sysMsgKey='recruit_window/financial_success', auxData=ctx, vehName=self.vehicle.userName, price=formatPrice(tmanCost, useStyle=True), type=_getFinancialTransactionSysMsgType(tmanCost)) if tmanCost else makeI18nSuccess('recruit_window/success', type=_getSysMsgType(self.tmanCostTypeIdx), auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to recruit tankman: %s, %s, %s, %s', self.nationID, self.vehTypeID, self.role, self.tmanCostTypeIdx)
        BigWorld.player().shop.buyTankman(self.nationID, self.vehTypeID, self.role, self.tmanCostTypeIdx, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))


class TankmanTokenRecruit(Processor):

    def __init__(self, nationID, vehTypeID, role, tokenName, tokenData):
        vehicle = self.itemsCache.items.getItemByCD(makeIntCompactDescrByID('vehicle', nationID, vehTypeID))
        super(TankmanTokenRecruit, self).__init__([plugins.VehicleCrewLockedValidator(vehicle), plugins.IsLongDisconnectedFromCenter(), plugins.BarracksSlotsValidator(addWarning=True)])
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


class TankmanEquip(GroupedRequestProcessor):

    def __init__(self, tankmanInvID, vehicleInvID, vehicleSlotIdx, groupID=0, groupSize=1):
        self.__tankmanInvID = tankmanInvID
        self.__vehicleInvID = vehicleInvID
        self.__vehicleSlotIdx = vehicleSlotIdx
        tankman = self.itemsCache.items.getTankman(tankmanInvID)
        vehicle = self.itemsCache.items.getVehicle(vehicleInvID)
        isEnableBarrackValidator = False
        self.__sysMsgPrefix = 'equip_tankman'
        anotherTankman = dict(vehicle.crew).get(vehicleSlotIdx)
        if tankman is not None and anotherTankman is not None and anotherTankman.invID != tankman.invID:
            self.__sysMsgPrefix = 'reequip_tankman'
            isEnableBarrackValidator = True
        super(TankmanEquip, self).__init__(BigWorld.player().inventory.equipTankman, vehicleInvID, vehicleSlotIdx, tankmanInvID, groupID=groupID, groupSize=groupSize, plugins=(plugins.TankmanLockedValidator(tankman),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}),
         plugins.BarracksSlotsValidator(isEnabled=isEnableBarrackValidator, addWarning=True)))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/{}'.format(self.__sysMsgPrefix, errStr), defaultSysMsgKey='{}/server_error'.format(self.__sysMsgPrefix), auxData=self._makeErrorData(errStr), type=SM_TYPE.NotEnoughBerthError if errStr == 'not_enough_space' else SM_TYPE.Error)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self.__sysMsgPrefix), vehName=self.itemsCache.items.getVehicle(self.__vehicleInvID).userName, auxData=self._makeSuccessData(ctx))


class TankmanRecruitAndEquip(Processor):

    def __init__(self, vehicle, slot, tmanCostTypeIdx):
        super(TankmanRecruitAndEquip, self).__init__()
        self.vehicle = vehicle
        self.slot = slot
        self.tmanCostTypeIdx = tmanCostTypeIdx
        self.isReplace = dict(vehicle.crew).get(slot) is not None
        self.addPlugins((plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}),
         plugins.VehicleCrewLockedValidator(vehicle),
         plugins.MoneyValidator(_getRecruitPrice(tmanCostTypeIdx)),
         plugins.FreeTankmanValidator(isEnabled=tmanCostTypeIdx == 0),
         plugins.BarracksSlotsValidator(isEnabled=self.isReplace)))
        return

    def _request(self, callback):
        _logger.debug('Make server request to buy and equip tankman: %s, %s, %s', self.vehicle, self.slot, self.tmanCostTypeIdx)
        BigWorld.player().shop.buyAndEquipTankman(self.vehicle.invID, self.slot, self.tmanCostTypeIdx, lambda code, tmanInvID, tmanCompDescr: self._response(code, callback, ctx=tmanInvID))

    def _errorHandler(self, code, errStr='', ctx=None):
        prefix = self.__getSysMsgPrefix()
        return makeI18nError(sysMsgKey='{}/{}'.format(prefix, errStr), defaultSysMsgKey='{}/server_error'.format(prefix), auxData=ctx)

    def _successHandler(self, code, ctx=None):
        tmanCost = _getRecruitPrice(self.tmanCostTypeIdx)
        if tmanCost:
            currency = tmanCost.getCurrency()
            return makeI18nSuccess(sysMsgKey='recruit_window/financial_success_{}'.format(currency), auxData=ctx, vehName=self.vehicle.userName, price=formatPriceValue(tmanCost.get(currency), currency, useStyle=True), type=_getFinancialTransactionSysMsgType(tmanCost))
        return makeI18nSuccess(sysMsgKey='recruit_window/success', auxData=ctx, vehName=self.vehicle.userName, type=_getSysMsgType(tmanCost))

    def __getSysMsgPrefix(self):
        return 'buy_and_equip_tankman' if not self.isReplace else 'buy_and_reequip_tankman'


class CrewSkinsProcessorBase(Processor):

    def __init__(self, tmanInvID):
        super(CrewSkinsProcessorBase, self).__init__()
        self._tmanInvID = tmanInvID

    def _successHandler(self, code, ctx=None):
        additionalMsgs = []
        return makeI18nSuccess(sysMsgKey='crewSkinsNotification/SkinChanged', type=SM_TYPE.Information, auxData=additionalMsgs)


class CrewSkinUnequip(CrewSkinsProcessorBase):

    def _request(self, callback):
        _logger.debug('Make server request to equip crewSkin: %d', self._tmanInvID)
        BigWorld.player().inventory.unequipCrewSkin(self._tmanInvID, lambda code: self._response(code, callback))


class CrewSkinEquip(CrewSkinsProcessorBase):

    def __init__(self, tmanInvID, skinID):
        super(CrewSkinEquip, self).__init__(tmanInvID)
        self.__skinID = skinID

    def _request(self, callback):
        _logger.debug('Make server request to equip crewSkin : %d, %d', self._tmanInvID, self.__skinID)
        BigWorld.player().inventory.equipCrewSkin(self._tmanInvID, self.__skinID, lambda code: self._response(code, callback))


class TankmanUnload(GroupedRequestProcessor):

    def __init__(self, vehicleInvID, vehicleSlotIdx=NO_SLOT, groupID=0, groupSize=1):
        self.__vehicleInvID = vehicleInvID
        self.__vehicleSlotIdx = vehicleSlotIdx
        vehicle = self.itemsCache.items.getVehicle(vehicleInvID)
        super(TankmanUnload, self).__init__(BigWorld.player().inventory.equipTankman, vehicleInvID, vehicleSlotIdx, None, groupID=groupID, groupSize=groupSize, plugins=(plugins.VehicleValidator(vehicle, False, prop={'isLocked': True}), plugins.VehicleCrewLockedValidator(vehicle)))
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/{}'.format(self.__sysMsgPrefix(ctx), errStr), defaultSysMsgKey='{}/server_error'.format(self.__sysMsgPrefix(ctx)), auxData=self._makeErrorData(errStr), type=SM_TYPE.NotEnoughBerthError if errStr == 'not_enough_space' else SM_TYPE.Error)

    def _successHandler(self, code, ctx=None):
        if self.itemsCache.items.freeTankmenBerthsCount() < 0:
            plugins.showWarning(text='', type=SM_TYPE.NotEnoughBerthWarning)
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self.__sysMsgPrefix(ctx)), auxData=self._makeSuccessData(ctx))

    @staticmethod
    def __sysMsgPrefix(ctx):
        return 'unload_crew' if TankmanUnload.__tmanQuantity(ctx) > 1 else 'unload_tankman'

    @staticmethod
    def __tmanQuantity(ctx):
        return len(ctx) / 2


class TankmanReturn(Processor):

    def __init__(self, vehicle):
        self.__prefix = 'return_crew'
        self.__vehicle = vehicle
        super(TankmanReturn, self).__init__((plugins.VehicleValidator(self.__vehicle, False, prop={'isLocked': True}), plugins.VehicleCrewLockedValidator(vehicle)))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self.__prefix), type=SM_TYPE.Information)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/{}'.format(self.__prefix, errStr), defaultSysMsgKey='{}/server_error'.format(self.__prefix))

    def _request(self, callback):
        _logger.debug('Make server request to return crew. VehicleItem: %s', self.__vehicle)
        BigWorld.player().inventory.returnCrew(self.__vehicle.invID, lambda code: self._response(code, callback))


class TankmanRetraining(GroupedRequestProcessor):

    def __init__(self, tankmanInvID, vehicleIntCD, tmanCostTypeIdx, isRoleChange, groupID=0, groupSize=1):
        self.__tankmanInvID = tankmanInvID
        self.__vehicleIntCD = vehicleIntCD
        self.__tmanCostTypeIdx = tmanCostTypeIdx
        self.__tmanCost = _getRecruitPrice(self.__tmanCostTypeIdx)
        self.__isRoleChange = isRoleChange
        tankman = self.itemsCache.items.getTankman(tankmanInvID)
        vehicle = self.itemsCache.items.getItemByCD(vehicleIntCD)
        super(TankmanRetraining, self).__init__(BigWorld.player().inventory.respecTankman, tankmanInvID, vehicleIntCD, tmanCostTypeIdx, plugins=(plugins.VehicleValidator(vehicle, False), plugins.TankmanLockedValidator(tankman), plugins.VehicleCrewLockedValidator(vehicle)), groupID=groupID, groupSize=groupSize)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/{}'.format(self.__sysMessagePrefix(ctx), errStr), auxData=ctx, defaultSysMsgKey='retraining_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        currency = self.__tmanCost.getCurrency(byWeight=False)
        vehicle = self.itemsCache.items.getItemByCD(self.__vehicleIntCD)
        amount = sum(list((item.itemCount for item in iter(ctx) if item.itemID == currency)))
        sysMessagePrefix = self.__sysMessagePrefix(ctx)
        changeRoleMsg = backport.text(R.strings.system_messages.retraining_change_tankman_role.success()) + '\n' if self.__isRoleChange else ''
        if amount:
            successMsg = backport.text(R.strings.system_messages.dyn(sysMessagePrefix).success(), vehName=vehicle.shortUserName)
            spendMsg = backport.text(R.strings.system_messages.dyn(sysMessagePrefix).dyn('financial_success_{}'.format(currency))(), money=formatPriceValue(amount, currency, useStyle=True))
            return makeSuccess(changeRoleMsg + successMsg + '\n' + spendMsg, _getFinancialTransactionSysMsgType(self.__tmanCost), self._makeSuccessData(ctx))
        return makeSuccess(changeRoleMsg + backport.text(R.strings.system_messages.dyn(sysMessagePrefix).financial_success_free(), vehName=vehicle.shortUserName), auxData=self._makeSuccessData(ctx))

    def __sysMessagePrefix(self, ctx):
        amount = len(ctx) / 3
        return 'retraining_crew' if amount > 1 else 'retraining_tankman'


class TankmanFreeToOwnXpConvertor(GroupedRequestProcessor):

    def __init__(self, tankmanInvID, selectedXpForConvert, groupID=0, groupSize=1):
        self.__tankmanInvID = tankmanInvID
        self.__selectedXpForConvert = selectedXpForConvert
        super(TankmanFreeToOwnXpConvertor, self).__init__(BigWorld.player().inventory.freeXPToTankman, tankmanInvID, selectedXpForConvert, groupID=groupID, groupSize=groupSize)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='free_xp_to_tman_skill/error/{}'.format(errStr), auxData=self._makeErrorData(errStr), defaultSysMsgKey='free_xp_to_tman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeSuccess(backport.text(R.strings.system_messages.free_xp_to_tman_skill.success(), money=sum((item.itemCount for item in iter(ctx) if item.itemID == 'freeXP'))))


class TankmanAddSkill(ItemProcessor):

    def __init__(self, tankman, skillName):
        super(TankmanAddSkill, self).__init__(tankman, (plugins.TankmanAddSkillValidator(tankman.descriptor, skillName),))
        self.skill = getTankmanSkill(skillName, tankman)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='add_tankman_skill/{}'.format(errStr), defaultSysMsgKey='add_tankman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='add_tankman_skill/success', skill=self.skill.userName, type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to add tankman skill: %s, %s', self.item, self.skill.name)
        BigWorld.player().inventory.addTankmanSkill(self.item.invID, self.skill.name, lambda code: self._response(code, callback))


class TankmanLearnFreeSkill(ItemProcessor):

    def __init__(self, tankman, skillName):
        super(TankmanLearnFreeSkill, self).__init__(tankman, (plugins.TankmanLearnFreeSkillValidator(tankman.descriptor, skillName),))
        self.skillName = skillName

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='learn_tankman_free_skill/{}'.format(errStr), defaultSysMsgKey='learn_tankman_free_skill/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='learn_tankman_free_skill/success', type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to add tankman skill: %s, %s', self.item, self.skillName)
        BigWorld.player().inventory.learnTankmanFreeSkill(self.item.invID, self.skillName, lambda code: self._response(code, callback))


class TankmanChangeRole(GroupedRequestProcessor):

    def __init__(self, tankmanInvID, role, vehTypeCompDescr, vehSlotIdx=-1, groupID=0, groupSize=1):
        self.__roleIdx = SKILL_INDICES[role]
        self.__vehTypeCompDescr = vehTypeCompDescr
        self.__changeRoleCost = self.itemsCache.items.shop.changeRoleCost
        self.__vehSlotIdx = vehSlotIdx
        tankman = self.itemsCache.items.getTankman(tankmanInvID)
        self.__vehicle = self.itemsCache.items.getItemByCD(self.__vehTypeCompDescr)
        self.__retrainVehicle = True if tankman.vehicleNativeDescr.type.compactDescr != self.__vehicle.intCD else False
        super(TankmanChangeRole, self).__init__(BigWorld.player().inventory.changeTankmanRole, tankmanInvID, self.__roleIdx, self.__vehTypeCompDescr, groupID=groupID, groupSize=groupSize, plugins=(plugins.TankmanLockedValidator(tankman),
         plugins.VehicleCrewLockedValidator(self.__vehicle),
         plugins.VehicleValidator(self.__vehicle, False),
         plugins.VehicleRoleValidator(self.__vehicle, role, tankman),
         plugins.MoneyValidator(Money(gold=self.__changeRoleCost))))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='change_tankman_role/{}'.format(errStr), defaultSysMsgKey='change_tankman_role/server_error', auxData=self._makeErrorData(errStr))


class TankmanDropSkills(ItemProcessor):

    def __init__(self, tankman, dropSkillCostIdx, useRecertificationForm):
        super(TankmanDropSkills, self).__init__(tankman, (plugins.TankmanDropSkillValidator(tankman, True),))
        self.dropSkillCostIdx = dropSkillCostIdx
        self.useRecertificationForm = useRecertificationForm

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='drop_tankman_skill/{}'.format(errStr), defaultSysMsgKey='drop_tankman_skill/server_error')

    def _successHandler(self, code, ctx=None):
        msgType = self.__getTankmanSysMsgType(self.dropSkillCostIdx)
        price = self.itemsCache.items.shop.dropSkillsCost[self.dropSkillCostIdx]
        cost = Money(**price)
        if cost:
            currency = cost.getCurrency()
            return makeI18nSuccess(sysMsgKey='drop_tankman_skill/finance_success_{}'.format(currency), auxData=ctx, money=formatPriceValue(cost.get(currency), currency, useStyle=True), type=msgType)
        return makeI18nSuccess(sysMsgKey='drop_tankman_skill/success', auxData=ctx, type=msgType)

    def _request(self, callback):
        _logger.debug('Make server request to drop tankman skills: %s, %s', self.item, self.dropSkillCostIdx)
        BigWorld.player().inventory.dropTankmanSkills(self.item.invID, self.dropSkillCostIdx, self.useRecertificationForm, lambda code: self._response(code, callback))

    def __getTankmanSysMsgType(self, dropSkillCostIdx):
        if dropSkillCostIdx == 1:
            return SM_TYPE.FinancialTransactionWithCredits
        return SM_TYPE.FinancialTransactionWithGold if dropSkillCostIdx == 2 else SM_TYPE.Information


class TankmanChangePassport(ItemProcessor):

    def __init__(self, tankmanInvID, firstNameID, firstNameGroup, lastNameID, lastNameGroup, iconID, iconGroup):
        tankman = self.itemsCache.items.getTankman(tankmanInvID)
        super(TankmanChangePassport, self).__init__(tankman, (plugins.TankmanChangePassportValidator(tankman),))
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


class TankmanRestore(GroupedRequestProcessor):

    def __init__(self, tankman, berthsNeeded, groupID=0, groupSize=1):
        self.__tankmanInvID = tankman.invID
        self.__restorePrice, _ = getTankmenRestoreInfo(tankman)
        super(TankmanRestore, self).__init__(BigWorld.player().recycleBin.restoreTankman, tankman.invID, groupID=groupID, groupSize=groupSize, plugins=(plugins.TankmanLockedValidator(tankman),
         plugins.MoneyValidator(self.__restorePrice),
         plugins.IsLongDisconnectedFromCenter(),
         plugins.BarracksSlotsValidator(berthsNeeded=berthsNeeded, addWarning=True)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='restore_tankman/{}'.format(errStr), defaultSysMsgKey='restore_tankman/server_error', auxData=self._makeErrorData())

    def _successHandler(self, code, ctx=None):
        if self.__restorePrice:
            currency = self.__restorePrice.getCurrency()
            return makeI18nSuccess(sysMsgKey='restore_tankman/financial_success', type=_getFinancialTransactionSysMsgType(self.__restorePrice), money=formatPrice(Money(self.__restorePrice.get(currency)), justValue=True), auxData=self._makeSuccessData())
        return makeI18nSuccess(sysMsgKey='restore_tankman/success', type=SM_TYPE.Information, auxData=self._makeSuccessData())


class TankmenJunkConverter(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='conversion/error', defaultSysMsgKey='restore_tankman/server_error')

    def _successHandler(self, code, ctx=None):
        if not ctx:
            return makeI18nSuccess(sysMsgKey='conversion/success', type=SM_TYPE.Information)
        else:
            showConversionAwardsView(conversionResults=ctx)
            formatedDate = str(time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(time.time())))
            message = backport.text(R.strings.system_messages.conversion.header(), at=formatedDate)
            crewBooks = []
            for intCD, count in ctx.iteritems():
                crewBook = self.itemsCache.items.getItemByCD(intCD)
                if crewBook is None:
                    continue
                crewBooks.append(dict(name=crewBook.getName().strip(), count=count, nation=GUI_NATIONS_ORDER_INDEX[crewBook.getNation()], type=crewBook.getBookTypeOrder()))

            crewBooks.sort(key=lambda item: (item['nation'], -item['type']))
            message += ',\n'.join(('{} ({})'.format(crewBook['name'], crewBook['count']) for crewBook in crewBooks)) + '.'
            SystemMessages.pushMessage(text=message, type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.LOW, messageData={'header': backport.text(R.strings.system_messages.conversion.title())})
            return

    def _request(self, callback):
        _logger.debug('Make server request to convert junk tankmen ')
        BigWorld.player().inventory.convertJunkTankmen(lambda code, ctx: self._response(code, callback, ctx=ctx))

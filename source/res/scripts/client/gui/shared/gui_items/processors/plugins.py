# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/plugins.py
from collections import namedtuple
from adisp import process, async
from debug_utils import LOG_WARNING
from account_helpers import isLongDisconnectedFromCenter
from account_helpers.AccountSettings import AccountSettings
from items import tankmen as tmen_core, vehicles as vehs_core
from gui import DialogsInterface
from gui.game_control import restore_contoller
from gui.shared.formatters.tankmen import formatDeletedTankmanStr
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_PURCHASE_CODE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.money import Currency
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, I18nInfoDialogMeta, DIALOG_BUTTON_ID, IconPriceDialogMeta, IconDialogMeta, DemountDeviceDialogMeta, DestroyDeviceDialogMeta, TankmanOperationDialogMeta, HtmlMessageDialogMeta, HtmlMessageLocalDialogMeta, CheckBoxDialogMeta
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_SHELLS_MONEY_ERRORS = {Currency.CREDITS: 'SHELLS_NO_CREDITS',
 Currency.GOLD: 'SHELLS_NO_GOLD',
 Currency.CRYSTAL: 'SHELLS_NO_CRYSTAL'}
_EQS_MONEY_ERRORS = {Currency.CREDITS: 'EQS_NO_CREDITS',
 Currency.GOLD: 'EQS_NO_GOLD',
 Currency.CRYSTAL: 'EQS_NO_CRYSTAL'}
PluginResult = namedtuple('PluginResult', 'success errorMsg ctx')

def makeSuccess(**kwargs):
    return PluginResult(True, '', kwargs)


def makeError(msg='', **kwargs):
    return PluginResult(False, msg, kwargs)


class ProcessorPlugin(object):

    class TYPE:
        """ Plugins type. """
        VALIDATOR = 0
        CONFIRMATOR = 1

    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, pluginType, isAsync=False, isEnabled=True):
        """
        Ctor.
        
        @param type: <ProcessorPlugin.TYPE.*> plugin type
        @param isAsync: <bool> asynchronous or not
        @param isEnabled: <bool> plugin enabled or not
        """
        self.type = pluginType
        self.isAsync = isAsync
        self.isEnabled = isEnabled


class SyncValidator(ProcessorPlugin):

    def __init__(self, isEnabled=True):
        super(SyncValidator, self).__init__(self.TYPE.VALIDATOR, isEnabled=isEnabled)

    def validate(self):
        return self._validate()

    def _validate(self):
        return makeSuccess()


class AsyncValidator(ProcessorPlugin):

    def __init__(self, isEnabled=True):
        super(AsyncValidator, self).__init__(self.TYPE.VALIDATOR, True, isEnabled=isEnabled)

    @async
    @process
    def validate(self, callback):
        result = yield self._validate()
        callback(result)

    @async
    def _validate(self, callback):
        callback(makeSuccess())


class AsyncConfirmator(ProcessorPlugin):

    def __init__(self, isEnabled=True):
        super(AsyncConfirmator, self).__init__(self.TYPE.CONFIRMATOR, True, isEnabled=isEnabled)

    @async
    @process
    def confirm(self, callback):
        result = yield self._confirm()
        callback(result)

    @async
    def _confirm(self, callback):
        callback(makeSuccess())


class VehicleValidator(SyncValidator):

    def __init__(self, vehicle, setAll=True, prop=None, isEnabled=True):
        super(VehicleValidator, self).__init__(isEnabled)
        prop = prop or {}
        self.vehicle = vehicle
        self.isBroken = prop.get('isBroken', False) or setAll
        self.isLocked = prop.get('isLocked', False) or setAll
        self.isInInventory = prop.get('isInInventory', False) or setAll

    def _validate(self):
        if self.vehicle is None:
            return makeError('invalid_vehicle')
        elif self.isBroken and self.vehicle.isBroken:
            return makeError('vehicle_need_repair')
        elif self.isLocked and self.vehicle.isLocked:
            return makeError('vehicle_locked')
        else:
            return makeError('vehicle_not_found_in_inventory') if self.isInInventory and not self.vehicle.isInInventory else makeSuccess()


class VehicleRoleValidator(SyncValidator):

    def __init__(self, vehicle, role, isEnabled=True):
        super(VehicleRoleValidator, self).__init__(isEnabled)
        self.vehicle = vehicle
        self.role = role

    def _validate(self):
        if self.vehicle is None:
            return makeError('invalid_vehicle')
        else:
            if self.vehicle is not None:
                mainRoles = set(map(lambda r: r[0], self.vehicle.descriptor.type.crewRoles))
                if self.role not in mainRoles:
                    return makeError('invalid_role')
            return makeSuccess()


class VehicleSellValidator(SyncValidator):

    def __init__(self, vehicle, isEnabled=True):
        super(VehicleSellValidator, self).__init__(isEnabled)
        self.vehicle = vehicle

    def _validate(self):
        return makeError('vehicle_cannot_be_sold') if self.vehicle.canNotBeSold else makeSuccess()


class VehicleTradeInValidator(SyncValidator):

    def __init__(self, vehicleToBuy, vehicleToTradeOff, isEnabled=True):
        super(VehicleTradeInValidator, self).__init__(isEnabled)
        self.vehicleToBuy = vehicleToBuy
        self.vehicleToTradeOff = vehicleToTradeOff

    def _validate(self):
        if not self.vehicleToBuy.canTradeIn:
            return makeError('vehicle_cannot_trade_in')
        return makeError('vehicle_cannot_trade_off') if not self.vehicleToTradeOff.canTradeOff else makeSuccess()


class VehicleLockValidator(SyncValidator):

    def __init__(self, vehicle, setAll=True, isEnabled=True):
        super(VehicleLockValidator, self).__init__(isEnabled)
        self.vehicle = vehicle

    def _validate(self):
        if self.vehicle is None:
            return makeError('invalid_vehicle')
        else:
            return makeError('vehicle_locked') if self.vehicle.isLocked else makeSuccess()


class ModuleValidator(SyncValidator):

    def __init__(self, module):
        super(ModuleValidator, self).__init__()
        self.module = module

    def _validate(self):
        return makeError('invalid_module') if not self.module else makeSuccess()


class ModuleTypeValidator(SyncValidator):

    def __init__(self, module, allowableTypes):
        super(ModuleTypeValidator, self).__init__()
        self.module = module
        self.allowableTypes = allowableTypes

    def _validate(self):
        return makeError('invalid_module_type') if self.module.itemTypeID not in self.allowableTypes else makeSuccess()


class ModuleConfigValidator(SyncValidator):

    def __init__(self, module):
        super(ModuleConfigValidator, self).__init__()
        self.module = module

    def _validate(self):
        return makeError() if not self.module.fullyConfigured else makeSuccess()


class EliteVehiclesValidator(SyncValidator):

    def __init__(self, vehiclesCD):
        super(EliteVehiclesValidator, self).__init__()
        self.vehiclesCD = vehiclesCD

    def _validate(self):
        for vehCD in self.vehiclesCD:
            item = self.itemsCache.items.getItemByCD(int(vehCD))
            if item is None:
                return makeError('invalid_vehicle')
            if item.itemTypeID is not GUI_ITEM_TYPE.VEHICLE:
                return makeError('invalid_module_type')
            if not item.isElite:
                return makeError('vehicle_not_elite')

        return makeSuccess()


class CompatibilityValidator(SyncValidator):

    def __init__(self, vehicle, module, slotIdx=0):
        super(CompatibilityValidator, self).__init__()
        self.vehicle = vehicle
        self.module = module
        self.slotIdx = slotIdx

    def _checkCompatibility(self):
        """
        @rtype : tuple
        """
        return makeSuccess()

    def _validate(self):
        success, errMsg = self._checkCompatibility()
        return makeError('error_%s' % errMsg.replace(' ', '_')) if not success else makeSuccess()


class CompatibilityInstallValidator(CompatibilityValidator):

    def _checkCompatibility(self):
        return self.module.mayInstall(self.vehicle, self.slotIdx)


class TurretCompatibilityInstallValidator(SyncValidator):

    def __init__(self, vehicle, module, gunCD=0):
        super(TurretCompatibilityInstallValidator, self).__init__()
        self.vehicle = vehicle
        self.module = module
        self.gunCD = gunCD

    def _checkCompatibility(self):
        """
        @rtype : tuple
        """
        return self.module.mayInstall(self.vehicle, 0, self.gunCD)

    def _validate(self):
        success, errMsg = self._checkCompatibility()
        return makeError('error_%s' % errMsg.replace(' ', '_')) if not success else makeSuccess()


class CompatibilityRemoveValidator(CompatibilityValidator):

    def __init__(self, vehicle, module):
        super(CompatibilityRemoveValidator, self).__init__(vehicle, module)

    def _checkCompatibility(self):
        return self.module.mayRemove(self.vehicle)


class MoneyValidator(SyncValidator):
    """
    Validates money. Possible errors: not_enough_credits, not_enough_gold, not_enough_crystal (see Currency enum)
    """

    def __init__(self, price):
        super(MoneyValidator, self).__init__()
        self.price = price

    def _validate(self):
        stats = self.itemsCache.items.stats
        delta = self.price - stats.money
        delta = delta.toNonNegative()
        if delta:
            currency = delta.getCurrency(byWeight=False)
            if currency == Currency.GOLD and not stats.mayConsumeWalletResources:
                error = GUI_ITEM_PURCHASE_CODE.WALLET_NOT_AVAILABLE
            else:
                error = GUI_ITEM_PURCHASE_CODE.getMoneyError(currency)
            return makeError(error)
        return makeSuccess()


class WalletValidator(SyncValidator):

    def __init__(self, isEnabled=True):
        super(WalletValidator, self).__init__(isEnabled)

    def _validate(self):
        stats = self.itemsCache.items.stats
        return makeError(GUI_ITEM_PURCHASE_CODE.WALLET_NOT_AVAILABLE) if not stats.mayConsumeWalletResources else makeSuccess()


class VehicleSellsLeftValidator(SyncValidator):

    def __init__(self, vehicle, isEnabled=True):
        super(VehicleSellsLeftValidator, self).__init__(isEnabled)
        self.vehicle = vehicle

    def _validate(self):
        return makeError('vehicle_sell_limit') if self.itemsCache.items.stats.vehicleSellsLeft <= 0 else makeSuccess()


class VehicleLayoutValidator(SyncValidator):

    def __init__(self, shellsPrice, eqsPrice):
        super(VehicleLayoutValidator, self).__init__()
        self.shellsPrice = shellsPrice
        self.eqsPrice = eqsPrice

    def _validate(self):
        money = self.itemsCache.items.stats.money
        error = self.__checkMoney(money, self.shellsPrice, _SHELLS_MONEY_ERRORS)
        if error is not None:
            return error
        else:
            money = money - self.shellsPrice
            error = self.__checkMoney(money, self.eqsPrice, _EQS_MONEY_ERRORS)
            return error if error is not None else makeSuccess()

    def __checkMoney(self, money, price, errors):
        shortage = money.getShortage(price)
        if shortage:
            currency, value = shortage[0]
            if currency in errors:
                return makeError(errors[currency])
            else:
                LOG_WARNING('Unexpected case: unknown currency!')
                return makeError()
        return None


class BarracksSlotsValidator(SyncValidator):

    def __init__(self, berthsNeeded=1, isEnabled=True):
        super(BarracksSlotsValidator, self).__init__(isEnabled)
        self.berthsNeeded = berthsNeeded

    def _validate(self):
        barracksTmen = self.itemsCache.items.getTankmen(~REQ_CRITERIA.TANKMAN.IN_TANK | REQ_CRITERIA.TANKMAN.ACTIVE)
        tmenBerthsCount = self.itemsCache.items.stats.tankmenBerthsCount
        return makeError('not_enough_space') if self.berthsNeeded > 0 and self.berthsNeeded > tmenBerthsCount - len(barracksTmen) else makeSuccess()


class FreeTankmanValidator(SyncValidator):

    def _validate(self):
        return makeError('free_tankmen_limit') if not self.itemsCache.items.stats.freeTankmenLeft else makeSuccess()


class TankmanDropSkillValidator(SyncValidator):
    """
    Validates that there is at least one skill for dropping.
    """

    def __init__(self, tankman, isEnabled=True):
        super(TankmanDropSkillValidator, self).__init__(isEnabled)
        self.__tankman = tankman

    def _validate(self):
        return makeSuccess() if self.__tankman is not None and len(self.__tankman.skills) else makeError('server_error')


class GroupOperationsValidator(SyncValidator):
    AVAILABLE_OPERATIONS = range(3)

    def __init__(self, group, operation=0, isEnabled=True):
        super(GroupOperationsValidator, self).__init__(isEnabled)
        self.group = group
        self.operation = operation

    def _validate(self):
        if len(self.group) == 0:
            return makeError('empty_list')
        return makeError('invalid_operation') if self.operation not in self.AVAILABLE_OPERATIONS else makeSuccess()


class DialogAbstractConfirmator(AsyncConfirmator):

    def __init__(self, activeHandler=None, isEnabled=True):
        super(DialogAbstractConfirmator, self).__init__(isEnabled=isEnabled)
        self.activeHandler = activeHandler or (lambda : True)

    def __del__(self):
        self.activeHandler = None
        return

    def _makeMeta(self):
        raise NotImplementedError

    @async
    def _showDialog(self, callback):
        callback(None)
        return

    def _activeHandler(self):
        return self.activeHandler()

    @async
    @process
    def _confirm(self, callback):
        yield lambda callback: callback(None)
        if self._activeHandler():
            isOk = yield DialogsInterface.showDialog(meta=self._makeMeta())
            if not isOk:
                callback(makeError())
                return
        callback(makeSuccess())


class I18nMessageAbstractConfirmator(DialogAbstractConfirmator):

    def __init__(self, localeKey, ctx=None, activeHandler=None, isEnabled=True):
        super(I18nMessageAbstractConfirmator, self).__init__(activeHandler, isEnabled)
        self.localeKey = localeKey
        self.ctx = ctx


class MessageConfirmator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return I18nConfirmDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class ModuleBuyerConfirmator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return I18nConfirmDialogMeta(self.localeKey, meta=HtmlMessageLocalDialogMeta('html_templates:lobby/dialogs', self.localeKey, ctx=self.ctx))


class HtmlMessageConfirmator(I18nMessageAbstractConfirmator):

    def __init__(self, localeKey, metaPath, metaKey, ctx=None, activeHandler=None, isEnabled=True, sourceKey='text'):
        super(HtmlMessageConfirmator, self).__init__(localeKey, ctx, activeHandler, isEnabled)
        self.metaPath = metaPath
        self.metaKey = metaKey
        self.sourceKey = sourceKey
        self.ctx = ctx

    def _makeMeta(self):
        return I18nConfirmDialogMeta(self.localeKey, self.ctx, self.ctx, meta=HtmlMessageDialogMeta(self.metaPath, self.metaKey, self.ctx, sourceKey=self.sourceKey), focusedID=DIALOG_BUTTON_ID.SUBMIT)


class TankmanOperationConfirmator(I18nMessageAbstractConfirmator):

    def __init__(self, localeKey, tankman):
        super(TankmanOperationConfirmator, self).__init__(localeKey, tankman, None, True)
        self.__previousPrice, _ = restore_contoller.getTankmenRestoreInfo(tankman)
        return

    @async
    @process
    def _confirm(self, callback):
        if self._activeHandler():
            isOk = yield DialogsInterface.showDialog(meta=self._makeMeta())
            if isOk and self.__priceChanged():
                isOk = yield DialogsInterface.showDialog(meta=self._makeMeta(True))
            if not isOk:
                callback(makeError())
                return
        callback(makeSuccess())

    def _makeMeta(self, priceChanged=False):
        return TankmanOperationDialogMeta(self.localeKey, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT, showPeriodEndWarning=priceChanged)

    def __priceChanged(self):
        price, _ = restore_contoller.getTankmenRestoreInfo(self.ctx)
        return price != self.__previousPrice


class BufferOverflowConfirmator(I18nMessageAbstractConfirmator):

    def __init__(self, ctx, isEnabled=True):
        if ctx.get('multiple'):
            localeKey = 'dismissedBufferOverFlawMultiple'
        else:
            localeKey = 'dismissedBufferOverFlaw'
        super(BufferOverflowConfirmator, self).__init__(localeKey, ctx, isEnabled=isEnabled)

    def _makeMeta(self):
        msgContext = {'dismissedName': self.ctx['dismissed'].fullUserName,
         'deletedStr': formatDeletedTankmanStr(self.ctx['deleted'])}
        if self.ctx.get('multiple'):
            msgContext['extraCount'] = self.ctx['extraCount']
        return I18nConfirmDialogMeta(self.localeKey, messageCtx=msgContext, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class IconPriceMessageConfirmator(I18nMessageAbstractConfirmator):
    """
    Invoke dialog window contains icon, text and component with price
    """

    def __init__(self, localeKey, ctx=None, activeHandler=None, isEnabled=True):
        super(IconPriceMessageConfirmator, self).__init__(localeKey, ctx, activeHandler, isEnabled)

    def _makeMeta(self):
        return IconPriceDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class DemountDeviceConfirmator(IconPriceMessageConfirmator):
    """
    Invoke dialog window contains icon, text and component with price
    """

    def __init__(self, localeKey, ctx=None, activeHandler=None, isEnabled=True):
        super(DemountDeviceConfirmator, self).__init__(localeKey, ctx, activeHandler, isEnabled)

    def _makeMeta(self):
        return DemountDeviceDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class IconMessageConfirmator(I18nMessageAbstractConfirmator):
    """
    Invoke dialog window contains icon, text and component with price
    """

    def __init__(self, localeKey, ctx=None, activeHandler=None, isEnabled=True):
        super(IconMessageConfirmator, self).__init__(localeKey, ctx, activeHandler, isEnabled)

    def _makeMeta(self):
        return IconDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class DestroyDeviceConfirmator(IconMessageConfirmator):
    __DESTROY_DEVICE_PATH = '../maps/icons/modules/destroyDevice.png'

    def __init__(self, localeKey, itemName=None, activeHandler=None, isEnabled=True):
        super(DestroyDeviceConfirmator, self).__init__(localeKey, {'name': itemName,
         'icon': self.__DESTROY_DEVICE_PATH}, activeHandler, isEnabled)

    def _makeMeta(self):
        return DestroyDeviceDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class MessageInformator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return I18nInfoDialogMeta(self.localeKey, self.ctx, self.ctx)


class VehicleSlotsConfirmator(MessageInformator):

    def __init__(self, isEnabled=True):
        super(VehicleSlotsConfirmator, self).__init__('haveNoEmptySlots', isEnabled=isEnabled)

    def _activeHandler(self):
        return self.itemsCache.items.stats.vehicleSlots <= len(self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY))


class VehicleFreeLimitConfirmator(MessageInformator):

    def __init__(self, vehicle, crewType):
        super(VehicleFreeLimitConfirmator, self).__init__('freeVehicleLeftLimit')
        self.vehicle = vehicle
        self.crewType = crewType

    def _activeHandler(self):
        return not self.vehicle.buyPrice and self.crewType < 1 and not self.itemsCache.items.stats.freeVehiclesLeft


class PotapovQuestValidator(SyncValidator):

    def __init__(self, quests):
        super(PotapovQuestValidator, self).__init__()
        self.quests = quests

    def _validate(self):
        for quest in self.quests:
            if quest is None:
                return makeError('WRONG_ARGS_TYPE')
            if not quest.isUnlocked():
                return makeError('NOT_UNLOCKED_QUEST')

        return makeSuccess()


class _EventsCacheValidator(SyncValidator):
    eventsCache = dependency.descriptor(IEventsCache)


class PotapovQuestsLockedByVehicle(_EventsCacheValidator):

    def __init__(self, quests, messageKeyPrefix=''):
        super(PotapovQuestsLockedByVehicle, self).__init__()
        self._messageKeyPrefix = messageKeyPrefix
        self._lockedChains = self.eventsCache.getLockedQuestTypes()
        self.quests = quests

    def _validate(self):
        for quest in self.quests:
            if quest.getMajorTag() in self._lockedChains:
                return makeError(self._messageKeyPrefix + 'LOCKED_BY_VEHICLE_QUEST')

        return makeSuccess()


class PotapovQuestSlotsValidator(SyncValidator):

    def __init__(self, questsProgress, isEnabled=True, removedCount=0):
        super(PotapovQuestSlotsValidator, self).__init__(isEnabled)
        self.__removedCount = removedCount
        self._questsProgress = questsProgress

    def _validate(self):
        return makeError('NOT_ENOUGH_SLOTS') if not self._questsProgress.getPotapovQuestsFreeSlots(self.__removedCount) else makeSuccess()


class PotapovQuestChainsValidator(_EventsCacheValidator):

    def __init__(self, quest):
        super(PotapovQuestChainsValidator, self).__init__()
        self.quest = quest

    def _validate(self):
        for quest in self.eventsCache.potapov.getSelectedQuests().itervalues():
            if quest.getChainID() == self.quest.getChainID():
                return makeError('TOO_MANY_QUESTS_IN_CHAIN')

        return makeSuccess()


class PotapovQuestSeasonsValidator(_EventsCacheValidator):

    def __init__(self, quest):
        super(PotapovQuestSeasonsValidator, self).__init__()
        self.quest = quest

    def _validate(self):
        qVehClasses = self.quest.getVehicleClasses()
        if len(qVehClasses) == 1:
            for quest in self.eventsCache.potapov.getSelectedQuests().itervalues():
                if len(quest.getVehicleClasses() & qVehClasses) and quest.getSeasonID() == self.quest.getSeasonID():
                    return makeError('SEASON_LIMIT_THE_SAME_CLASS')

        return makeSuccess()


class PotapovQuestRewardValidator(SyncValidator):

    def __init__(self, quest):
        super(PotapovQuestRewardValidator, self).__init__()
        self.quest = quest

    def _validate(self):
        return makeError('NO_REWARD') if not self.quest.needToGetReward() else makeSuccess()


class CheckBoxConfirmator(DialogAbstractConfirmator):
    __ACC_SETT_MAIN_KEY = 'checkBoxConfirmator'

    def __init__(self, settingFieldName, activeHandler=None, isEnabled=True):
        super(CheckBoxConfirmator, self).__init__(activeHandler, isEnabled)
        self.settingFieldName = settingFieldName

    def _activeHandler(self):
        return self._getSetting().get(self.settingFieldName)

    @async
    @process
    def _confirm(self, callback):
        yield lambda callback: callback(None)
        if self._activeHandler():
            success, selected = yield DialogsInterface.showDialog(meta=self._makeMeta())
            if selected:
                self._setSetting(not selected)
            if not success:
                callback(makeError())
        callback(makeSuccess())

    def _getSetting(self):
        return AccountSettings.getSettings(CheckBoxConfirmator.__ACC_SETT_MAIN_KEY)

    def _setSetting(self, value):
        settings = self._getSetting()
        settings[self.settingFieldName] = value
        AccountSettings.setSettings(CheckBoxConfirmator.__ACC_SETT_MAIN_KEY, settings)


class PotapovQuestSelectConfirmator(CheckBoxConfirmator):

    def __init__(self, quest, oldQuest, activeHandler=None, isEnabled=True):
        super(PotapovQuestSelectConfirmator, self).__init__(settingFieldName='questsConfirmDialogShow', activeHandler=activeHandler, isEnabled=isEnabled)
        self.quest = quest
        self.oldQuest = oldQuest

    def _makeMeta(self):
        return CheckBoxDialogMeta('questsConfirmDialog', messageCtx={'newQuest': self.quest.getUserName(),
         'oldQuest': self.oldQuest.getUserName()})


class BoosterActivateValidator(SyncValidator):

    def __init__(self, booster):
        super(BoosterActivateValidator, self).__init__()
        self.booster = booster

    def _validate(self):
        if not self.booster.isInAccount:
            return makeError('NO_BOOSTERS')
        return makeError('ALREADY_USED') if self.booster.inCooldown else makeSuccess()


class TankmanAddSkillValidator(SyncValidator):

    def __init__(self, tankmanDscr, skillName):
        super(TankmanAddSkillValidator, self).__init__()
        self.tankmanDscr = tankmanDscr
        self.skillName = skillName

    def _validate(self):
        if self.skillName in self.tankmanDscr.skills:
            return makeError()
        from items.tankmen import ACTIVE_SKILLS
        if self.skillName not in ACTIVE_SKILLS:
            return makeError()
        from items.tankmen import MAX_SKILL_LEVEL
        if self.tankmanDscr.roleLevel != MAX_SKILL_LEVEL:
            return makeError()
        return makeError() if self.tankmanDscr.skills and self.tankmanDscr.lastSkillLevel != MAX_SKILL_LEVEL else makeSuccess()


class IsLongDisconnectedFromCenter(SyncValidator):

    def _validate(self):
        return makeError('disconnected_from_center') if isLongDisconnectedFromCenter() else makeSuccess()


class VehicleCrewLockedValidator(SyncValidator):

    def __init__(self, vehicle):
        super(VehicleCrewLockedValidator, self).__init__()
        self.__vehicle = vehicle

    def _validate(self):
        return makeError('FORBIDDEN') if self.__vehicle.isCrewLocked else makeSuccess()


class TankmanLockedValidator(SyncValidator):

    def __init__(self, tankman):
        super(TankmanLockedValidator, self).__init__()
        self.__tankman = tankman

    def _validate(self):
        return makeError('FORBIDDEN') if tmen_core.ownVehicleHasTags(self.__tankman.strCD, (VEHICLE_TAGS.CREW_LOCKED,)) else makeSuccess()


class BattleBoosterConfirmator(I18nMessageAbstractConfirmator):

    def __init__(self, localeKey, notSuitableLocaleKey, vehicle, battleBooster):
        self.__notSuitableLocaleKey = notSuitableLocaleKey
        self.__vehicle = vehicle
        self.__battleBooster = battleBooster
        super(BattleBoosterConfirmator, self).__init__(localeKey)

    def _activeHandler(self):
        return not self.__battleBooster.isAffectsOnVehicle(self.__vehicle)

    def _makeMeta(self):
        data = self.itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, REQ_CRITERIA.VEHICLE.SUITABLE([self.__vehicle], [GUI_ITEM_TYPE.OPTIONALDEVICE])).values()
        optDevicesList = [ device for device in data if self.__battleBooster.isOptionalDeviceCompatible(device) ]
        ctx = {'devices': ', '.join([ device.userName for device in optDevicesList ])}
        localeKey = self.localeKey if optDevicesList else self.__notSuitableLocaleKey
        return I18nConfirmDialogMeta(localeKey, meta=HtmlMessageLocalDialogMeta('html_templates:lobby/dialogs', localeKey, ctx=ctx))

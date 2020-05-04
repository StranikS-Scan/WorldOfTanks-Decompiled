# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/plugins.py
from functools import partial
import logging
from collections import namedtuple
import async as future_async
from adisp import process, async
from account_helpers import isLongDisconnectedFromCenter
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view import dialogs
from gui.shared.gui_items.artefacts import OptionalDevice
from items import tankmen
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.dialogs.missions_dialogs_meta import UseAwardSheetDialogMeta
from gui import DialogsInterface
from gui.game_control import restore_contoller
from gui.shared.formatters.tankmen import formatDeletedTankmanStr
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.vehicle_collector_helper import isAvailableForPurchase
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.money import Currency
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, I18nInfoDialogMeta, DIALOG_BUTTON_ID, IconPriceDialogMeta, IconDialogMeta, PMConfirmationDialogMeta, TankmanOperationDialogMeta, HtmlMessageDialogMeta, HtmlMessageLocalDialogMeta, CheckBoxDialogMeta, CrewSkinsRemovalCompensationDialogMeta, CrewSkinsRemovalDialogMeta
from helpers import dependency
from items.components import skills_constants
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
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


def _wrapHtmlMessage(message):
    return makeHtmlString('html_templates:lobby/dialogs', 'questsDialogAlert', {'message': message})


class ProcessorPlugin(object):

    class TYPE(object):
        VALIDATOR = 0
        CONFIRMATOR = 1

    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, pluginType, isAsync=False, isEnabled=True):
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


class AwaitConfirmator(ProcessorPlugin):

    def __init__(self, isEnabled=True):
        super(AwaitConfirmator, self).__init__(self.TYPE.CONFIRMATOR, isAsync=True, isEnabled=isEnabled)

    @async
    @future_async.async
    def confirm(self, callback):
        Waiting.suspend(lockerID=id(self))
        yield future_async.await(self._confirm(callback))
        Waiting.resume(lockerID=id(self))

    @future_async.async
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

    def __init__(self, vehicle, role, tankman, isEnabled=True):
        super(VehicleRoleValidator, self).__init__(isEnabled)
        self.vehicle = vehicle
        self.role = role
        self.tankman = tankman

    def _validate(self):
        if self.vehicle is None:
            return makeError('invalid_vehicle')
        else:
            if self.vehicle is not None:
                mainRoles = set((r[0] for r in self.vehicle.descriptor.type.crewRoles))
                if self.role not in mainRoles:
                    return makeError('invalid_role')
                td = self.tankman.descriptor
                if not tankmen.tankmenGroupHasRole(td.nationID, td.gid, td.isPremium, self.role):
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
            if not item.isElite and not item.isOnlyForEventBattles:
                return makeError('vehicle_not_elite')

        return makeSuccess()


class CollectibleVehiclesValidator(SyncValidator):

    def __init__(self, vehicleCD):
        super(CollectibleVehiclesValidator, self).__init__()
        self.__vehicleCD = vehicleCD

    def _validate(self):
        vehicle = self.itemsCache.items.getItemByCD(int(self.__vehicleCD))
        if vehicle is None:
            return makeError('invalid_vehicle')
        else:
            return makeError('not_unlocked_nation') if vehicle.isCollectible and not isAvailableForPurchase(vehicle) else makeSuccess()


class CompatibilityValidator(SyncValidator):

    def __init__(self, vehicle, module, slotIdx=0):
        super(CompatibilityValidator, self).__init__()
        self.vehicle = vehicle
        self.module = module
        self.slotIdx = slotIdx

    def _checkCompatibility(self):
        return makeSuccess()

    def _validate(self):
        success, errMsg = self._checkCompatibility()
        return makeError('error_{}'.format(errMsg.replace(' ', '_'))) if not success else makeSuccess()


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
        return self.module.mayInstall(self.vehicle, 0, self.gunCD)

    def _validate(self):
        success, errMsg = self._checkCompatibility()
        return makeError('error_{}'.format(errMsg.replace(' ', '_'))) if not success else makeSuccess()


class CompatibilityRemoveValidator(CompatibilityValidator):

    def _checkCompatibility(self):
        return self.module.mayRemove(self.vehicle)


class MoneyValidator(SyncValidator):

    def __init__(self, price):
        super(MoneyValidator, self).__init__()
        self.price = price

    def _validate(self):
        stats = self.itemsCache.items.stats
        shortage = stats.money.getShortage(self.price)
        if shortage:
            currency = shortage.getCurrency(byWeight=False)
            if currency == Currency.GOLD and not stats.mayConsumeWalletResources:
                error = GUI_ITEM_ECONOMY_CODE.WALLET_NOT_AVAILABLE
            else:
                error = GUI_ITEM_ECONOMY_CODE.getMoneyError(currency)
            return makeError(error)
        return makeSuccess()


class WalletValidator(SyncValidator):

    def _validate(self):
        stats = self.itemsCache.items.stats
        return makeError(GUI_ITEM_ECONOMY_CODE.WALLET_NOT_AVAILABLE) if not stats.mayConsumeWalletResources else makeSuccess()


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
            currency = shortage.getCurrency(byWeight=True)
            if currency not in errors:
                _logger.warning('Unexpected case: unknown currency!')
                return makeError()
            return makeError(errors[currency])
        else:
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

    def __init__(self, tankman, isEnabled=True):
        super(TankmanDropSkillValidator, self).__init__(isEnabled)
        self.__tankman = tankman

    def _validate(self):
        return makeSuccess() if self.__tankman is not None and self.__tankman.skills else makeError('server_error')


class GroupOperationsValidator(SyncValidator):
    AVAILABLE_OPERATIONS = range(3)

    def __init__(self, group, operation=0, isEnabled=True):
        super(GroupOperationsValidator, self).__init__(isEnabled)
        self.group = group
        self.operation = operation

    def _validate(self):
        if not self.group:
            return makeError('empty_list')
        return makeError('invalid_operation') if self.operation not in self.AVAILABLE_OPERATIONS else makeSuccess()


class DialogAbstractConfirmator(AsyncConfirmator):
    _dialogsInterfaceMethod = staticmethod(DialogsInterface.showDialog)

    def __init__(self, activeHandler=None, isEnabled=True):
        super(DialogAbstractConfirmator, self).__init__(isEnabled=isEnabled)
        self.activeHandler = activeHandler or (lambda : True)

    def __del__(self):
        self.activeHandler = None
        return

    def _makeMeta(self):
        raise NotImplementedError

    def _gfMakeMeta(self):
        return None

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
            gfMetaData = self._gfMakeMeta()
            if gfMetaData:
                isOk, data = yield gfMetaData
                result = makeSuccess(**data) if isOk else makeError()
                callback(result)
                return
            isOk = yield self._dialogsInterfaceMethod(meta=self._makeMeta())
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


class BuyAndInstallConfirmator(ModuleBuyerConfirmator):

    def __init__(self, localeKey, ctx=None, activeHandler=None, isEnabled=True, item=None):
        super(BuyAndInstallConfirmator, self).__init__(localeKey, ctx, activeHandler, isEnabled)
        self.item = item

    def _gfMakeMeta(self):
        from gui.shared.event_dispatcher import showOptionalDeviceBuyAndInstall
        return partial(showOptionalDeviceBuyAndInstall, self.item.intCD) if self.item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else None


class BCBuyAndInstallConfirmator(BuyAndInstallConfirmator):
    _dialogsInterfaceMethod = staticmethod(DialogsInterface.showBCConfirmationDialog)
    _BOOTCAM_LABELS_PATH = '../maps/icons/bootcamp/lines'
    _VEHICLE_COMPONENTS_LABLES = {'vehicleChassis': 'bcChassis.png',
     'vehicleTurret': 'bcTurret.png',
     'vehicleGun': 'bcGun.png',
     'vehicleRadio': 'bcRadio.png',
     'vehicleWheels': 'bcWheels.png',
     'vehicleEngine': 'bcEngine.png'}

    @staticmethod
    def getPath(itemTypeName):
        dataStr = ''
        if itemTypeName in BCBuyAndInstallConfirmator._VEHICLE_COMPONENTS_LABLES:
            dataStr = '/'.join((BCBuyAndInstallConfirmator._BOOTCAM_LABELS_PATH, BCBuyAndInstallConfirmator._VEHICLE_COMPONENTS_LABLES[itemTypeName]))
        return dataStr

    def _makeMeta(self):
        dialogData = {'label': backport.text(R.strings.bootcamp.message.confirmBuyAndInstall.module.title()).format(self.item.longUserName),
         'labelExecute': backport.text(R.strings.bootcamp.message.confirmBuyAndInstall.module.buttonLabel()),
         'icon': BCBuyAndInstallConfirmator.getPath(self.item.itemTypeName),
         'costValue': self.ctx['price'],
         'isBuy': True}
        return dialogs.BCConfirmDialogMeta(dialogData)


class BuyAndStorageConfirmator(ModuleBuyerConfirmator):

    def __init__(self, localeKey, ctx=None, activeHandler=None, isEnabled=True, item=None):
        super(BuyAndStorageConfirmator, self).__init__(localeKey, ctx, activeHandler, isEnabled)
        self.item = item

    def _gfMakeMeta(self):
        from gui.shared.event_dispatcher import showOptionalDeviceBuyAndStorage
        return partial(showOptionalDeviceBuyAndStorage, self.item.intCD) if self.item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE else None


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


class CrewSkinsCompensationDialogConfirmator(I18nMessageAbstractConfirmator):

    def __init__(self, localeKey, reasonSuffix, ctx=None, activeHandler=None, isEnabled=True):
        super(CrewSkinsCompensationDialogConfirmator, self).__init__(localeKey, ctx, activeHandler, isEnabled)
        self.reasonSuffix = reasonSuffix

    def _makeMeta(self):
        return CrewSkinsRemovalCompensationDialogMeta(self.localeKey, self.reasonSuffix, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class CrewSkinsRoleChangeRemovalConfirmator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return CrewSkinsRemovalDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class IconPriceMessageConfirmator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return IconPriceDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class DemountDeviceConfirmator(IconPriceMessageConfirmator):
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, isEnabled=True, item=None):
        super(DemountDeviceConfirmator, self).__init__(None, isEnabled=isEnabled)
        self.item = item
        return

    def _gfMakeMeta(self):
        from gui.shared import event_dispatcher
        demountKit = self._goodiesCache.getDemountKit()
        isDkEnabled = demountKit and demountKit.enabled
        if self.item.isDeluxe or not isDkEnabled:
            showDialog = partial(event_dispatcher.showOptionalDeviceDemountSinglePrice, self.item.intCD)
        else:
            showDialog = partial(event_dispatcher.showOptionalDeviceDemount, self.item.intCD)
        return showDialog


class IconMessageConfirmator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return IconDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class InstallDeviceConfirmator(MessageConfirmator):

    def __init__(self, isEnabled=True, item=None):
        super(InstallDeviceConfirmator, self).__init__(None, isEnabled=isEnabled)
        self.item = item
        return

    def _gfMakeMeta(self):
        from gui.shared import event_dispatcher
        return partial(event_dispatcher.showOptionalDeviceInstall, self.item.intCD)


class DestroyDeviceConfirmator(IconMessageConfirmator):

    def __init__(self, isEnabled=True, item=None):
        super(DestroyDeviceConfirmator, self).__init__(None, isEnabled=isEnabled)
        self.item = item
        return

    def _gfMakeMeta(self):
        from gui.shared import event_dispatcher
        return partial(event_dispatcher.showOptionalDeviceDestroy, self.item.intCD)


class MessageInformator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return I18nInfoDialogMeta(self.localeKey, self.ctx, self.ctx)


class VehicleSlotsConfirmator(MessageInformator):

    def __init__(self, isEnabled=True):
        super(VehicleSlotsConfirmator, self).__init__('haveNoEmptySlots', isEnabled=isEnabled)

    def _activeHandler(self):
        return self.itemsCache.items.inventory.getFreeSlots(self.itemsCache.items.stats.vehicleSlots) <= 0


class VehicleFreeLimitConfirmator(MessageInformator):

    def __init__(self, vehicle, crewType):
        super(VehicleFreeLimitConfirmator, self).__init__('freeVehicleLeftLimit')
        self.vehicle = vehicle
        self.crewType = crewType

    def _activeHandler(self):
        return not self.vehicle.buyPrices.itemPrice.isDefined() and self.crewType < 1 and not self.itemsCache.items.stats.freeVehiclesLeft


class PMValidator(SyncValidator):

    def __init__(self, quests):
        super(PMValidator, self).__init__()
        self.quests = quests

    def _validate(self):
        for quest in self.quests:
            if quest is None:
                return makeError('WRONG_ARGS_TYPE')
            if not quest.isUnlocked():
                return makeError('NOT_UNLOCKED_QUEST')

        return makeSuccess()


class PMPawnValidator(SyncValidator):

    def __init__(self, quests):
        super(PMPawnValidator, self).__init__()
        self.quests = quests

    def _validate(self):
        for quest in self.quests:
            if quest is None:
                return makeError('WRONG_ARGS_TYPE')
            if not quest.canBePawned():
                return makeError('CANNOT_BE_PAWNED')

        return makeSuccess()


class _EventsCacheValidator(SyncValidator):
    eventsCache = dependency.descriptor(IEventsCache)


class PMLockedByVehicle(_EventsCacheValidator):

    def __init__(self, branch, quests, messageKeyPrefix=''):
        super(PMLockedByVehicle, self).__init__()
        self._messageKeyPrefix = messageKeyPrefix
        self.quests = quests
        self._lockedChains = self.eventsCache.getLockedQuestTypes(branch)

    def _validate(self):
        for quest in self.quests:
            if quest.getMajorTag() in self._lockedChains:
                return makeError(self._messageKeyPrefix + 'LOCKED_BY_VEHICLE_QUEST', questName=quest.getShortUserName())

        return makeSuccess()


class PMSlotsValidator(SyncValidator):

    def __init__(self, questsProgress, isEnabled=True, removedCount=0):
        super(PMSlotsValidator, self).__init__(isEnabled)
        self.__removedCount = removedCount
        self._questsProgress = questsProgress

    def _validate(self):
        return makeError('NOT_ENOUGH_SLOTS') if not self._questsProgress.getPersonalMissionsFreeSlots(self.__removedCount) else makeSuccess()


class PMRewardValidator(SyncValidator):

    def __init__(self, quest):
        super(PMRewardValidator, self).__init__()
        self.quest = quest

    def _validate(self):
        return makeError('NO_REWARD') if not self.quest.needToGetReward() else makeSuccess()


class PMFreeTokensValidator(_EventsCacheValidator):

    def __init__(self, quest, isEnabled=True):
        super(PMFreeTokensValidator, self).__init__(isEnabled)
        self.quest = quest
        self._branch = quest.getPMType().branch

    def _validate(self):
        return makeError('NOT_ENOUGH_FREE_TOKENS') if self.eventsCache.getPersonalMissions().getFreeTokensCount(self._branch) < self.quest.getPawnCost() else makeSuccess()


class TokenValidator(_EventsCacheValidator):

    def __init__(self, tokenID, amount, isEnabled=True):
        super(TokenValidator, self).__init__(isEnabled)
        self._tokenID = tokenID
        self._amount = amount

    def _validate(self):
        return makeError('NOT_ENOUGH_TOKENS') if self.eventsCache.questsProgress.getTokenCount(self._tokenID) < self._amount else makeSuccess()


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


class PMSelectConfirmator(CheckBoxConfirmator):

    def __init__(self, quest, oldQuest, settingFieldName, activeHandler=None, isEnabled=True):
        super(PMSelectConfirmator, self).__init__(settingFieldName=settingFieldName, activeHandler=activeHandler, isEnabled=isEnabled)
        self.quest = quest
        self.oldQuest = oldQuest

    def _makeMeta(self):
        return CheckBoxDialogMeta('questsConfirmDialog', messageCtx={'newQuest': self.quest.getUserName(),
         'oldQuest': self.oldQuest.getUserName()})


class PMProgressResetConfirmator(DialogAbstractConfirmator):

    def __init__(self, quest, oldQuest, activeHandler=None, isEnabled=True):
        super(PMProgressResetConfirmator, self).__init__(activeHandler=activeHandler, isEnabled=isEnabled)
        self.quest = quest
        self.oldQuest = oldQuest

    def _makeMeta(self):
        return PMConfirmationDialogMeta('questsConfirmProgressDialog', messageCtx={'newQuest': self.quest.getUserName(),
         'oldQuest': self.oldQuest.getUserName(),
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_90X84,
         'alert': _wrapHtmlMessage(backport.text(R.strings.dialogs.questsConfirmProgressDialog.message.alert()))})


class PMDismissWithProgressConfirmator(DialogAbstractConfirmator):

    def __init__(self, quest, activeHandler=None, isEnabled=True):
        super(PMDismissWithProgressConfirmator, self).__init__(activeHandler=activeHandler, isEnabled=isEnabled)
        self.quest = quest

    def _makeMeta(self):
        return PMConfirmationDialogMeta('questsDismissProgressDialog', messageCtx={'quest': self.quest.getUserName(),
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_90X84,
         'alert': _wrapHtmlMessage(backport.text(R.strings.dialogs.questsDismissProgressDialog.message.alert()))})


class PMDiscardConfirmator(DialogAbstractConfirmator):

    def __init__(self, curQuest, activeHandler=None, isEnabled=True):
        super(PMDiscardConfirmator, self).__init__(activeHandler=activeHandler, isEnabled=isEnabled)
        self.curQuest = curQuest

    def _makeMeta(self):
        return PMConfirmationDialogMeta('questsConfirmDiscardDialog', messageCtx={'curQuest': self.curQuest.getUserName(),
         'icon': RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_90X84,
         'alert': _wrapHtmlMessage(backport.text(R.strings.dialogs.questsConfirmDiscardDialog.message.alert()))})


class PMPawnConfirmator(DialogAbstractConfirmator):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, quest, activeHandler=None, isEnabled=True):
        super(PMPawnConfirmator, self).__init__(activeHandler=activeHandler, isEnabled=isEnabled)
        self.quest = quest
        self._branch = quest.getPMType().branch

    def _activeHandler(self):
        return self.quest.canBePawned()

    def _makeMeta(self):
        return UseAwardSheetDialogMeta(self.quest, self.eventsCache.getPersonalMissions().getFreeTokensCount(self._branch))


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
        if self.skillName not in skills_constants.ACTIVE_SKILLS:
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
        self._tankman = tankman

    def _validate(self):
        return makeError('FORBIDDEN') if tankmen.ownVehicleHasTags(self._tankman.strCD, (VEHICLE_TAGS.CREW_LOCKED,)) else makeSuccess()


class TankmanChangePassportValidator(TankmanLockedValidator):

    def _validate(self):
        return makeError('FORBIDDEN') if self._tankman.descriptor.getRestrictions().isPassportReplacementForbidden() else super(TankmanChangePassportValidator, self)._validate()


class BattleBoosterConfirmator(I18nMessageAbstractConfirmator):

    def __init__(self, localeKey, notSuitableLocaleKey, vehicle, battleBooster, isEnabled=True):
        self.__notSuitableLocaleKey = notSuitableLocaleKey
        self.__vehicle = vehicle
        self.__battleBooster = battleBooster
        super(BattleBoosterConfirmator, self).__init__(localeKey, isEnabled=isEnabled)

    def _activeHandler(self):
        return not self.__battleBooster.isAffectsOnVehicle(self.__vehicle)

    def _makeMeta(self):
        data = self.itemsCache.items.getItems(GUI_ITEM_TYPE.OPTIONALDEVICE, REQ_CRITERIA.VEHICLE.SUITABLE([self.__vehicle], [GUI_ITEM_TYPE.OPTIONALDEVICE])).values()
        optDevicesList = [ device for device in data if self.__battleBooster.isOptionalDeviceCompatible(device) ]
        ctx = {'devices': ', '.join([ device.userName for device in optDevicesList ])}
        localeKey = self.localeKey if optDevicesList else self.__notSuitableLocaleKey
        return I18nConfirmDialogMeta(localeKey, meta=HtmlMessageLocalDialogMeta('html_templates:lobby/dialogs', localeKey, ctx=ctx))


class BadgesValidator(SyncValidator):

    def __init__(self, badges):
        super(BadgesValidator, self).__init__()
        self.badges = badges

    def _validate(self):
        allBadges = self.itemsCache.items.getBadges()
        for badgeID in self.badges:
            if badgeID not in allBadges:
                return makeError('WRONG_ARGS_TYPE')
            badge = allBadges[badgeID]
            if not badge.isAchieved:
                return makeError('NOT_UNLOCKED_BADGE')

        return makeSuccess()


class BattleBoosterValidator(SyncValidator):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, boosters, isEnabled=True):
        super(BattleBoosterValidator, self).__init__(isEnabled)
        for booster in boosters:
            if booster.itemTypeID != GUI_ITEM_TYPE.BATTLE_BOOSTER:
                raise SoftException("Expected type 'BattleBoosters' for BattleBoosterValidator, not '{}'!".format(type(booster)))

        self.boosters = boosters

    def _validate(self):
        return makeError('disabledService') if self.boosters and not self.__lobbyContext.getServerSettings().isBattleBoostersEnabled() else makeSuccess()


class DismountForDemountKitValidator(SyncValidator):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, vehicle, itemsForDemountKit):
        super(DismountForDemountKitValidator, self).__init__(isEnabled=bool(itemsForDemountKit))
        self.vehicle = vehicle
        self.itemsForDemountKit = itemsForDemountKit
        self.demountKit = self.goodiesCache.getDemountKit()

    def _validate(self):
        if not self.demountKit:
            return makeError()
        if not self.demountKit.enabled:
            return makeError('demount_kit_disabled')
        if self.demountKit.inventoryCount < len(self.itemsForDemountKit):
            return makeError()
        for opDev in self.itemsForDemountKit:
            if opDev.itemTypeID != GUI_ITEM_TYPE.OPTIONALDEVICE:
                return makeError()
            if opDev.isDeluxe:
                return makeError()

        return makeSuccess()

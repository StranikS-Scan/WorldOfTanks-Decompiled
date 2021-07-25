# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/plugins.py
from functools import partial
import logging
from collections import namedtuple
import async as future_async
import constants
from adisp import process, async
from account_helpers import isLongDisconnectedFromCenter
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view import dialogs
from gui.goodies.demount_kit import getDemountKitForOptDevice
from gui.shared.gui_items.artefacts import OptionalDevice
from gui.shared.gui_items.vehicle_equipment import EMPTY_ITEM
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
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, I18nInfoDialogMeta, DIALOG_BUTTON_ID, IconPriceDialogMeta, IconDialogMeta, PMConfirmationDialogMeta, TankmanOperationDialogMeta, HtmlMessageDialogMeta, HtmlMessageLocalDialogMeta, CheckBoxDialogMeta
from helpers import dependency
from items.components import skills_constants
from items.components.c11n_constants import SeasonType
from gui.shared.items_cache import getFreeDormsRooms
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
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
    detachmentCache = dependency.descriptor(IDetachmentCache)

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


class Development(SyncValidator):

    def _validate(self):
        return makeError('server_error') if not constants.IS_DEVELOPMENT else makeSuccess()


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


class VehicleDetachmentValidator(SyncValidator):

    def __init__(self, vehicle, isEnabled=True):
        super(VehicleDetachmentValidator, self).__init__(isEnabled)
        self.vehicle = vehicle

    def _validate(self):
        if self.vehicle is None:
            return makeError('invalid_vehicle')
        else:
            return makeError('vehicle_has_old_crew') if self.vehicle.hasOldCrew else makeSuccess()


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


class VehicleCrewDismissValidator(SyncValidator):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehicle, isDismiss, isEnabled=True):
        super(VehicleCrewDismissValidator, self).__init__(isEnabled)
        self._vehicle = vehicle
        self._isDismiss = isDismiss

    def _validate(self):
        if self._isDismiss and not self.__lobbyContext.getServerSettings().isDissolveDetachmentEnabled():
            return makeError('detachment_dismiss_switched_off')
        return makeError('vehicle_crew_forbidden_dismiss') if self._isDismiss and self._vehicle.hasOldCrew and not self._vehicle.isCrewLocked else makeSuccess()


class VehicleTradeInValidator(SyncValidator):

    def __init__(self, vehicleToBuy, vehicleToTradeOff, isEnabled=True):
        super(VehicleTradeInValidator, self).__init__(isEnabled)
        self.vehicleToBuy = vehicleToBuy
        self.vehicleToTradeOff = vehicleToTradeOff

    def _validate(self):
        if not self.vehicleToBuy.canTradeIn:
            return makeError('vehicle_cannot_trade_in')
        return makeError('vehicle_cannot_trade_off') if not self.vehicleToTradeOff.canTradeOff else makeSuccess()


class VehiclePersonalTradeInValidator(SyncValidator):

    def __init__(self, vehicleToBuy, vehicleToTradeOff, isEnabled=True):
        super(VehiclePersonalTradeInValidator, self).__init__(isEnabled)
        self.vehicleToBuy = vehicleToBuy
        self.vehicleToTradeOff = vehicleToTradeOff

    def _validate(self):
        if not self.vehicleToBuy.canPersonalTradeInBuy:
            return makeError('vehicle_cannot_trade_in')
        return makeError('vehicle_cannot_trade_off') if not self.vehicleToTradeOff.canPersonalTradeInSale else makeSuccess()


class VehicleLockValidator(SyncValidator):

    def __init__(self, vehicle, isEnabled=True):
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

    def __init__(self, price, byCurrencyError=True):
        super(MoneyValidator, self).__init__()
        self.price = price
        self.__byCurrencyError = byCurrencyError

    def _validate(self):
        stats = self.itemsCache.items.stats
        shortage = stats.money.getShortage(self.price)
        if shortage:
            if shortage.get(Currency.GOLD, 0) > 0 and not stats.mayConsumeWalletResources:
                error = GUI_ITEM_ECONOMY_CODE.WALLET_NOT_AVAILABLE
            elif self.__byCurrencyError:
                error = GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_MONEY
                for currency in Currency.ALL:
                    if shortage.get(currency, 0) > 0:
                        error = GUI_ITEM_ECONOMY_CODE.getCurrencyError(currency)
                        break

            else:
                error = GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_MONEY
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


class DormitoriesSlotsValidator(SyncValidator):

    def __init__(self, roomsNeeded=1, isEnabled=True):
        super(DormitoriesSlotsValidator, self).__init__(isEnabled)
        self.roomsNeeded = roomsNeeded

    def _validate(self):
        return makeError('not_enough_space') if self.roomsNeeded > 0 and self.roomsNeeded > getFreeDormsRooms(itemsCache=self.itemsCache) else makeSuccess()


class DormitoriesBuyingEnableValidator(SyncValidator):

    def _validate(self):
        return makeError('switched_off') if not self.itemsCache.items.shop.getDormitoryBuyingSettings else makeSuccess()


class DetachmentValidator(SyncValidator):

    def __init__(self, detInvID, isEnabled=True):
        super(DetachmentValidator, self).__init__(isEnabled)
        self.detachment = self.detachmentCache.getDetachment(detInvID)

    def _validate(self):
        return makeError('invalid_detachment_id') if not self.detachment else makeSuccess()


class CrewSkinValidator(SyncValidator):

    def __init__(self, skinID, detachment, isEnabled=True):
        super(CrewSkinValidator, self).__init__(isEnabled)
        self.skin = self.itemsCache.items.getCrewSkin(skinID)
        self.detachment = detachment

    def _validate(self):
        if not self.skin:
            return makeError('invalid_skin_id')
        nation = self.skin.getNation()
        return makeError('invalid_nation') if nation and self.detachment.nationName != nation else makeSuccess()


class InstructorSlotValidator(SyncValidator):

    def __init__(self, detInvID, slotID, isEnabled=True):
        super(InstructorSlotValidator, self).__init__(isEnabled)
        self.detachment = self.detachmentCache.getDetachment(detInvID)
        self.slotID = slotID

    def _validate(self):
        if not self.detachment:
            return makeError('invalid_detachment')
        return makeError('invalid_instructor_slot') if not 0 <= self.slotID < len(self.detachment.getInstructorsIDs()) else makeSuccess()


class DetachmentSwapSlotsValidator(SyncValidator):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, detInvID, slotsType, slot1Index, slot2Index, isEnabled=True):
        super(DetachmentSwapSlotsValidator, self).__init__(isEnabled)
        self.detachment = self.detachmentCache.getDetachment(detInvID)
        self.slotsType = slotsType
        self.slot1Index = slot1Index
        self.slot2Index = slot2Index

    def _validate(self):
        if not self.detachment:
            return makeError('invalid_detachment')
        elif self.slot1Index == self.slot2Index:
            return makeError('same_slot')
        slots = self.detachment.getDescriptor().getAllSlotsInfo(self.slotsType)
        slot1 = slots[self.slot1Index]
        slot2 = slots[self.slot2Index]
        if not slot1.available or slot1.locked or slot1.typeCompDescr is None:
            return makeError('invalid_source_slot')
        else:
            return makeError('invalid_target_slot') if not slot2.available or slot2.locked else makeSuccess()


class DetachmentDemobilizeValidator(SyncValidator):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, detachment, isEnabled=True):
        super(DetachmentDemobilizeValidator, self).__init__(isEnabled)
        self.detachment = detachment

    def _validate(self):
        if not self.__lobbyContext.getServerSettings().isDissolveDetachmentEnabled():
            return makeError('switched_off')
        if not self.detachment:
            return makeError('invalid_detachment')
        return makeError('detachment_already_demobilize') if self.detachment.isInRecycleBin else makeSuccess()


class DetachmentRestoreValidator(SyncValidator):

    def __init__(self, detachment, isEnabled=True):
        super(DetachmentRestoreValidator, self).__init__(isEnabled)
        self.detachment = detachment

    def _validate(self):
        if not self.detachment:
            return makeError('invalid_detachment')
        return makeError('detachment_not_demobilize') if not self.detachment.isInRecycleBin else makeSuccess()


class InstructorValidator(SyncValidator):

    def __init__(self, instrInvID, isEnabled=True):
        super(InstructorValidator, self).__init__(isEnabled)
        self.instrInvID = instrInvID

    def _validate(self):
        instructor = self.detachmentCache.getInstructor(self.instrInvID)
        return makeError('incorrect_instructor_id') if not instructor else makeSuccess()


class InstructorSlotsBreakerValidator(SyncValidator):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def _validate(self):
        return makeError('switched_off') if not self.__lobbyContext.getServerSettings().isInstructorSlotsEnabled() else makeSuccess()


class InstructorAlreadyHasPerksValidator(SyncValidator):

    def __init__(self, instrInvID, isEnabled=True):
        super(InstructorAlreadyHasPerksValidator, self).__init__(isEnabled)
        self.instrInvID = instrInvID

    def _validate(self):
        instructor = self.detachmentCache.getInstructor(self.instrInvID)
        return makeError('instructor_already_has_bonuses') if instructor.descriptor.perksIDs else makeSuccess()


class UnpackedInstructorValidator(SyncValidator):

    def __init__(self, instrInvID, isEnabled=True):
        super(UnpackedInstructorValidator, self).__init__(isEnabled)
        self.instrInvID = instrInvID

    def _validate(self):
        instructor = self.detachmentCache.getInstructor(self.instrInvID)
        return makeError('instructor_is_not_token') if not instructor.isToken() else makeSuccess()


class UnpackedInstructorProfessionValidator(SyncValidator):

    def __init__(self, instrInvID, professionID, isEnabled=True):
        super(UnpackedInstructorProfessionValidator, self).__init__(isEnabled)
        self.instrInvID = instrInvID
        self.professionID = professionID

    def _validate(self):
        instructor = self.detachmentCache.getInstructor(self.instrInvID)
        professionSettings = instructor.getInstructorSettings().professionVariants
        return makeError('incorrect_instructor_profession') if professionSettings is not None and self.professionID not in professionSettings else makeSuccess()


class UnpackedInstructorNationIDValidator(SyncValidator):

    def __init__(self, instrInvID, nationID, isEnabled=True):
        super(UnpackedInstructorNationIDValidator, self).__init__(isEnabled)
        self.instrInvID = instrInvID
        self.nationID = nationID

    def _validate(self):
        instructor = self.detachmentCache.getInstructor(self.instrInvID)
        if instructor.descriptor.isNationSet():
            if instructor.nationID != self.nationID:
                return makeError('instructor_already_has_nation')
        elif self.nationID not in instructor.getInstructorSettings().nations:
            return makeError('incorrect_nation_id')
        return makeSuccess()


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


class IconPriceMessageConfirmator(I18nMessageAbstractConfirmator):

    def _makeMeta(self):
        return IconPriceDialogMeta(self.localeKey, self.ctx, self.ctx, focusedID=DIALOG_BUTTON_ID.SUBMIT)


class DemountDeviceConfirmator(IconPriceMessageConfirmator):
    _goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, isEnabled=True, item=None, vehicle=None):
        super(DemountDeviceConfirmator, self).__init__(None, isEnabled=isEnabled)
        self.item = item
        self.__vehicleToInstall = vehicle
        return

    def _gfMakeMeta(self):
        from gui.shared import event_dispatcher
        demountKit, _ = getDemountKitForOptDevice(self.item)
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


class TankmenLockedValidator(SyncValidator):

    def __init__(self, tmen, isEnabled=True, checkLockCrew=True):
        super(TankmenLockedValidator, self).__init__(isEnabled=isEnabled)
        self._tmen = tmen
        self._checkLockCrew = checkLockCrew

    def _validate(self):
        vehicles = {}
        for tman in self._tmen:
            if not tman or tman.vehicleInvID in vehicles:
                continue
            vehicle = self.itemsCache.items.getVehicle(tman.vehicleInvID)
            if vehicle:
                if vehicle.isLocked:
                    return makeError('tankman_locked')
                vehicles[tman.vehicleInvID] = vehicle

        if self._checkLockCrew:
            if any((tman and tankmen.ownVehicleHasTags(tman.strCD, (VEHICLE_TAGS.CREW_LOCKED,)) for tman in self._tmen)):
                return makeError('FORBIDDEN')
        return makeSuccess()


class IsLongDisconnectedFromCenter(SyncValidator):

    def _validate(self):
        return makeError('disconnected_from_center') if isLongDisconnectedFromCenter() else makeSuccess()


class VehicleCrewLockedValidator(SyncValidator):

    def __init__(self, vehicle, isEnabled=True):
        super(VehicleCrewLockedValidator, self).__init__(isEnabled)
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
        ctx = {'devices': ', '.join(set([ device.userName for device in optDevicesList ]))}
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
        if self.boosters and not self.__lobbyContext.getServerSettings().isBattleBoostersEnabled():
            return makeError('disabledService')
        isCrewBattleBoostersEnabled = not self.__lobbyContext.getServerSettings().isCrewBattleBoostersEnabled()
        return makeError('disabledService') if any((booster.isCrewBooster() and not isCrewBattleBoostersEnabled for booster in self.boosters)) else makeSuccess()


class DismountForDemountKitValidator(SyncValidator):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, vehicle, itemsForDemountKit):
        super(DismountForDemountKitValidator, self).__init__(isEnabled=bool(itemsForDemountKit))
        self.vehicle = vehicle
        self.itemsForDemountKit = itemsForDemountKit

    def _validate(self):
        spentDemountKits = {}
        for opDev in self.itemsForDemountKit:
            if opDev.itemTypeID != GUI_ITEM_TYPE.OPTIONALDEVICE or opDev.isRemovable:
                return makeError()
            if opDev.isDeluxe:
                return makeError()
            demountKit, _ = getDemountKitForOptDevice(opDev)
            if demountKit is None:
                return makeError()
            if not demountKit.enabled:
                return makeError('demount_kit_disabled')
            spentDemountKits[demountKit.goodieID] = spentDemountKits.get(demountKit.goodieID, 0) + 1
            if demountKit.inventoryCount < spentDemountKits[demountKit.goodieID]:
                return makeError()

        return makeSuccess()


class LayoutInstallValidator(SyncValidator):

    def __init__(self, vehicle, isEnabled=True):
        self._vehicle = vehicle
        super(LayoutInstallValidator, self).__init__(isEnabled)

    def _validate(self):
        layout = self._getLayout()
        if not all((item.itemTypeID == self._getItemType() for item in layout.getItems())):
            return makeError('WRONG_ITEMS_TYPE')
        return makeError('IMPOSSIBLE_INSTALL') if not all((item.mayInstall(self._vehicle, slotIdx=slotIdx) for slotIdx, item in enumerate(layout) if item != EMPTY_ITEM and item not in self._getInstalled())) else makeSuccess()

    def _getLayout(self):
        raise NotImplementedError()

    def _getInstalled(self):
        raise NotImplementedError()

    def _getItemType(self):
        raise NotImplementedError()


class OptionalDevicesInstallValidator(LayoutInstallValidator):

    def _getLayout(self):
        return self._vehicle.optDevices.layout

    def _getInstalled(self):
        return self._vehicle.optDevices.installed

    def _getItemType(self):
        return GUI_ITEM_TYPE.OPTIONALDEVICE


class BattleAbilitiesValidator(LayoutInstallValidator):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def _validate(self):
        if not self.__epicMetaGameCtrl.isEnabled():
            return makeError('epic_mode_disabled')
        return makeError('battle_abilities_locked') if not all((item.innationID in self.__epicMetaGameCtrl.getUnlockedAbilityIds() for item in self._getLayout() if item != EMPTY_ITEM and item not in self._getInstalled())) else super(BattleAbilitiesValidator, self)._validate()

    def _getLayout(self):
        return self._vehicle.battleAbilities.layout

    def _getInstalled(self):
        return self._vehicle.battleAbilities.installed

    def _getItemType(self):
        return GUI_ITEM_TYPE.BATTLE_ABILITY


class ConsumablesInstallValidator(LayoutInstallValidator):

    def _getLayout(self):
        return self._vehicle.consumables.layout

    def _getInstalled(self):
        return self._vehicle.consumables.installed

    def _getItemType(self):
        return GUI_ITEM_TYPE.EQUIPMENT


class ShellsInstallValidator(LayoutInstallValidator):

    def _getLayout(self):
        return self._vehicle.shells.layout

    def _getInstalled(self):
        return self._vehicle.shells.installed

    def _getItemType(self):
        return GUI_ITEM_TYPE.SHELL


class BattleBoostersInstallValidator(LayoutInstallValidator):

    def _getLayout(self):
        return self._vehicle.battleBoosters.layout

    def _getInstalled(self):
        return self._vehicle.battleBoosters.installed

    def _getItemType(self):
        return GUI_ITEM_TYPE.BATTLE_BOOSTER


class CustomizationPurchaseValidator(SyncValidator):

    def __init__(self, outfitData):
        super(CustomizationPurchaseValidator, self).__init__()
        self.outfitData = outfitData

    def _validate(self):
        seasons = []
        styleID = None
        if not self.outfitData:
            return makeError('empty_request')
        else:
            for outfit, season in self.outfitData:
                if season not in SeasonType.RANGE:
                    return makeError('unsupported_season_type')
                if season not in seasons:
                    seasons.append(season)
                else:
                    return makeError('seasons_must_be_different')
                outfitId = outfit.id
                if styleID is None:
                    styleID = outfitId
                if styleID != outfitId:
                    return makeError('outfits_must_have_same_style')

            return makeSuccess()

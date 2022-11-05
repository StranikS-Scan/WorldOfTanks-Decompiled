# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/module_deconstruct_dialogs.py
from adisp import adisp_process
import logging
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.lobby.tank_setup.array_providers.opt_device import DeconstructOptDeviceStorageProvider, DeconstructOptDeviceOnVehicleProvider
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.shared import IItemsCache
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.module import ModuleDeconstruct
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.confirm_actions_with_equipment_dialog_model import ConfirmActionsWithEquipmentDialogModel, DialogType
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.current_balance_model import CurrentBalanceModel
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import MAX_ITEMS_FOR_OPERATION
_logger = logging.getLogger(__name__)

def _initBalance(viewModel, currency, itemsCache):
    cur = CurrentBalanceModel()
    cur.setCurrencyType(currency)
    money = itemsCache.items.stats.money
    cur.setCurrencyValue(money.get(currency, 0))
    balance = viewModel.getBalance()
    balance.clear()
    balance.addViewModel(cur)
    balance.invalidate()


def _initItemInfo(viewModel, device, currency):
    with viewModel.transaction() as model:
        model.detailsDevice.setOverlayType(device.getHighlightType())
        model.detailsDevice.setLevel(device.level)
        model.detailsDevice.setDeviceName(device.name)
        model.detailsPriceBlock.setCurrencyName(currency)
        model.detailsPriceBlock.setCountDevice(device.inventoryCount)
        actualPrices = device.sellPrices.itemPrice.price
        model.detailsPriceBlock.setPriceDevice(actualPrices.toSignDict().get(currency, 0))


class ConfirmInStorageDialogView(ViewImpl):
    __slots__ = ('__device', '__currency')
    LAYOUT_ID = R.views.lobby.tanksetup.dialogs.ConfirmActionsWithEquipmentDialog()
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemIntCD):
        settings = ViewSettings(layoutID=self.LAYOUT_ID, model=ConfirmActionsWithEquipmentDialogModel())
        super(ConfirmInStorageDialogView, self).__init__(settings)
        self.__device = self.__itemsCache.items.getItemByCD(itemIntCD)
        self.__currency = self.__device.sellPrices.itemPrice.price.getCurrency(byWeight=True)

    @property
    def viewModel(self):
        return super(ConfirmInStorageDialogView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ConfirmInStorageDialogView, self)._onLoading(*args, **kwargs)
        if self.__isModernized():
            self.viewModel.setDialogType(DialogType.DECONSTRUCTFROMSTORAGE)
            _initBalance(self.viewModel, self.__currency, self.__itemsCache)
            _initItemInfo(self.viewModel, self.__device, self.__currency)
        else:
            self.viewModel.setDialogType(DialogType.SELLFROMSTORAGE)
            _logger.error('[ConfirmInStorageDialogView] Initialization of view model was not implemented for non modernized devices.')
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(ConfirmInStorageDialogView, self)._finalize()

    def __addListeners(self):
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self.viewModel.onSell += self.__onSell
        self.viewModel.onDeconstruct += self.__onDeconstruct
        self.viewModel.onClose += self.__onClose

    def __removeListeners(self):
        self.viewModel.onSell -= self.__onSell
        self.viewModel.onDeconstruct -= self.__onDeconstruct
        self.viewModel.onClose -= self.__onClose
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onSell(self, *args, **kwargs):
        _logger.error('[ConfirmInStorageDialogView] Sale was not implemented.')

    @adisp_process
    def __onDeconstruct(self, count):
        Waiting.show('storage/forDeconstruct')
        result = yield ModuleDeconstruct(self.__device, min(count.get('count', 1), MAX_ITEMS_FOR_OPERATION)).request()
        Waiting.hide('storage/forDeconstruct')
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            self.destroyWindow()

    def __onClose(self, *args, **kwargs):
        self.destroyWindow()

    def __onMoneyUpdated(self, _):
        _initBalance(self.viewModel, self.__currency, self.__itemsCache)

    def __isModernized(self):
        return self.__device.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and self.__device.isModernized


class ConfirmOnSlotDialogView(DialogTemplateView):
    __slots__ = ('__device', '__currency', '__fromVehicle', '__curCount')
    LAYOUT_ID = R.views.lobby.tanksetup.dialogs.ConfirmActionsWithEquipmentDialog()
    VIEW_MODEL = ConfirmActionsWithEquipmentDialogModel
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemIntCD, fromVehicle=False):
        super(ConfirmOnSlotDialogView, self).__init__()
        self.__device = self.__itemsCache.items.getItemByCD(itemIntCD)
        self.__currency = self.__device.sellPrices.itemPrice.price.getCurrency(byWeight=True)
        self.__fromVehicle = fromVehicle
        self.__curCount = self.__device.inventoryCount if not fromVehicle else 1

    @property
    def viewModel(self):
        return super(ConfirmOnSlotDialogView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ConfirmOnSlotDialogView, self)._onLoading(*args, **kwargs)
        if self.__fromVehicle:
            self.viewModel.setDialogType(DialogType.DECONSTRUCTFROMSLOTS)
        else:
            self.viewModel.setDialogType(DialogType.DECONSTRUCTFROMSTORAGE)
        _initBalance(self.viewModel, self.__currency, self.__itemsCache)
        _initItemInfo(self.viewModel, self.__device, self.__currency)
        storageProvider = DeconstructOptDeviceStorageProvider()
        onVehicleProvider = DeconstructOptDeviceOnVehicleProvider()
        totalCount = sum((item.inventoryCount for item in storageProvider.getItems())) + len(onVehicleProvider.getItems())
        self.viewModel.setIsLastEquipt(totalCount == 1)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(ConfirmOnSlotDialogView, self)._finalize()

    def __addListeners(self):
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self.viewModel.onSell += self.__onSell
        self.viewModel.onDeconstruct += self.__onDeconstruct
        self.viewModel.onClose += self.__onClose

    def __removeListeners(self):
        self.viewModel.onSell -= self.__onSell
        self.viewModel.onDeconstruct -= self.__onDeconstruct
        self.viewModel.onClose -= self.__onClose
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onSell(self, *args, **kwargs):
        _logger.error('[ConfirmInStorageDialogView] Sale was not implemented.')

    def __onDeconstruct(self, count):
        self.__curCount = count.get('count', 1)
        self._setResult(DialogButtons.SUBMIT)

    def __onClose(self, *args, **kwargs):
        self._setResult(DialogButtons.CANCEL)

    def _getAdditionalData(self):
        return self.__curCount

    def __onMoneyUpdated(self, _):
        _initBalance(self.viewModel, self.__currency, self.__itemsCache)


class ConfirmInStorageDialogWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, itemIntCD, parent=None):
        super(ConfirmInStorageDialogWindow, self).__init__(WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=ConfirmInStorageDialogView(itemIntCD), parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW)

    def _finalize(self):
        self.__blur.fini()
        super(ConfirmInStorageDialogWindow, self)._finalize()

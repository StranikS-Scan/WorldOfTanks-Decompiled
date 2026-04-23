# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/opt_device_sell_dialog.py
from constants import OPT_DEVICES_RESTORE_SETTING
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import MAX_ITEMS_FOR_OPERATION
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.sell_view_model import SellViewModel, ModuleType
from gui.impl.lobby.tank_setup.dialogs.dialog_helpers.balance import initBalance
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.gui_items.processors.module import ModuleSeller
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class OptDeviceSellDialog(ViewImpl):
    __slots__ = ('__device',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    LAYOUT_ID = R.views.lobby.tanksetup.dialogs.Sell()

    def __init__(self, itemIntCD):
        settings = ViewSettings(layoutID=self.LAYOUT_ID, model=SellViewModel())
        super(OptDeviceSellDialog, self).__init__(settings)
        self.__device = self.__itemsCache.items.getItemByCD(itemIntCD)

    @property
    def viewModel(self):
        return super(OptDeviceSellDialog, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(OptDeviceSellDialog, self)._onLoading(*args, **kwargs)
        initBalance(self.viewModel.getBalance(), Currency.GUI_ALL, self.__itemsCache)
        self.__fillModel()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(OptDeviceSellDialog, self)._finalize()

    def __fillModel(self):
        device = self.__device
        currency = device.sellPrices.itemPrice.price.getCurrency(byWeight=True)
        with self.viewModel.transaction() as model:
            equipType = ModuleType.STANDARD
            if device.isDeluxe:
                equipType = ModuleType.IMPROVED
            elif device.isTrophy:
                equipType = ModuleType.TROPHY
            model.setIsOptDeviceRestored(self.__getOptDevicesRestoreState())
            model.setModuleType(equipType)
            model.equipment.setItem(device.getGUIEmblemID())
            model.equipment.setOverlayType(device.getOverlayType())
            model.equipment.setName(device.name)
            model.equipmentPrice.setType(currency)
            model.equipmentPrice.setAmount(device.inventoryCount)
            actualPrices = device.sellPrices.itemPrice.price
            model.equipmentPrice.setPrice(actualPrices.toSignDict().get(currency, 0))

    def __addListeners(self):
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self.viewModel.onSell += self.__onSell
        self.viewModel.onClose += self.__onClose
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def __removeListeners(self):
        self.viewModel.onSell -= self.__onSell
        self.viewModel.onClose -= self.__onClose
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onClose(self, *args, **kwargs):
        self.destroyWindow()

    def __onMoneyUpdated(self, _):
        initBalance(self.viewModel.getBalance(), Currency.GUI_ALL, self.__itemsCache)

    def __onServerSettingsChange(self, diff):
        if OPT_DEVICES_RESTORE_SETTING in diff:
            self.__fillModel()

    def __getOptDevicesRestoreState(self):
        return self.__lobbyContext.getServerSettings().isOptionalDeviceRestoreEnabled()

    @decorators.adisp_process('sellItem')
    def __onSell(self, count):
        result = yield ModuleSeller(self.__device, min(count.get('amount', 1), MAX_ITEMS_FOR_OPERATION)).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self.destroyWindow()


class OptDeviceSellDialogWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, itemIntCD, parent=None):
        super(OptDeviceSellDialogWindow, self).__init__(WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=OptDeviceSellDialog(itemIntCD), parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW)

    def _finalize(self):
        self.__blur.fini()
        super(OptDeviceSellDialogWindow, self)._finalize()

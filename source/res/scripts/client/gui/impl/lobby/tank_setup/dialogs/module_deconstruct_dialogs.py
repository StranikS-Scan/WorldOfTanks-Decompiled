# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/dialogs/module_deconstruct_dialogs.py
from adisp import adisp_process
import logging
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.lobby.tank_setup.dialogs.dialog_helpers.balance import initBalance
from gui.impl.lobby.tank_setup.dialogs.dialog_helpers.model_formatters import initItemInfo
from helpers import dependency
from gui.impl.gen import R
from skeletons.gui.shared import IItemsCache
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import SystemMessages
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shared.gui_items.processors.module import ModuleDeconstruct
from gui.impl.gen.view_models.views.lobby.tank_setup.dialogs.confirm_actions_with_equipment_dialog_model import ConfirmActionsWithEquipmentDialogModel, DialogType
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import MAX_ITEMS_FOR_OPERATION
_logger = logging.getLogger(__name__)

class DeconstructDialogView(ViewImpl):
    __slots__ = ('__device', '__currency')
    LAYOUT_ID = R.views.lobby.tanksetup.dialogs.ConfirmActionsWithEquipmentDialog()
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemIntCD):
        settings = ViewSettings(layoutID=self.LAYOUT_ID, model=ConfirmActionsWithEquipmentDialogModel())
        super(DeconstructDialogView, self).__init__(settings)
        self.__device = self.__itemsCache.items.getItemByCD(itemIntCD)
        self.__currency = self.__device.sellPrices.itemPrice.price.getCurrency(byWeight=True)

    @property
    def viewModel(self):
        return super(DeconstructDialogView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DeconstructDialogView, self)._onLoading(*args, **kwargs)
        initItemInfo(self.viewModel, self.__device, self.__currency)
        self.viewModel.setDialogType(DialogType.DECONSTRUCTFROMSTORAGE)
        initBalance(self.viewModel.getBalance(), (self.__currency,), self.__itemsCache)
        self.viewModel.setAlertText(backport.text(R.strings.tank_setup.dialogs.confirmActionsWithEquipmentDialog.warning()))
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(DeconstructDialogView, self)._finalize()

    def __addListeners(self):
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self.viewModel.onDeconstruct += self.__onDeconstruct
        self.viewModel.onClose += self.__onClose

    def __removeListeners(self):
        self.viewModel.onDeconstruct -= self.__onDeconstruct
        self.viewModel.onClose -= self.__onClose
        g_clientUpdateManager.removeObjectCallbacks(self)

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
        initBalance(self.viewModel.getBalance(), (self.__currency,), self.__itemsCache)


class DeconstructDialogWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, itemIntCD, parent=None):
        super(DeconstructDialogWindow, self).__init__(WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=DeconstructDialogView(itemIntCD), parent=parent)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.WINDOW)

    def _finalize(self):
        self.__blur.fini()
        super(DeconstructDialogWindow, self)._finalize()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/storage_cm_handlers.py
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import showStorageModuleInfo
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class _StorageOptions(object):
    INFORMATION = 'information'
    SELL = 'sell'
    SALE_OPTION = 'saleOption'


class StorageForSellItemCMHandler(AbstractContextMenuHandler, EventSystemEntity):
    itemsCache = dependency.descriptor(IItemsCache)
    service = dependency.descriptor(ICustomizationService)

    def __init__(self, cmProxy, ctx=None):
        self._intCD = 0
        self._selected = False
        super(StorageForSellItemCMHandler, self).__init__(cmProxy, ctx, {_StorageOptions.INFORMATION: 'showInformation',
         _StorageOptions.SELL: 'sellItem',
         _StorageOptions.SALE_OPTION: 'changeSaleOption'})

    def showInformation(self):
        showStorageModuleInfo(self._intCD)

    @process
    def sellItem(self):
        yield DialogsInterface.showDialog(SellModuleMeta(int(self._intCD)))

    def changeSaleOption(self):
        self.fireEvent(events.StorageEvent(events.StorageEvent.SELECT_MODULE_FOR_SELL, ctx={'intCD': self._intCD}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _generateOptions(self, ctx=None):
        if self._selected:
            label = MENU.cst_item_ctx_menu('prohibitSale')
        else:
            label = MENU.cst_item_ctx_menu('allowSale')
        return [self._makeItem(_StorageOptions.INFORMATION, MENU.cst_item_ctx_menu(_StorageOptions.INFORMATION)), self._makeItem(_StorageOptions.SELL, MENU.cst_item_ctx_menu(_StorageOptions.SELL)), self._makeItem(_StorageOptions.SALE_OPTION, label)]

    def _initFlashValues(self, ctx):
        self._intCD = int(ctx.id)
        self._selected = ctx.selected

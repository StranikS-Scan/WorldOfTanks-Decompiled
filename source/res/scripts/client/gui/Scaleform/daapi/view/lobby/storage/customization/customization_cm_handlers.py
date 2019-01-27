# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/customization/customization_cm_handlers.py
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nSellMeta
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import option, CMLabel, ContextMenu
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import customizationAvailableForSell
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import customizationPreview
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class CustomizationCMHandler(ContextMenu, EventSystemEntity):
    _service = dependency.descriptor(ICustomizationService)
    _itemsCache = dependency.descriptor(IItemsCache)
    _sqGen = SequenceIDGenerator()

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        pass

    @option(_sqGen.next(), CMLabel.PREVIEW_CUSTOMIZATION)
    def preview(self):
        customizationPreview(self._id)

    @option(_sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        item = self._itemsCache.items.getItemByCD(self._id)
        yield DialogsInterface.showDialog(ConfirmC11nSellMeta(item.intCD, item.inventoryCount, self.__sellItem))

    def _getOptionCustomData(self, label):
        if label == CMLabel.SELL:
            item = self._itemsCache.items.getItemByCD(self._id)
            return {'enabled': item and customizationAvailableForSell(item)}
        else:
            return {'enabled': False} if label == CMLabel.INFORMATION else None

    def __sellItem(self, itemCD, count):
        item = self._itemsCache.items.getItemByCD(itemCD)
        self._service.sellItem(item, count)

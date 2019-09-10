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
    __service = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __sqGen = SequenceIDGenerator()

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        pass

    @option(__sqGen.next(), CMLabel.PREVIEW_CUSTOMIZATION)
    def preview(self):
        customizationPreview(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        item = self.__itemsCache.items.getItemByCD(self._id)
        yield DialogsInterface.showDialog(ConfirmC11nSellMeta(item.intCD, item.inventoryCount, self.__sellItem))

    def _getOptionCustomData(self, label):
        optionData = super(CustomizationCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.SELL:
            item = self.__itemsCache.items.getItemByCD(self._id)
            optionData.enabled = item is not None and customizationAvailableForSell(item)
        elif label == CMLabel.INFORMATION:
            optionData.enabled = False
        return optionData

    def __sellItem(self, itemCD, count):
        item = self.__itemsCache.items.getItemByCD(itemCD)
        self.__service.sellItem(item, count)

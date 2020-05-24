# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/customization/customization_cm_handlers.py
import math
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.confirm_customization_item_dialog_meta import ConfirmC11nSellMeta
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import option, CMLabel, ContextMenu
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import isCustomizationAvailableForSell, getAvailableForSellCustomizationCount
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import customizationPreview
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared.gui_items import GUI_ITEM_TYPE
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
        customizationPreview(itemCD=self._id, vehicleCD=self._vehicleCD)

    @option(__sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        item = self.__itemsCache.items.getItemByCD(self._id)
        vehicle = self.__itemsCache.items.getItemByCD(self._vehicleCD) if self._vehicleCD is not None else None
        inventoryCount = getAvailableForSellCustomizationCount(item, self._vehicleCD)
        yield DialogsInterface.showDialog(ConfirmC11nSellMeta(item.intCD, inventoryCount, self.__sellItem, vehicle=vehicle))
        return

    def _initFlashValues(self, ctx):
        self._id = int(ctx.id)
        self._vehicleCD = int(ctx.vehicleCD) if not math.isnan(ctx.vehicleCD) else None
        return

    def _getOptionCustomData(self, label):
        optionData = super(CustomizationCMHandler, self)._getOptionCustomData(label)
        item = self.__itemsCache.items.getItemByCD(self._id)
        if label == CMLabel.SELL:
            optionData.enabled = item is not None and isCustomizationAvailableForSell(item, self._vehicleCD)
        elif label == CMLabel.INFORMATION:
            optionData.enabled = False
        elif label == CMLabel.PREVIEW_CUSTOMIZATION:
            optionData.enabled = item is not None and item.itemTypeID == GUI_ITEM_TYPE.STYLE
        return optionData

    def __sellItem(self, itemCD, count, vehicle):
        item = self.__itemsCache.items.getItemByCD(itemCD)
        self.__service.sellItem(item, count, vehicle)

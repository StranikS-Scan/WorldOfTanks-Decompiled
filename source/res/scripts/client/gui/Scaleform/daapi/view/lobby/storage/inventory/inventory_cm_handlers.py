# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/inventory_cm_handlers.py
from adisp import process
from gui import DialogsInterface, ingame_shop as shop
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import ContextMenu, option, CMLabel
from gui.Scaleform.framework.managers.context_menu import CM_BUY_COLOR
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from ids_generators import SequenceIDGenerator
from items import UNDEFINED_ITEM_CD
from skeletons.gui.shared import IItemsCache
_SOURCE = shop.Source.EXTERNAL
_ORIGIN = shop.Origin.STORAGE

class ModulesShellsCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    def _getOptionCustomData(self, label):
        optionData = super(ModulesShellsCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.BUY_MORE:
            optionData.textColor = CM_BUY_COLOR
        return optionData


class ModulesShellsNoSaleCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    def _getOptionCustomData(self, label):
        optionData = super(ModulesShellsNoSaleCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.BUY_MORE:
            optionData.textColor = CM_BUY_COLOR
        return optionData


class EquipmentCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    __itemsCache = dependency.descriptor(IItemsCache)

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    @option(__sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        typeID = self.__itemsCache.items.getItemByCD(self._id).itemTypeID if self._id else UNDEFINED_ITEM_CD
        if typeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            shop.showBuyOptionalDeviceOverlay(self._id, _SOURCE, _ORIGIN)
        elif typeID == GUI_ITEM_TYPE.EQUIPMENT:
            shop.showBuyEquipmentOverlay(self._id, _SOURCE, _ORIGIN)
        else:
            shared_events.showWebShop()

    def _getOptionCustomData(self, label):
        optionData = super(EquipmentCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.BUY_MORE:
            optionData.textColor = CM_BUY_COLOR
        return optionData


class BattleBoostersCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    @option(__sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        shop.showBuyBattleBoosterOverlay(self._id, _SOURCE, _ORIGIN)

    def _getOptionCustomData(self, label):
        optionData = super(BattleBoostersCMHandler, self)._getOptionCustomData(label)
        if label in (CMLabel.INFORMATION, CMLabel.SELL):
            optionData.enabled = False
        elif label == CMLabel.BUY_MORE:
            optionData.textColor = CM_BUY_COLOR
        return optionData

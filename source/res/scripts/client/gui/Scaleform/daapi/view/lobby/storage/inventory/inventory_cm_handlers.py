# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/inventory_cm_handlers.py
from adisp import process
from gui import DialogsInterface, ingame_shop as shop
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import ContextMenu, option, CMLabel, CM_BUY_COLOR
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.shared import IItemsCache
_SOURCE = shop.Source.EXTERNAL
_ORIGIN = shop.Origin.STORAGE

class ModulesShellsCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(_sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    def _getOptionCustomData(self, label):
        return {'textColor': CM_BUY_COLOR} if label == CMLabel.BUY_MORE else None


class EquipmentCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(_sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    @option(_sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        typeID = self._itemsCache.items.getItemByCD(self._id).itemTypeID if self._id else -1
        if typeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            shop.showBuyOptionalDeviceOverlay(self._id, _SOURCE, _ORIGIN)
        elif typeID == GUI_ITEM_TYPE.EQUIPMENT:
            shop.showBuyEquipmentOverlay(self._id, _SOURCE, _ORIGIN)
        else:
            shared_events.showWebShop()

    def _getOptionCustomData(self, label):
        return {'textColor': CM_BUY_COLOR} if label == CMLabel.BUY_MORE else None


class BattleBoostersCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(_sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    @option(_sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        shop.showBuyBattleBoosterOverlay(self._id, _SOURCE, _ORIGIN)

    def _getOptionCustomData(self, label):
        if label in (CMLabel.INFORMATION, CMLabel.SELL):
            return {'enabled': False}
        else:
            return {'textColor': CM_BUY_COLOR} if label == CMLabel.BUY_MORE else None

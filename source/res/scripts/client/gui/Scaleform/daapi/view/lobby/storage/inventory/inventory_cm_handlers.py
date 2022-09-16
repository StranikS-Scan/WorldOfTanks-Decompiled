# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/inventory_cm_handlers.py
from adisp import adisp_process
from gui import DialogsInterface, shop
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import ContextMenu, option, CMLabel
from gui.Scaleform.framework.managers.context_menu import CM_BUY_COLOR
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showBattleBoosterSellDialog
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from ids_generators import SequenceIDGenerator
from items import UNDEFINED_ITEM_CD
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
_SOURCE = shop.Source.EXTERNAL
_ORIGIN = shop.Origin.STORAGE

class ModulesShellsCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @adisp_process
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


class _ArmingCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(_sqGen.next(), CMLabel.SELL)
    @adisp_process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    def buy(self):
        shared_events.showShop()

    def _getHighlightedLabels(self):
        return tuple()

    def _generateOptions(self, ctx=None):
        options = super(_ArmingCMHandler, self)._generateOptions(ctx)
        module = self._itemsCache.items.getItemByCD(int(self._id))
        if module.isHidden:
            return [ item for item in options if item['id'] != CMLabel.BUY_MORE ]
        return options

    def _getOptionCustomData(self, label):
        optionData = super(_ArmingCMHandler, self)._getOptionCustomData(label)
        if label in self._getHighlightedLabels():
            optionData.textColor = CM_BUY_COLOR
        return optionData


class EquipmentCMHandler(_ArmingCMHandler):

    @option(_ArmingCMHandler._sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        typeID = self._itemsCache.items.getItemByCD(self._id).itemTypeID if self._id else UNDEFINED_ITEM_CD
        if typeID == GUI_ITEM_TYPE.EQUIPMENT:
            shop.showBuyEquipmentOverlay(self._id, source=_SOURCE, origin=_ORIGIN, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)
        else:
            super(EquipmentCMHandler, self).buy()

    def _getHighlightedLabels(self):
        return (CMLabel.BUY_MORE,)


class OptionalDeviceCMHandler(_ArmingCMHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @option(_ArmingCMHandler._sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        shop.showBuyOptionalDeviceOverlay(self._id, source=_SOURCE, origin=_ORIGIN, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)

    @option(_ArmingCMHandler._sqGen.next(), CMLabel.UPGRADE)
    def upgrade(self):
        module = self._itemsCache.items.getItemByCD(int(self._id))
        ItemsActionsFactory.doAction(ItemsActionsFactory.UPGRADE_OPT_DEVICE, module, None, None, None)
        return

    def _generateOptions(self, ctx=None):
        options = super(OptionalDeviceCMHandler, self)._generateOptions(ctx)
        module = self._itemsCache.items.getItemByCD(int(self._id))
        if not module.isUpgradable or not self.__lobbyContext.getServerSettings().isTrophyDevicesEnabled():
            options = [ item for item in options if item['id'] != CMLabel.UPGRADE ]
        return options

    def _getHighlightedLabels(self):
        return (CMLabel.BUY_MORE, CMLabel.UPGRADE)


class BattleBoostersCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)

    def _initFlashValues(self, ctx):
        super(BattleBoostersCMHandler, self)._initFlashValues(ctx)
        self._enabled = bool(ctx.enabled)

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    def sell(self):
        showBattleBoosterSellDialog(self._id)

    @option(__sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        shop.showBattleBoosterOverlay(self._id, source=_SOURCE, origin=_ORIGIN, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)

    def _getOptionCustomData(self, label):
        optionData = super(BattleBoostersCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.INFORMATION:
            optionData.enabled = False
        elif label == CMLabel.SELL:
            optionData.enabled = self._enabled
        elif label == CMLabel.BUY_MORE:
            optionData.textColor = CM_BUY_COLOR
        return optionData

    def _isVisible(self, label):
        return not self._itemsCache.items.getItemByCD(self._id).isHidden if label == CMLabel.BUY_MORE else super(BattleBoostersCMHandler, self)._isVisible(label)


class DemountKitsCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showGoodieInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @adisp_process
    def sell(self):
        raise NotImplementedError

    @option(__sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        raise NotImplementedError

    def _getOptionCustomData(self, label):
        optionData = super(DemountKitsCMHandler, self)._getOptionCustomData(label)
        if label in (CMLabel.SELL, CMLabel.BUY_MORE):
            optionData.enabled = False
        return optionData


class RecertificationFormsCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showGoodieInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @adisp_process
    def sell(self):
        raise NotImplementedError

    @option(__sqGen.next(), CMLabel.BUY_MORE)
    def buy(self):
        raise NotImplementedError

    def _getOptionCustomData(self, label):
        optionData = super(RecertificationFormsCMHandler, self)._getOptionCustomData(label)
        if label in (CMLabel.SELL, CMLabel.BUY_MORE):
            optionData.enabled = False
        return optionData

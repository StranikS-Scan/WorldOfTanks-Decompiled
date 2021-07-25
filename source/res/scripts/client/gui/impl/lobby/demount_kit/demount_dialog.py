# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/demount_dialog.py
import typing
from gui.goodies.demount_kit import getDemountKitForOptDevice
from gui.goodies.goodie_items import DemountKit
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.select_option_content import SelectOptionContent, DemountKitOption, MoneyOption
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.lobby.demount_kit.demount_kit_utils import getDemountDialogTitle
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shop import showBuyGoldForEquipment
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.shared.gui_items.artefacts import OptionalDevice
NOTHING = -1
DEMOUNT_KIT = 0
GOLD = 1

class DemountOptionalDeviceDialog(DialogTemplateView):
    __slots__ = ('__item', '__forFitting', 'removalPrice', '__selector', '__moneyOption')
    _wallet = dependency.descriptor(IWalletController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemCD, forFitting=False):
        super(DemountOptionalDeviceDialog, self).__init__()
        self.__item = self._itemsCache.items.getItemByCD(itemCD)
        self.removalPrice = self.__item.getRemovalPrice(self._itemsCache.items)
        self.__forFitting = forFitting
        self.__selector = None
        self.__moneyOption = None
        return

    def _onLoading(self, *args, **kwargs):
        self.setSubView(Placeholder.TOP_RIGHT, MoneyBalance())
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(getDemountDialogTitle(self.__item, self.__forFitting)))
        self.__selector = content = SelectOptionContent()
        content.addOption(DemountKitOption(self.__item.intCD))
        self.__moneyOption = MoneyOption(self.removalPrice)
        content.addOption(self.__moneyOption)
        content.setMessage(backport.text(R.strings.demount_kit.equipmentDemount.confirmation.description()))
        dk, _ = getDemountKitForOptDevice(self.__item)
        goldEnough = self._isGoldEnough()
        if dk.inventoryCount > 0:
            self._select(DEMOUNT_KIT)
        elif goldEnough:
            self._select(GOLD)
        else:
            self._select(NOTHING)
        self.setSubView(Placeholder.CONTENT, self.__selector)
        self.addButton(ConfirmButton(R.strings.menu.moduleFits.removeName()))
        self.addButton(CancelButton())
        self._itemsCache.onSyncCompleted += self._inventorySyncHandler
        super(DemountOptionalDeviceDialog, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self._itemsCache.onSyncCompleted -= self._inventorySyncHandler
        super(DemountOptionalDeviceDialog, self)._finalize()

    def _inventorySyncHandler(self, *_):
        dk, _ = getDemountKitForOptDevice(self.__item)
        if not dk.enabled:
            self._closeClickHandler()
            return
        if self.__moneyOption:
            self.__moneyOption.updatePrice(self.removalPrice)
        self.removalPrice = self.__item.getRemovalPrice(self._itemsCache.items)
        gold = self._itemsCache.items.stats.gold
        goldEnough = self._isGoldEnough(gold)
        dkCount = dk.inventoryCount
        if self._isSelected(GOLD) and not goldEnough:
            if dkCount > 0:
                self._select(DEMOUNT_KIT)
            else:
                self._select(NOTHING)
        elif self._isSelected(DEMOUNT_KIT) and dkCount <= 0:
            if goldEnough:
                self._select(GOLD)
            else:
                self._select(NOTHING)
        elif self._isSelected(NOTHING):
            if dkCount > 0:
                self._select(DEMOUNT_KIT)
            elif goldEnough:
                self._select(GOLD)

    def _isSelected(self, index):
        return self.__selector.selectedIndex == index

    def _select(self, index):
        self.__selector.selectedIndex = index

    def _getAdditionalData(self):
        dk, _ = getDemountKitForOptDevice(self.__item)
        return {'useDemountKit': self._isSelected(DEMOUNT_KIT),
         'openSingleDemountWindow': dk and not dk.enabled}

    def _isGoldEnough(self, gold=None):
        _gold = gold or self._itemsCache.items.stats.gold
        return _gold >= self.removalPrice.price.gold

    def _setResult(self, result):
        goldEnough = self._isGoldEnough()
        dk, _ = getDemountKitForOptDevice(self.__item)
        dkEnough = dk.inventoryCount > 0
        if result == DialogButtons.SUBMIT:
            if not goldEnough and not dkEnough:
                showBuyGoldForEquipment(self.removalPrice.price.gold)
                result = DialogButtons.CANCEL
        super(DemountOptionalDeviceDialog, self)._setResult(result)

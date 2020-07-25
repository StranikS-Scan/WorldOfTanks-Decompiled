# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/buy_sell_item_base_dialog.py
from abc import abstractproperty
from typing import TYPE_CHECKING
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel as FrmtModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
if TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.common.buy_sell_items_dialog_model import BuySellItemsDialogModel

class DialogBuySellItemBaseView(FullScreenDialogView):

    def __init__(self, settings, typeCompDescr):
        super(DialogBuySellItemBaseView, self).__init__(settings)
        self._itemCD = typeCompDescr
        self._item = self._itemsCache.items.getItemByCD(self._itemCD)

    @abstractproperty
    def viewModel(self):
        pass

    @abstractproperty
    def isBuying(self):
        pass

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                itemPrice = self._getItemPrice()
                args = (ACTION_TOOLTIPS_TYPE.ITEM,
                 self._item.intCD,
                 list(itemPrice.price),
                 list(itemPrice.defPrice),
                 self.isBuying)
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
                window.load()
                return window
        return super(DialogBuySellItemBaseView, self).createToolTip(event)

    def _setBaseParams(self, model):
        super(DialogBuySellItemBaseView, self)._setBaseParams(model)
        self._setItemPrices(model)
        model.setBackgroundImg(R.images.gui.maps.shop.artefacts.c_180x135.dyn(self._item.descriptor.icon[0])())

    def _getItemPrice(self):
        if self.isBuying:
            price = self._item.getBuyPrice(preferred=False)
        else:
            price = self._item.getSellPrice(preferred=False)
        return price

    def _setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FrmtModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

        arrModel.invalidate()

    def _setItemPrices(self, model):
        itemPrice = self._getItemPrice()
        currency = itemPrice.getCurrency(byWeight=True)
        model.setCurrencyType(currency)
        model.setItemPrice(itemPrice.price.getSignValue(currency))
        count = model.getItemCount()
        model.setItemTotalPrice(count * itemPrice.price.getSignValue(currency))
        model.setIsAlert(itemPrice.isActionPrice())

    def _finalize(self):
        super(DialogBuySellItemBaseView, self)._finalize()
        self._item = None
        return

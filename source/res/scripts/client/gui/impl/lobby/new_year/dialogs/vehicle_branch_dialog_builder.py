# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/vehicle_branch_dialog_builder.py
import typing
from gui.impl import backport
from gui.impl.dialogs.dialog_template_button import CancelButton, CheckMoneyButton
from gui.impl.dialogs.gf_builders import BaseDialogBuilder
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.gui_item_economics import ItemPrice
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from new_year.vehicle_branch_helpers import getVehicleChangePrice
if typing.TYPE_CHECKING:
    from gui.impl.dialogs.dialog_template import DialogTemplateView

class VehicleBranchDialogBuilder(BaseDialogBuilder):
    __slots__ = ('__veh', '__slot')
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, invID, slotID):
        self.__veh = self._itemsCache.items.getVehicle(invID)
        self.__slot = self._nyController.getVehicleBranch().getVehicleSlots()[slotID]
        super(VehicleBranchDialogBuilder, self).__init__()

    def _extendTemplate(self, template):
        super(VehicleBranchDialogBuilder, self)._extendTemplate(template)
        template.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        self.__setTitle(template)
        vehicleChangePrice = getVehicleChangePrice()
        template.setSubView(DefaultDialogPlaceHolders.FOOTER, SinglePriceFooter(R.strings.ny.dialogs.setVehicleBranch.price(), ItemPrice(price=vehicleChangePrice, defPrice=vehicleChangePrice), CurrencySize.BIG))
        if self.__slot.getVehicle():
            label = R.strings.ny.dialogs.setVehicleBranch.btnApply()
        else:
            label = R.strings.ny.dialogs.setVehicleBranch.btnSelect()
        template.addButton(CheckMoneyButton(vehicleChangePrice, label, DialogButtons.PURCHASE, ButtonType.MAIN))
        template.addButton(CancelButton())

    def __setTitle(self, template):
        if self.__slot.getVehicle():
            title = backport.text(R.strings.ny.dialogs.setVehicleBranch.title(), oldVehicle=self.__slot.getVehicle().userName, newVehicle=self.__veh.userName)
        else:
            title = backport.text(R.strings.ny.dialogs.setVehicleBranch.addVehicleTitle(), vehicle=self.__veh.userName)
        template.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(title))

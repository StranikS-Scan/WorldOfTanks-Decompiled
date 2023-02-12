# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/dialogs/rentConfirm.py
from time import time
from battle_royale.gui.impl.dialogs.sub_views.top_right.br_money_balance import BRMoneyBalance
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from helpers import dependency
from gui.impl.gen.view_models.views.battle_royale.equipment_panel_cmp_rent_states import EquipmentPanelCmpRentStates
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController, IBattleRoyaleController
from skeletons.gui.shared import IItemsCache
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.sub_views.content.text_warning_content import TextWithWarning
from gui.shared.gui_items.Vehicle import getUserName
from items import vehicles
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from battle_royale.gui.constants import BR_COIN
from battle_royale.gui.impl.dialogs.sub_views.footer.br_single_price_footer import BRSinglePriceFooter

class BrMoney(Money):

    def __init__(self, brcoin=None, *args, **kwargs):
        super(BrMoney, self).__init__(*args, **kwargs)
        if brcoin is not None:
            self._values[BR_COIN] = brcoin
        return

    def getCurrency(self, byWeight=True):
        res = super(BrMoney, self).getCurrency(byWeight)
        return BR_COIN if self._values.get(res) is None else res


class RentConfirm(DialogTemplateView):
    __slots__ = ('__vehicleCD',)
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, vehicleCD, layoutID=None, uniqueID=None):
        super(RentConfirm, self).__init__(layoutID, uniqueID)
        self.__vehicleCD = vehicleCD

    @property
    def itemPrice(self):
        return self.__item.getRemovalPrice(self._itemsCache.items)

    def _onLoading(self, *args, **kwargs):
        self.setSubView(Placeholder.TOP_RIGHT, BRMoneyBalance())
        vehicle = self._itemsCache.items.getItemByCD(self.__vehicleCD)
        if vehicle.name:
            vehName = vehicle.name.split(':')[1]
            vehName = vehName.replace('-', '_')
            resID = R.images.gui.maps.icons.battleRoyale.rentVehicles.dyn(vehName)()
            if resID > 0:
                _list = [R.images.gui.maps.icons.battleRoyale.rentVehicles.background()]
                self.setSubView(Placeholder.ICON, IconSet(resID, backgroundResIDList=_list))
        titleMsg = ''
        descriptionMsg = ''
        buttonConfirmMsg = ''
        rentState = self.__rentVehiclesController.getRentState(self.__vehicleCD)
        resID = R.strings.dialogs.battleRoyale.confirmRent
        vehicleName = getUserName(vehicles.getVehicleType(self.__vehicleCD))
        warningMsg = None
        if rentState == EquipmentPanelCmpRentStates.STATE_TEST_DRIVE_AVAILABLE:
            rentTime = int(self.__rentVehiclesController.getNextTestDriveDaysTotal(self.__vehicleCD))
            buttonConfirmMsg = resID.testDrive.Button()
            titleMsg = backport.text(resID.testDrive.Title(), vehicle=vehicleName, days=rentTime)
            nextRentDays = int(self.__rentVehiclesController.getNextRentDaysTotal(self.__vehicleCD))
            descriptionMsg = backport.text(resID.testDrive.Description(), days=nextRentDays)
        elif rentState == EquipmentPanelCmpRentStates.STATE_RENT_AVAILABLE:
            rentTime = self.__rentVehiclesController.getNextRentDaysTotal(self.__vehicleCD)
            buttonConfirmMsg = resID.rent.Button()
            titleMsg = backport.text(resID.rent.Title(), vehicle=vehicleName, days=rentTime)
            descriptionMsg = backport.text(resID.rent.Description())
            if self._battleRoyaleController.isActive():
                timeLeft = (self._battleRoyaleController.getEndTime() - time()) / 86400
                if timeLeft <= rentTime:
                    warningMsg = backport.text(resID.eventEndsSoon(), days=int(timeLeft))
            price = self.__rentVehiclesController.getRentPrice(self.__vehicleCD)
            currency = price.getCurrency()
            res = {currency: price.get(currency)}
            itemPrice = ItemPrice(price=BrMoney(**res), defPrice=BrMoney(**res))
            self.setSubView(Placeholder.FOOTER, BRSinglePriceFooter(resID.rentPrice, itemPrice, CurrencySize.BIG))
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(titleMsg))
        self.setSubView(Placeholder.CONTENT, TextWithWarning(descriptionMsg, warningMsg))
        self.addButton(ConfirmButton(label=buttonConfirmMsg, buttonType=ButtonType.PRIMARY))
        self.addButton(CancelButton())
        super(RentConfirm, self)._onLoading(*args, **kwargs)
        return

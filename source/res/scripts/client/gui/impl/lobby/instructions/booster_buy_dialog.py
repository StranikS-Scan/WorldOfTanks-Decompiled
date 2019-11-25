# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/instructions/booster_buy_dialog.py
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.instructions.booster_buy_model import BoosterBuyModel
from gui.impl.lobby.common.buy_sell_item_base_dialog import DialogBuySellItemBaseView
from gui.impl.lobby.instructions import getBattleBoosterItemType
from gui.shared.gui_items.processors.module import ModuleBuyer
from gui.shared.gui_items.processors.vehicle import VehicleAutoBattleBoosterEquipProcessor
from adisp import process
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory

class BoosterBuyWindowView(DialogBuySellItemBaseView):

    def __init__(self, typeCompDescr, install, layoutID=R.views.lobby.instructions.BuyWindow()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.TOP_WINDOW_VIEW
        settings.model = BoosterBuyModel()
        super(BoosterBuyWindowView, self).__init__(settings, typeCompDescr)
        self.__install = install

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isBuying(self):
        return True

    def _onUpdateStats(self, *args, **kwargs):
        super(BoosterBuyWindowView, self)._onUpdateStats(*args, **kwargs)
        shortage = self._stats.money.getShortage(self._getItemPrice().price)
        maxCount = self.__calculateMaxCount()
        with self.viewModel.transaction() as model:
            model.setItemMaxCount(maxCount)
            model.setIsAcceptDisabled(bool(shortage))
            model.setItemCount(min(model.getItemCount(), maxCount))

    def _setBaseParams(self, model):
        itemPrice = self._getItemPrice()
        currency = itemPrice.getCurrency(byWeight=True)
        vehicle = g_currentVehicle.item
        self._setTitleArgs(model.getTitleArgs(), (('name', R.strings.artefacts.dyn(self._item.name).name()),))
        model.setTitleBody(R.strings.menu.boosterBuyWindow.title())
        model.setItemMaxCount(self.__calculateMaxCount())
        oldPrice = itemPrice.defPrice.getSignValue(currency)
        newPrice = itemPrice.price.getSignValue(currency)
        model.setIsDiscount(itemPrice.isActionPrice())
        model.setDiscountValue(int(100.0 * newPrice / oldPrice) - 100)
        shortage = self._stats.money.getShortage(itemPrice.price)
        model.setIsAcceptDisabled(bool(shortage))
        model.setItemType(getBattleBoosterItemType(self._item))
        model.setIsRearm(vehicle.isAutoBattleBoosterEquip() if vehicle is not None else False)
        if vehicle is not None and not self._item.isAffectsOnVehicle(vehicle):
            model.setUpperDescription(R.strings.tooltips.battleBooster.buy.useless.upper_description())
            model.setLowerDescription(R.strings.tooltips.battleBooster.buy.useless.lower_description())
        super(BoosterBuyWindowView, self)._setBaseParams(model)
        return

    def _initialize(self):
        super(BoosterBuyWindowView, self)._initialize()
        self.viewModel.onSetIsRearm += self._onSetIsRearm

    def _finalize(self):
        self.viewModel.onSetIsRearm -= self._onSetIsRearm
        super(BoosterBuyWindowView, self)._finalize()

    @process
    def _onSetIsRearm(self):
        vehicle = g_currentVehicle.item
        isRearm = self.viewModel.getIsRearm()
        if vehicle is not None:
            yield VehicleAutoBattleBoosterEquipProcessor(vehicle, isRearm).request()
        return

    @process
    def _onAcceptClicked(self):
        count = self.viewModel.getItemCount()
        if self.__install and g_currentVehicle.isPresent():
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM_VEHICLE_LAYOUT, g_currentVehicle.item, None, None, self._item, count, skipConfirm=True)
        else:
            currency = self._item.getBuyPrice(preferred=False).getCurrency(byWeight=True)
            result = yield ModuleBuyer(self._item, count, currency).request()
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        super(BoosterBuyWindowView, self)._onAcceptClicked()
        return

    def __calculateMaxCount(self):
        itemPrice = self._getItemPrice()
        currency = itemPrice.getCurrency(byWeight=True)
        return int(float(self._stats.money.getSignValue(currency)) / itemPrice.price.getSignValue(currency)) or 1

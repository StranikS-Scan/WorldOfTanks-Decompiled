# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/instructions/booster_buy_dialog.py
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.instructions.booster_buy_model import BoosterBuyModel
from gui.impl.lobby.common.buy_sell_item_base_dialog import DialogBuySellItemBaseView
from gui.shared.gui_items.processors.module import ModuleBuyer
from gui.shared.gui_items.processors.vehicle import VehicleAutoBattleBoosterEquipProcessor
from adisp import adisp_process
from helpers.func_utils import oncePerPeriod

class BoosterBuyWindowView(DialogBuySellItemBaseView):

    def __init__(self, typeCompDescr, layoutID=R.views.lobby.instructions.BuyWindow()):
        settings = ViewSettings(layoutID)
        settings.model = BoosterBuyModel()
        super(BoosterBuyWindowView, self).__init__(settings, typeCompDescr)

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def isBuying(self):
        return True

    def _onInventoryResync(self, *args, **kwargs):
        super(BoosterBuyWindowView, self)._onInventoryResync(*args, **kwargs)
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
        self._setTitleArgs(model.getTitleArgs(), (('name', self._item.userName),))
        model.setTitleBody(R.strings.menu.boosterBuyWindow.title())
        model.setItemMaxCount(self.__calculateMaxCount())
        oldPrice = itemPrice.defPrice.getSignValue(currency)
        newPrice = itemPrice.price.getSignValue(currency)
        model.setIsDiscount(itemPrice.isActionPrice())
        model.setDiscountValue(int(100.0 * newPrice / oldPrice) - 100)
        shortage = self._stats.money.getShortage(itemPrice.price)
        model.setIsAcceptDisabled(bool(shortage))
        model.setSpecialType(self._item.getOverlayType())
        model.setIsRearm(vehicle.isAutoBattleBoosterEquip() if vehicle is not None else False)
        if vehicle is not None and not self._item.isAffectsOnVehicle(vehicle):
            model.setUpperDescription(R.strings.tooltips.battleBooster.useless.header())
            root = R.strings.tooltips.crewSkillBattleBooster if self._item.isCrewBooster() else R.strings.tooltips.battleBooster
            model.setLowerDescription(root.useless.body())
        super(BoosterBuyWindowView, self)._setBaseParams(model)
        return

    def _initialize(self):
        super(BoosterBuyWindowView, self)._initialize()
        self.viewModel.onSetIsRearm += self._onSetIsRearm

    def _finalize(self):
        self.viewModel.onSetIsRearm -= self._onSetIsRearm
        super(BoosterBuyWindowView, self)._finalize()

    def _onSetIsRearm(self, args=None):
        if args is not None:
            self.viewModel.setIsRearm(args.get('isRearm'))
        return

    @oncePerPeriod(1)
    @adisp_process
    def _onAcceptClicked(self):
        count = self.viewModel.getItemCount()
        isRearm = self.viewModel.getIsRearm()
        vehicle = g_currentVehicle.item
        if vehicle is not None:
            yield VehicleAutoBattleBoosterEquipProcessor(vehicle, isRearm).request()
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

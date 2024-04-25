# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/proxy_currency_panel.py
from battle_royale.gui.impl.lobby.tooltips.br_coin_tooltip_view import BrCoinTooltipView
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getSteelHunterProductsUrl
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from skeletons.gui.game_control import IBattleRoyaleRentVehiclesController
from gui.impl.gen.view_models.views.battle_royale.proxy_currency_cmp_view_model import ProxyCurrencyCmpViewModel

class ProxyCurrencyComponentInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return ProxyCurrencyView()


class ProxyCurrencyView(ViewImpl):
    __slots__ = ()
    __rentVehiclesController = dependency.descriptor(IBattleRoyaleRentVehiclesController)

    def __init__(self):
        settings = ViewSettings(R.views.battle_royale.lobby.views.ProxyCurrencyView())
        settings.flags = ViewFlags.VIEW
        settings.model = ProxyCurrencyCmpViewModel()
        super(ProxyCurrencyView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ProxyCurrencyView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BrCoinTooltipView() if contentID == R.views.battle_royale.lobby.tooltips.BrCoinTooltipView() else None

    def _initialize(self):
        super(ProxyCurrencyView, self)._initialize()
        self.__rentVehiclesController.onBalanceUpdated += self.__onBalanceUpdated
        self.viewModel.onGotoShopBtnClicked += self.__onGotoShopBtnClicked
        self.__updateModel()

    def _finalize(self):
        self.__rentVehiclesController.onBalanceUpdated -= self.__onBalanceUpdated
        self.viewModel.onGotoShopBtnClicked -= self.__onGotoShopBtnClicked
        super(ProxyCurrencyView, self)._finalize()

    def __onBalanceUpdated(self):
        self.__updateModel()

    def __onGotoShopBtnClicked(self):
        showShop(getSteelHunterProductsUrl())

    def __updateModel(self):
        brCoin = self.__rentVehiclesController.getBRCoinBalance(0)
        with self.viewModel.transaction() as model:
            model.setBalance(brCoin)

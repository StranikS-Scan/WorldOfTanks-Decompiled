# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tech_parameters_cmp.py
from battle_royale.gui.impl.lobby.tooltips.shop_tooltip_view import ShopTooltipView
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.common.battle_royale import br_helpers
from gui.Scaleform.daapi.view.meta.BattleRoyaleTechParametersComponent import BattleRoyaleTechParametersComponent
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.doc_loaders.battle_royale_settings_loader import getVehicleProperties
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle_royale.tech_parameters_cmp_view_model import TechParametersCmpViewModel
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showShop
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getSteelHunterProductsUrl
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class TechParametersComponent(BattleRoyaleTechParametersComponent, InjectComponentAdaptor):

    def _makeInjectView(self):
        return TechParametersView(R.views.lobby.battle_royale.TechParametersVIew(), self.__updateHeight)

    def __updateHeight(self, value):
        self.as_updateHeightS(value)


class TechParametersView(ViewImpl):
    __slots__ = ('updateHeight',)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, viewKey, updateHeight, viewModelClazz=TechParametersCmpViewModel):
        self.updateHeight = updateHeight
        settings = ViewSettings(viewKey)
        settings.flags = ViewFlags.VIEW
        settings.model = viewModelClazz()
        super(TechParametersView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TechParametersView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return ShopTooltipView() if contentID == R.views.battle_royale.lobby.tooltips.ShopTooltipView() else super(TechParametersView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(TechParametersView, self)._onLoading(args, kwargs)
        self.__updateModel()

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onCurrentVehicleChanged),
         (self.viewModel.onClick, self.__onClick),
         (self.viewModel.onResized, self.__onResized),
         (self.viewModel.onOpenShop, self.__onGotoShopBtnClicked),
         (self.__battleRoyaleController.onBalanceUpdated, self.__updateModel))

    def __onClick(self):
        event_dispatcher.showHangarVehicleConfigurator()

    def __onResized(self, value):
        self.updateHeight(value['height'])

    def __onCurrentVehicleChanged(self):
        self.__updateModel()

    def __onGotoShopBtnClicked(self):
        showShop(getSteelHunterProductsUrl())

    def __updateModel(self):
        vehicle = g_currentVehicle.item
        if br_helpers.isIncorrectVehicle(vehicle):
            return
        stpCoin = self.__battleRoyaleController.getSTPCoinBalance(0)
        nationName = vehicle.nationName
        params = getVehicleProperties(nationName)
        with self.viewModel.transaction() as tx:
            tx.setSpotting(params.spotting)
            tx.setDifficulty(params.difficulty)
            tx.setSurvivability(params.survivability)
            tx.setMobility(params.mobility)
            tx.setDamage(params.damage)
            tx.setBalance(stpCoin)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/info/bottom_panel_style_buying.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info import dyn_currencies_utils as dyn_utils
from gui.Scaleform.daapi.view.lobby.vehicle_preview.info.style_buying import StyleBuyingProcessor
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelStyleBuyingMeta import VehiclePreviewBottomPanelStyleBuyingMeta
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_preview.buying_panel.style_buying_panel_model import StyleBuyingPanelModel, StyleBuyingStatus
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from gui.shared.gui_items.customization.c11n_items import Style

class VehiclePreviewBottomPanelStyleBuying(VehiclePreviewBottomPanelStyleBuyingMeta):

    def __init__(self):
        super(VehiclePreviewBottomPanelStyleBuying, self).__init__()
        self.__view = None
        return

    def setStyleInfo(self, style, price, level):
        self.__view.setStyleInfo(style, price, level)

    def setBuyParams(self, buyParams):
        self.__view.setBuyParams(buyParams)

    def _makeInjectView(self):
        self.__view = _StyleBuyingPanelView()
        return self.__view


class _StyleBuyingPanelView(ViewImpl):
    __slots__ = ('__ordPrice', '__dynPrice', '__level', '__buyingProcessor')
    __battlePass = dependency.descriptor(IBattlePassController)
    __customizationService = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.vehicle_preview.buying_panel.StyleBuyingPanel())
        settings.flags = ViewFlags.VIEW
        settings.model = StyleBuyingPanelModel()
        self.__ordPrice = {}
        self.__dynPrice = {}
        self.__level = 0
        self.__buyingProcessor = StyleBuyingProcessor()
        super(_StyleBuyingPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(_StyleBuyingPanelView, self).getViewModel()

    def setStyleInfo(self, style, price, level):
        self.__buyingProcessor.setStyle(style)
        self.__ordPrice, self.__dynPrice = dyn_utils.separatePrice(price)
        self.__level = level

    def setBuyParams(self, buyParams):
        self.__buyingProcessor.setBuyParams(buyParams)

    def _getCallbacks(self):
        return (('stats.{}'.format(c), self.__updateVMData) for c in Currency.ALL)

    def _getEvents(self):
        return ((g_currentPreviewVehicle.onChangeStarted, self.__onVehicleChangeStarted), (g_currentPreviewVehicle.onChanged, self.__onVehicleChanged), (self.viewModel.onBuy, self.__onBuy))

    def _onLoaded(self, *args, **kwargs):
        self.__updateVMData()
        self.__applyStyle()

    def __onVehicleChangeStarted(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.unsubscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleChanged(self):
        entity = self.__hangarSpace.getVehicleEntity()
        if entity and entity.appearance:
            entity.appearance.loadState.subscribe(self.__onVehicleLoadFinished, self.__onVehicleLoadStarted)

    def __onVehicleLoadStarted(self):
        pass

    def __onVehicleLoadFinished(self):
        if self.__level is not None:
            self.__applyStyle()
        return

    def __updateVMData(self, *_):
        currency, price, userCurrency, level, status = self.__prepareVMData()
        with self.getViewModel().transaction() as tx:
            tx.setCurrency(currency)
            tx.setPrice(price)
            tx.setUserCurrency(userCurrency)
            tx.setLevel(level)
            tx.setStatus(status)

    def __prepareVMData(self):
        money = dyn_utils.getMoney(self.__ordPrice, self.__dynPrice)
        currency = money.getCurrency()
        price = money.get(currency, 0)
        userCurrency = dyn_utils.getUserMoney(currency)
        mayObtain = self.__buyingProcessor.mayObtain(money)
        status = StyleBuyingStatus.BPNOTPASSED if not self.__battlePass.isCompleted() else (StyleBuyingStatus.AVAILABLE if mayObtain else StyleBuyingStatus.NOTENOUGHMONEY)
        return (currency,
         int(price),
         userCurrency,
         self.__level or 0,
         status)

    def __applyStyle(self):
        if self.__level:
            res = self.__customizationService.changeStyleProgressionLevelPreview(self.__level)
            if res != self.__level:
                self.__onVehicleChanged()

    def __onBuy(self, *_):
        money = dyn_utils.getMoney(self.__ordPrice, self.__dynPrice)
        self.__buyingProcessor.buy(money)

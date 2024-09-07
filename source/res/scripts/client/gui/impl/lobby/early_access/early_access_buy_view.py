# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_buy_view.py
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer, ViewModel
from gui.Scaleform.daapi.view.lobby.techtree.sound_constants import TECHTREE_SOUND_SPACE
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.early_access.tooltips.early_access_compensation_tooltip import EarlyAccessCompensationTooltip
from gui.impl.lobby.early_access.early_access_vehicle_view import EarlyAccessVehicleView
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.early_access_buy_view_model import EarlyAccessBuyViewModel, BuyResult
from gui.impl.gen.view_models.views.lobby.early_access.early_access_vehicle_model import EarlyAccessVehicleModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from gui.impl.lobby.early_access.early_access_window_events import showBuyGoldForEarlyAccess, showEarlyAccessInfoPage
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController
from skeletons.gui.shared import IItemsCache
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.gui_items.items_actions import factory
from gui.impl.lobby.early_access.shared.actions import BUY_EARLY_ACCESS_TOKENS

class EarlyAccessBuyView(ViewImpl):
    __slots__ = ('__backCallback',)
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = TECHTREE_SOUND_SPACE

    def __init__(self, layoutID, backCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = EarlyAccessBuyViewModel()
        super(EarlyAccessBuyView, self).__init__(settings)
        self.__backCallback = backCallback

    @property
    def viewModel(self):
        return super(EarlyAccessBuyView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(EarlyAccessBuyView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessCompensationTooltip():
            return EarlyAccessCompensationTooltip()
        return ViewImpl(ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessTokensStepperTooltip(), model=ViewModel())) if contentID == R.views.lobby.early_access.tooltips.EarlyAccessTokensStepperTooltip() else super(EarlyAccessBuyView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        vehicleCD = event.getArgument('vehicleCD')
        data = createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE, specialArgs=[vehicleCD])
        return data

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessBuyView, self)._onLoading(*args, **kwargs)
        g_techTreeDP.load()
        self.__updateData()

    def _getEvents(self):
        return ((self.__earlyAccessCtrl.onUpdated, self.__updateData),
         (self.__earlyAccessCtrl.onBalanceUpdated, self.__updateData),
         (self.viewModel.onBuyTokens, self.__onBuyTokens),
         (self.viewModel.onBackToPrevScreen, self.__onBackToPrevScreen),
         (self.viewModel.onAboutEvent, showEarlyAccessInfoPage))

    def _getCallbacks(self):
        return (('stats', self.__onStatsUpdated),)

    def __onStatsUpdated(self, _):
        goldBalance = self.__itemsCache.items.stats.money
        with self.getViewModel().transaction() as model:
            model.setGoldBalance(goldBalance.gold)

    def __updateData(self):
        ctrl = self.__earlyAccessCtrl
        state = ctrl.getState()
        startProgressionTime, endProgressionTime = ctrl.getProgressionTimes()
        _, endSeasonTime = ctrl.getSeasonInterval()
        totalTokensCount = ctrl.getTotalVehiclesPrice()
        receivedTokensCount = ctrl.getReceivedTokensCount()
        currentTokensBalance = ctrl.getTokensBalance()
        priceInGold = ctrl.getTokenCost()
        goldBalance = self.__itemsCache.items.stats.money
        with self.getViewModel().transaction() as model:
            model.setState(state.value)
            model.setFromTimestamp(startProgressionTime)
            model.setToTimestamp(endProgressionTime if state == State.ACTIVE else endSeasonTime)
            model.setGoldBalance(goldBalance.gold)
            model.setRecievedTokensCount(receivedTokensCount)
            model.setCurrentTokensBalance(currentTokensBalance)
            model.setTotalTokensCount(totalTokensCount)
            if priceInGold.gold is not None:
                model.setTokenPriceInGold(priceInGold.gold)
            self.__fillVehicles(model)
        return

    def __fillVehicles(self, model):
        vehicles = (self.__itemsCache.items.getItemByCD(cd) for cd in self.__earlyAccessCtrl.getAffectedVehicles())
        vehicles = sorted(vehicles, key=lambda vehicle: vehicle.level)
        vehicleModelArray = model.getVehicles()
        vehicleModelArray.clear()
        for veh in vehicles:
            vModel = EarlyAccessVehicleModel()
            fillVehicleModel(vModel, veh)
            isNext2Unlock, _ = g_techTreeDP.isNext2Unlock(veh.compactDescr, unlocked=self.__itemsCache.items.stats.unlocks, xps=self.__itemsCache.items.stats.vehiclesXPs)
            state = EarlyAccessVehicleView.getVehicleState(veh, isNext2Unlock)
            vModel.setState(state)
            vModel.setPrice(self.__earlyAccessCtrl.getVehiclePrice(veh.compactDescr))
            vModel.setIsPostProgression(not self.__earlyAccessCtrl.isPostprogressionBlockedByQuestFinisher() and veh.compactDescr in self.__earlyAccessCtrl.getPostProgressionVehicles())
            vehicleModelArray.addViewModel(vModel)

        vehicleModelArray.invalidate()

    @adisp_process
    def __onBuyTokens(self, event):
        buyTokensAmount = int(event.get(EarlyAccessBuyViewModel.ARG_BUY_TOKENS_AMOUNT, 0))
        priceInGold = self.__earlyAccessCtrl.getTokenCost() * buyTokensAmount
        playerMoney = self.__itemsCache.items.stats.money
        shortage = playerMoney.getShortage(priceInGold)
        if shortage and shortage.getCurrency() == Currency.GOLD:
            showBuyGoldForEarlyAccess(priceInGold)
        else:
            action = factory.getAction(BUY_EARLY_ACCESS_TOKENS, buyTokensAmount)
            result = yield factory.asyncDoAction(action)
            self.viewModel.setBuyResult(BuyResult.SUCCESS if result else BuyResult.FAIL)
            self.__earlyAccessCtrl.onPayed(result, buyTokensAmount)
            if not result and not self.__itemsCache.items.stats.mayConsumeWalletResources:
                self.__exitBuyWindow()

    def __onBackToPrevScreen(self):
        self.__exitBuyWindow()

    def __exitBuyWindow(self):
        self.destroyWindow()
        if self.__backCallback is not None:
            self.__backCallback()
        return


class EarlyAccessBuyViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None, backCallback=None):
        super(EarlyAccessBuyViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=EarlyAccessBuyView(R.views.lobby.early_access.EarlyAccessBuyView(), backCallback=backCallback), parent=parent)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_buy_bundle_view.py
import BigWorld
from adisp import adisp_process
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_buy_bundle_view_model import ArmoryYardBuyBundleViewModel, BundleType
from armory_yard.gui.window_events import showBuyGoldForArmoryYard
from armory_yard.gui.impl.lobby.feature.tooltips.rest_reward_tooltip_view import RestRewardTooltipView
from armory_yard.gui.shared.bonus_packers import getArmoryYardBuyViewPacker, packRestModel
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from gui.shared.money import Currency
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.Scaleform.Waiting import Waiting
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.wgcg.shop.contexts import ShopBuyStorefrontProductCtx
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController, IWalletController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
BUNDLE_TYPES = {'small_bundle': BundleType.SMALL,
 'medium_bundle': BundleType.MEDIUM,
 'large_bundle': BundleType.LARGE}

class ArmoryYardBuyBundleView(ViewImpl):
    __slots__ = ('__tooltipData', '__blur', '__onLoadedCallback', '__parent', '__bundleId', '__timeoutCallback', '__isBuying', '__stepAfterBuy', '__onClosedCallback')
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self, layoutID, bundleId, parent=None, isBlurEnabled=False, onLoadedCallback=None, onClosedCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ArmoryYardBuyBundleViewModel()
        super(ArmoryYardBuyBundleView, self).__init__(settings)
        self.__tooltipData = {}
        self.__blur = CachedBlur(ownLayer=self.layer - 1) if isBlurEnabled else None
        self.__onLoadedCallback = onLoadedCallback
        self.__parent = parent
        self.__bundleId = bundleId
        self.__timeoutCallback = None
        self.__isBuying = False
        self.__stepAfterBuy = None
        self.__onClosedCallback = onClosedCallback
        return

    @property
    def viewModel(self):
        return super(ArmoryYardBuyBundleView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardBuyBundleView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.RestRewardTooltipView():
            tooltipData = self.getTooltipData(event)
            return RestRewardTooltipView([] if tooltipData is None else tooltipData.specialArgs[0])
        else:
            return super(ArmoryYardBuyBundleView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipData.get(event.getArgument('tooltipId'), None)

    def destroyWindow(self, isScene=False):
        if self.__isBuying or self.__timeoutCallback is not None and not self.__isTokenDelivered():
            return
        else:
            if isScene:
                if self.__onClosedCallback is not None:
                    self.__onClosedCallback(True)
                g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)
            super(ArmoryYardBuyBundleView, self).destroyWindow()
            return

    @adisp_process
    def onBuyBundle(self):
        if self.__isBuying:
            return
        else:
            product = None
            for bundle in self.__armoryYardCtrl.bundlesProducts:
                if self.__bundleId == bundle['id']:
                    product = bundle

            if product is None:
                self.__armoryYardCtrl.onPayedError()
                return
            price = product['price']
            shortage = self.__itemsCache.items.stats.money.getShortage(price)
            currency = price.getCurrency()
            if shortage:
                setCurrencies = shortage.getSetCurrencies()
                if len(setCurrencies) == 1 and setCurrencies[0] == Currency.GOLD:
                    showBuyGoldForArmoryYard(price)
            else:
                self.__isBuying = True
                if not Waiting.isOpened('buyBundleArmoryYard'):
                    Waiting.show('buyBundleArmoryYard', isAlwaysOnTop=True, isSingle=True)
                bundleTokens = product['tokens']
                self.__stepAfterBuy = self.__armoryYardCtrl.getCurrencyTokenCount() + bundleTokens
                maxTokensCount = self.__armoryYardCtrl.getTotalSteps()
                postProgressionCoins = 0
                if self.__stepAfterBuy > maxTokensCount:
                    if self.__armoryYardCtrl.isPostProgressionEnabled():
                        postProgressionCoins = self.__stepAfterBuy - maxTokensCount
                    self.__stepAfterBuy = maxTokensCount
                result = yield self.__webCtrl.sendRequest(ctx=ShopBuyStorefrontProductCtx(storefront=self.__armoryYardCtrl.getStarterPackSettings()['storefrontName'], productCode=product['productCode'], amount=1, prices=[{'code': currency,
                  'amount': price.get(currency),
                  'item_type': 'currency'}]))
                if result.isSuccess():
                    self.__armoryYardCtrl.refreshBundle()
                    if postProgressionCoins > 0:
                        self.__armoryYardCtrl.onPayed(False, bundleTokens - postProgressionCoins)
                        self.__armoryYardCtrl.onPayed(True, postProgressionCoins)
                    else:
                        self.__armoryYardCtrl.onPayed(False, bundleTokens)
                    if not self.__isTokenDelivered():
                        self.__timeoutCallback = BigWorld.callback(10, self.__timeout)
                    else:
                        Waiting.hide('buyBundleArmoryYard')
                        self.destroyWindow(isScene=True)
                else:
                    Waiting.hide('buyBundleArmoryYard')
                    self.__armoryYardCtrl.onPayedError()
                self.__isBuying = False
            return

    def __isTokenDelivered(self):
        return self.__stepAfterBuy is not None and self.__stepAfterBuy <= self.__armoryYardCtrl.getCurrencyTokenCount()

    def __timeout(self):
        if Waiting.isOpened('buyBundleArmoryYard'):
            Waiting.hide('buyBundleArmoryYard')
        self.__timeoutCallback = None
        self.__armoryYardCtrl.onBundleOutTime()
        self.destroyWindow(isScene=True)
        return

    def onClose(self):
        self.destroyWindow(isScene=True)

    def onBack(self):
        self.destroyWindow()

    def _onLoaded(self, *args, **kwargs):
        super(ArmoryYardBuyBundleView, self)._onLoaded(*args, **kwargs)
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardBuyBundleView, self)._onLoading(*args, **kwargs)
        if self.__blur is not None:
            self.__blur.enable()
        self.__fullUpdate()
        self.viewModel.setIsBlurEnabled(self.__blur is not None)
        return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.disable()
        super(ArmoryYardBuyBundleView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),
         (self.viewModel.onBack, self.onBack),
         (self.viewModel.onBuyBundle, self.onBuyBundle),
         (self.__armoryYardCtrl.onUpdated, self.__onProgressUpdated),
         (self.__armoryYardCtrl.onProgressUpdated, self.__onProgressUpdated),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self.__armoryYardCtrl.onBundlesDisabled, self.__onProgressUpdated))

    def __setMainData(self):
        with self.viewModel.transaction() as model:
            currentTokens = self.__armoryYardCtrl.getCurrencyTokenCount()
            maxTokens = self.__armoryYardCtrl.getTotalSteps()
            for bundle in self.__armoryYardCtrl.bundlesProducts:
                if self.__bundleId == bundle['id']:
                    product = bundle

            bundleType = BundleType.MEDIUM
            for tag in product['tags']:
                if tag in BUNDLE_TYPES:
                    bundleType = BUNDLE_TYPES[tag]
                    break

            endLevel = currentTokens + product['tokens']
            model.setIsWalletAvailable(self.__wallet.isAvailable)
            model.setStartLevel(currentTokens + 1)
            model.setEndLevel(endLevel if maxTokens >= endLevel else maxTokens)
            model.setType(bundleType)
            PriceModelBuilder.fillPriceModel(model.price, product['price'], checkBalanceAvailability=True)

    def __fullUpdate(self):
        self.__setMainData()
        self.__fillRewards()

    def __onProgressUpdated(self):
        if self.__timeoutCallback is not None and self.__isTokenDelivered():
            BigWorld.cancelCallback(self.__timeoutCallback)
            self.__timeoutCallback = None
            if Waiting.isOpened('buyBundleArmoryYard'):
                Waiting.hide('buyBundleArmoryYard')
            self.destroyWindow(isScene=True)
            return
        elif not self.__armoryYardCtrl.isActive() or self.__armoryYardCtrl.isCompleted() or not self.__armoryYardCtrl.isStarterPackAvailable():
            self.destroyWindow(isScene=True)
            return
        else:
            self.__fullUpdate()
            return

    def __fillRewards(self):
        with self.viewModel.transaction() as model:
            rewards = model.getRewards()
            rewards.clear()
            self.__tooltipData.clear()
            stepsRewards = self.__armoryYardCtrl.getStepsRewards()
            rewardsList = []
            for stepId in range(model.getStartLevel(), model.getEndLevel() + 1):
                for rewardType, rewardValue in stepsRewards[stepId].items():
                    rewardsList.extend(getNonQuestBonuses(rewardType, rewardValue))

            rewardsList = splitBonuses(mergeBonuses(rewardsList))
            rewardsList.sort(key=bonusesSortKeyFunc)
            for idx, value in enumerate(rewardsList):
                if value.getName() == 'battleToken' and value.getValue().get('ny24_yaga') is not None:
                    rewardsList.pop(idx)

            if len(rewardsList) > ArmoryYardBuyBundleViewModel.MAX_VISIBLE_REWARDS:
                packBonusModelAndTooltipData(rewardsList[:ArmoryYardBuyBundleViewModel.MAX_VISIBLE_REWARDS - 1], rewards, self.__tooltipData, packer=getArmoryYardBuyViewPacker())
                packRestModel(rewardsList[ArmoryYardBuyBundleViewModel.MAX_VISIBLE_REWARDS - 1:], rewards, self.__tooltipData, ArmoryYardBuyBundleViewModel.MAX_VISIBLE_REWARDS - 1)
            else:
                packBonusModelAndTooltipData(rewardsList, rewards, self.__tooltipData, packer=getArmoryYardBuyViewPacker())
            rewards.invalidate()
        return

    def __onWalletStatusChanged(self, *_):
        with self.viewModel.transaction() as vm:
            vm.setIsWalletAvailable(self.__wallet.isAvailable)


class ArmoryYardBuyBundleWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, bundleId, parent=None, isBlurEnabled=False, onLoadedCallback=None, onClosedCallback=None):
        super(ArmoryYardBuyBundleWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=ArmoryYardBuyBundleView(R.views.armory_yard.lobby.feature.ArmoryYardBuyBundleView(), bundleId, parent, isBlurEnabled, onLoadedCallback, onClosedCallback), parent=parent)

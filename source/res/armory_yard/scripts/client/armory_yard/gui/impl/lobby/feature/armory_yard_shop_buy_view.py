# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_shop_buy_view.py
import json
from typing import Tuple
from functools import partial
import BigWorld
from armory_yard_constants import PDATA_KEY_ARMORY_YARD, SHOP_PDATA_KEY, SHOP_LAST_SEASON_COMPLETED
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_shop_buy_view_model import ArmoryYardShopBuyViewModel
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_wallet_not_available_tooltip_view import ArmoryYardWalletNotAvailableTooltipView
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_view_model import State
from armory_yard.gui.impl.lobby.feature.armory_yard_shop_base import ArmoryYardShopBaseView
from armory_yard.gui.impl.lobby.feature.tooltips.rest_reward_tooltip_view import RestRewardTooltipView
from armory_yard.gui.shared.bonus_packers import getArmoryYardBuyViewPacker, packRestModel
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from armory_yard.gui.shared.shop_bonus_packers import packShopItem, getBonusPacker
from armory_yard.gui.window_events import showBuyGoldForArmoryYard, showArmoryYardShopWindow, showArmoryYardRewardWindow, showArmoryYardVehiclePreview, showArmoryYardShopRewardWindow, showArmoryYardShopBuyWindow
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, mergeBonuses
from gui.impl import backport
from gui.shared.money import Currency
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings, ViewFlags, ViewModel
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.game_control import IWalletController, IArmoryYardShopController, IArmoryYardController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.impl import IGuiLoader
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class ArmoryYardShopBuyView(ArmoryYardShopBaseView):
    __slots__ = ('__productId', '__tooltipData', '__onClosedCallback', '__isPurchasing', '__isArmoryVisiting')
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __armoryYardShopCtrl = dependency.descriptor(IArmoryYardShopController)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, productId, onClosedCallback=None, onLoadedCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ArmoryYardShopBuyViewModel()
        super(ArmoryYardShopBuyView, self).__init__(settings, onLoadedCallback)
        self.__tooltipData = {}
        self.__productId = productId
        self.__onClosedCallback = onClosedCallback
        self.__isPurchasing = False
        self.__isArmoryVisiting = self.__armoryYardCtrl.isArmoryVisiting

    @property
    def viewModel(self):
        return super(ArmoryYardShopBuyView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardShopBuyView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.RestRewardTooltipView():
            tooltipData = self.getTooltipData(event)
            return RestRewardTooltipView([] if tooltipData is None else tooltipData.specialArgs[0])
        elif contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardWalletNotAvailableTooltipView():
            return ArmoryYardWalletNotAvailableTooltipView()
        else:
            return ViewImpl(ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ShopCurrencyTooltipView(), model=ViewModel())) if contentID == R.views.armory_yard.lobby.feature.tooltips.ShopCurrencyTooltipView() else super(ArmoryYardShopBuyView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipData.get(event.getArgument('tooltipId'), None)

    def onBuyProduct(self, args):
        gold, tokens, count = int(args['gold']), int(args['tokens']), int(args.get('count', 1))
        if not self.__checkCost(gold, tokens, count):
            return
        self.__isPurchasing = True
        BigWorld.player().AccountArmoryYardComponent.buyShopProduct(self.__productId, count, json.dumps({Currency.GOLD: gold / self.viewModel.getGoldConversion()} if gold > 0 else {}), callback=partial(self.__onPurchaseResponse, isBundle=self.__armoryYardShopCtrl.isBundle(self.__productId), stages=self.__getProductData().get('UI', {}).get('stages', 1)))
        if not Waiting.isOpened('buyItem'):
            Waiting.show('buyItem', isAlwaysOnTop=True, isSingle=True)

    def __checkExit(self):
        if not self.__armoryYardCtrl.isActive() and self.__isArmoryVisiting:
            self.destroyWindow()

    def onClose(self):
        if self.__onClosedCallback:
            self.__onClosedCallback()
        self.destroyWindow()

    def onBack(self):
        if self.__onClosedCallback is None and not self.__isShopViewExist():
            showArmoryYardShopWindow(onLoadedCallback=self.destroyWindow)
        else:
            self.destroyWindow()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardShopBuyView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addCallbacks({PDATA_KEY_ARMORY_YARD: self.__checkAvailable,
         'cache.dynamicCurrencies': self.__updatePlayerMoney})
        g_clientUpdateManager.addMoneyCallback(self.__updatePlayerMoney)
        self.__update()
        self.__updatePlayerMoney()
        self.__onWalletStatusChanged()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),
         (self.viewModel.onBack, self.onBack),
         (self.viewModel.onBuyProduct, self.onBuyProduct),
         (self.viewModel.onShowVehiclePreview, self.__onShowVehiclePreview),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self.__armoryYardShopCtrl.onSettingsUpdate, self.__update),
         (self.__armoryYardShopCtrl.onProductsUpdate, self.__update),
         (self.__armoryYardCtrl.onUpdated, self.__checkExit))

    def __findView(self, view):
        return view.layoutID == R.views.armory_yard.lobby.feature.ArmoryYardShopView()

    def __isShopViewExist(self):
        windows = self.__gui.windowsManager.findViews(self.__findView)
        return len(windows)

    def __checkCost(self, gold, tokens, count):
        goldConversion = self.__armoryYardShopCtrl.conversionPrices.get(Currency.GOLD)
        playerGold, playerTokens = self.__getPlayerMoney()
        fundsShortage = max(gold - playerGold, 0)
        fundsToken = max(tokens - playerTokens, 0)
        if fundsToken > 0 or fundsShortage > 0:
            showBuyGoldForArmoryYard(gold + fundsToken * goldConversion)
            return False
        productCost = self.__getProductData()['price'] * goldConversion * count
        playerCost = tokens * goldConversion + gold
        return productCost == playerCost

    def __backCallback(self):
        showArmoryYardShopBuyWindow(productId=self.__productId)

    def __onShowVehiclePreview(self):
        vehicleCD = self.__getVehicleCD()
        if vehicleCD:
            vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
            self.onClose()
            if not self.__armoryYardCtrl.isArmoryVisiting:
                showArmoryYardVehiclePreview(vehicle.intCD, previewAlias=VIEW_ALIAS.LOBBY_STORE, showHeroTankText=False, previewBackCb=self.__backCallback, isNeedHeroTankHidden=True)
            else:
                self.__armoryYardCtrl.isVehiclePreview = True
                showArmoryYardVehiclePreview(vehicle.intCD, backToHangar=False, showHeroTankText=False, previewBackCb=partial(self.__armoryYardCtrl.goToArmoryYard, ctx={'loadShopBuyView': True,
                 'productID': self.__productId}), backBtnLabel=backport.text(R.strings.armory_shop.shopBuyView.backGoto()))
            self.__armoryYardCtrl.cameraManager.goToHangar()

    def __onPurchaseResponse(self, requestID, resultID, errorStr, data=None, isBundle=False, stages=0):
        Waiting.hide('buyItem')
        self.__isPurchasing = False
        if resultID < 0:
            self.__armoryYardShopCtrl.onPurchaseError()
            self.__update()
        else:
            rewards = data['rewards']
            rewardsCount = len(rewards)
            self.__armoryYardShopCtrl.onPurchaseComplete(data['productID'], data['currencies'], rewards, isBundle)
            if rewardsCount > 1:
                showArmoryYardRewardWindow(rewards, state=State.SHOP, closeCallback=showArmoryYardShopWindow, stage=stages)
            else:
                packer = getBonusPacker(data['productID'], rewards)
                showArmoryYardShopRewardWindow(packer.title, packer.largeIcon, packer.count, packer.itemType, closeCallback=showArmoryYardShopWindow)
            self.onClose()

    def __update(self):
        if self.__isPurchasing:
            return
        elif not self.__armoryYardShopCtrl.isEnabled:
            self.destroyWindow()
            return
        else:
            productData = self.__getProductData()
            if productData is None:
                self.onClose()
                return
            with self.viewModel.transaction() as model:
                model.item.setItemID(self.__productId)
                model.setGoldConversion(self.__armoryYardShopCtrl.conversionPrices.get(Currency.GOLD, None))
                itemModel = model.item
                itemModel.setItemID(self.__productId)
                packShopItem(self.__productId, productData, itemModel, isLargeIcon=True)
                itemModel.setAvailable(self.__armoryYardShopCtrl.isSeasonCompleted)
                self.__fillRewards(model.getRewards())
            return

    def __getProductData(self):
        return self.__armoryYardShopCtrl.products.get(self.__productId)

    def __getPlayerMoney(self):
        money = self.__itemsCache.items.stats.actualMoney
        dynMoney = self.__itemsCache.items.stats.dynamicCurrencies
        return (money.gold, dynMoney.get(Currency.AYCOIN, 0))

    def __fillRewards(self, modelRewardsList):
        modelRewardsList.clear()
        self.__tooltipData.clear()
        rewards = []
        for rewardType, rewardValue in self.__getProductData()['bonus'].items():
            rewards.extend(getNonQuestBonuses(rewardType, rewardValue))

        rewards = splitBonuses(mergeBonuses(rewards))
        rewards.sort(key=bonusesSortKeyFunc)
        isExceedsVisible = int(len(rewards) > self.viewModel.MAX_VISIBLE_REWARDS)
        packBonusModelAndTooltipData(rewards[:self.viewModel.MAX_VISIBLE_REWARDS - isExceedsVisible], modelRewardsList, tooltipData=self.__tooltipData, packer=getArmoryYardBuyViewPacker())
        if isExceedsVisible:
            packRestModel(rewards[self.viewModel.MAX_VISIBLE_REWARDS - isExceedsVisible:], modelRewardsList, self.__tooltipData, self.viewModel.MAX_VISIBLE_REWARDS - isExceedsVisible, restRewardsTextId=R.strings.armory_shop.shopBuyView.reward.rest())
        modelRewardsList.invalidate()

    def __onWalletStatusChanged(self, *_):
        with self.viewModel.transaction() as vm:
            vm.setIsWalletAvailable(self.__wallet.isAvailable)

    def __checkAvailable(self, diff):
        if SHOP_LAST_SEASON_COMPLETED in diff.get(SHOP_PDATA_KEY, {}):
            with self.viewModel.transaction() as model:
                model.item.setAvailable(self.__armoryYardShopCtrl.isSeasonCompleted)

    def __updatePlayerMoney(self, _=None):
        gold, tokens = self.__getPlayerMoney()
        if self.viewModel.getGoldAmount() == int(gold) and self.viewModel.getCurrencyAmount() == tokens:
            return
        with self.viewModel.transaction() as model:
            model.setGoldAmount(int(gold))
            model.setCurrencyAmount(tokens)

    def __getVehicleCD(self):
        vehicles = self.__getProductData()['bonus'].get('vehicles', {})
        return vehicles.keys()[0] if vehicles else None


class ArmoryYardShopBuyWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, productId, onClosedCallback=None, onLoadedCallback=None):
        super(ArmoryYardShopBuyWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=ArmoryYardShopBuyView(R.views.armory_yard.lobby.feature.ArmoryYardShopBuyView(), productId, onClosedCallback=onClosedCallback, onLoadedCallback=onLoadedCallback))

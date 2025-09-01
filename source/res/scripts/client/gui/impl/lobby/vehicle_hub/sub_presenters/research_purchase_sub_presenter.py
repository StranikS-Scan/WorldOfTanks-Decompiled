# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/research_purchase_sub_presenter.py
from __future__ import absolute_import
import typing
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.game_control.links import URLMacros
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.research_purchase_model import ResearchPurchaseModel
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.shared import events, g_eventBus
from gui.shared.event_dispatcher import showBlueprintView, selectVehicleInHangar, showShop
from gui.shared.gui_items.gui_item_economics import getPriceTypeAndValue, ActualPrice
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import ITradeInController, IHeroTankController, IWalletController, IRestoreController
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.server_events.event_items import Action

class ResearchPurchaseSubPresenter(SubPresenterBase):
    _restores = dependency.descriptor(IRestoreController)
    _tradeIn = dependency.descriptor(ITradeInController)
    _heroTanks = dependency.descriptor(IHeroTankController)
    _wallet = dependency.descriptor(IWalletController)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, model, parentView):
        super(ResearchPurchaseSubPresenter, self).__init__(model, parentView)
        self.__action = ''
        self.__actionState = ''

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, vhCtx, *args, **kwargs):
        super(ResearchPurchaseSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        g_techTreeDP.load()
        self.__fillViewModel()

    def finalize(self):
        self.__action = None
        super(ResearchPurchaseSubPresenter, self).finalize()
        return

    def setVehicleHubCtx(self, vhCtx):
        super(ResearchPurchaseSubPresenter, self).setVehicleHubCtx(vhCtx)
        self.__fillViewModel()

    def _getEvents(self):
        return ((self.viewModel.onAction, self.__onAction),
         (self.viewModel.onBlueprint, self.__onShowBlueprint),
         (self._itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self._wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self._restores.onRestoreChangeNotify, self.__onRestoreChanged))

    def __fillViewModel(self):
        with self.viewModel.transaction() as model:
            self.__fillResearchPurchase(model)

    def __fillResearchPurchase(self, model):
        veh = self.currentVehicle
        stats = self._itemsCache.items.stats
        actionState = ResearchPurchaseModel.ACTION_STATE_ENABLED
        actionStateReason = ''
        currency = ''
        vehPrice = 0
        oldPrice = 0
        priceDiscount = 0
        timeLeft = -1
        info = veh.restoreInfo
        if veh.isInInventory:
            action = ResearchPurchaseModel.ACTION_IN_GARAGE
        elif self.__isHeroTank:
            action = ResearchPurchaseModel.ACTION_PURCHASE_SHOP
            if not (self._heroTanks.getCurrentShopUrl() or self._heroTanks.getCurrentRelatedURL()):
                actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
        elif veh.isUnlocked or veh.isCollectible:
            shop = self._itemsCache.items.shop
            money = self._tradeIn.addTradeInPriceIfNeeded(veh, stats.money)
            priceType, price = getPriceTypeAndValue(veh, money, shop.defaults.exchangeRate)
            currency = price.getCurrency()
            isCurrencyAvailable = self.__walletAvailableForCurrency(currency)
            isGoldAvailable = self.__walletAvailableForCurrency(Currency.GOLD)
            mayObtainForMoney, _ = veh.mayObtainForMoney(money)
            mayObtainWithExchange = veh.mayObtainWithMoneyExchange(money, proxy=shop)
            isBuyingAvailable = not veh.isHidden or veh.isRentable or veh.isRestorePossible()
            if priceType == ActualPrice.RESTORE_PRICE:
                action = ResearchPurchaseModel.ACTION_RESTORE
                vehPrice = price.get(currency)
                if not veh.isRestorePossible():
                    actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                if info.isInCooldown():
                    timeLeft = info.getRestoreCooldownTimeLeft()
                else:
                    timeLeft = 0 if info.isUnlimited() else info.getRestoreTimeLeft()
            else:
                action = ResearchPurchaseModel.ACTION_PURCHASE
                vehPrice = price.price.get(currency)
                oldPrice = price.defPrice.get(currency)
                priceDiscount = price.getActionPrc()
            if vehPrice > 0:
                if not isCurrencyAvailable:
                    actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                    actionStateReason = ResearchPurchaseModel.ACTION_DESC_WALLET_UNAVAILABLE
                elif mayObtainForMoney:
                    pass
                elif not isGoldAvailable:
                    actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                    actionStateReason = ResearchPurchaseModel.ACTION_DESC_WALLET_UNAVAILABLE
                elif mayObtainWithExchange:
                    pass
                elif currency == Currency.GOLD and isBuyingAvailable:
                    pass
                elif info and info.isInCooldown():
                    actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                    actionStateReason = ResearchPurchaseModel.ACTION_DESC_RESTORE_REQUESTED
                else:
                    actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                    actionStateReason = ResearchPurchaseModel.ACTION_DESC_NOT_ENOUGH_CREDITS
        else:
            action = ResearchPurchaseModel.ACTION_RESEARCH
            currency = 'tankXP'
            _, isXpEnough = g_techTreeDP.isVehicleAvailableToUnlock(veh.intCD, veh.level)
            isNext2Unlock, unlockProps = g_techTreeDP.isNext2Unlock(veh.intCD, unlocked=set(stats.unlocks), xps=stats.vehiclesXPs, freeXP=stats.freeXP, level=veh.level)
            isFreeXpAvailable = self.__walletAvailableForCurrency(Currency.FREE_XP)
            vehPrice = unlockProps.xpCost
            if unlockProps.discount:
                oldPrice = unlockProps.xpFullCost
                priceDiscount = unlockProps.discount
            else:
                oldPrice = 0
                priceDiscount = 0
            if not isNext2Unlock:
                actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                actionStateReason = ResearchPurchaseModel.ACTION_DESC_PARENT_MODULE_IS_LOCKED
            elif not isFreeXpAvailable:
                actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                actionStateReason = ResearchPurchaseModel.ACTION_DESC_WALLET_UNAVAILABLE
            elif not isXpEnough:
                actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
                actionStateReason = ResearchPurchaseModel.ACTION_DESC_NOT_ENOUGH_XP
        self.__action = action
        self.__actionState = actionState
        model.setAction(action)
        model.setActionState(actionState)
        model.setActionStateReason(actionStateReason)
        model.setPrice(vehPrice)
        model.setCooldownTimeLeft(info.getRestoreCooldownTimeLeft() if info else 0)
        model.setOldPrice(oldPrice)
        model.setPriceDiscount(priceDiscount)
        model.setCurrency(currency)
        model.setTimeLeft(timeLeft)
        model.setNotInShopVehicle(veh.isDisabledForBuy or veh.isHidden)
        model.setElite(veh.isElite)
        model.setPremium(veh.isPremium)
        blueprintData = self._itemsCache.items.blueprints.getBlueprintData(veh.intCD, veh.level)
        if blueprintData is not None and g_techTreeDP.getTopLevel(veh.intCD):
            model.setBlueprintFragments(blueprintData.filledCount)
            model.setBlueprintTotal(blueprintData.totalCount)
        else:
            model.setBlueprintFragments(0)
            model.setBlueprintTotal(0)
        model.setCombatXp(stats.vehiclesXPs.get(veh.intCD, 0))
        model.setFreeXp(stats.freeXP)
        promo = self.__promo
        if promo is not None and veh.isUnlocked:
            model.setPromoTitle(promo.getUserName())
            model.setPromoFinishTime(promo.getFinishTime())
        return

    def __walletAvailableForCurrency(self, currency):
        return self._wallet.componentsStatuses.get(currency) == self._wallet.STATUS.AVAILABLE

    @property
    def __isHeroTank(self):
        return self._heroTanks.getCurrentTankCD() == self.currentVehicle.intCD

    @property
    def __promo(self):
        actions = self._eventsCache.getItemAction(self.currentVehicle)
        if actions:
            _, bestActionID = min(actions, key=lambda elem: elem[0])
            return self._eventsCache.getActions().get(bestActionID)
        else:
            return None

    def __onAction(self):
        if self.__actionState == ResearchPurchaseModel.ACTION_STATE_DISABLED:
            return
        veh = self.currentVehicle
        if self.__action == ResearchPurchaseModel.ACTION_RESEARCH:
            unlockProps = g_techTreeDP.getUnlockProps(veh.intCD, veh.level)
            factory.doAction(factory.UNLOCK_ITEM, veh.intCD, unlockProps)
        elif self.__action in (ResearchPurchaseModel.ACTION_PURCHASE, ResearchPurchaseModel.ACTION_RESTORE):
            factory.doAction(factory.BUY_VEHICLE, self.currentVehicle.intCD)
        elif self.__action == ResearchPurchaseModel.ACTION_PURCHASE_SHOP:
            self.__purchaseHeroTank()
        elif self.__action == ResearchPurchaseModel.ACTION_IN_GARAGE:
            selectVehicleInHangar(veh.intCD)

    @adisp_process
    def __purchaseHeroTank(self):
        url = self._heroTanks.getCurrentRelatedURL()
        shopUrl = self._heroTanks.getCurrentShopUrl()
        if shopUrl:
            showShop(shopUrl)
        elif url:
            parsedUrl = yield URLMacros().parse(url)
            g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=parsedUrl))

    def __onShowBlueprint(self):
        showBlueprintView(self.currentVehicle.intCD)

    def __onSyncCompleted(self, reason, diff):
        self.__fillViewModel()

    def __onWalletStatusChanged(self, *args):
        self.__fillViewModel()

    def __onRestoreChanged(self, vehicles):
        if self.currentVehicle.intCD in vehicles:
            self.__fillViewModel()

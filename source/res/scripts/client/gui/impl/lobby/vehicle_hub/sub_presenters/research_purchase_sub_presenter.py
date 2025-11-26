# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/research_purchase_sub_presenter.py
from __future__ import absolute_import
import typing
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.game_control.links import URLMacros
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.research_purchase_model import ResearchPurchaseModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.vehicle_hub.sub_presenters.sub_presenter_base import SubPresenterBase
from gui.shared import events, g_eventBus
from gui.shared.events import VehicleBuyEvent
from gui.shared.event_bus import EVENT_BUS_SCOPE
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

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, vhCtx, *args, **kwargs):
        super(ResearchPurchaseSubPresenter, self).initialize(vhCtx, *args, **kwargs)
        g_techTreeDP.load()
        self.__fillViewModel()

    def setVehicleHubCtx(self, vhCtx):
        super(ResearchPurchaseSubPresenter, self).setVehicleHubCtx(vhCtx)
        self.__fillViewModel()

    def _getEvents(self):
        return ((self.viewModel.onAction, self.__onAction),
         (self.viewModel.onBlueprint, self.__onShowBlueprint),
         (self._itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self._wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self._restores.onRestoreChangeNotify, self.__onRestoreChanged))

    def _getListeners(self):
        return ((VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeInVehicleToSellSelected, EVENT_BUS_SCOPE.DEFAULT),)

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
        tradeInVehicleToSell = self._tradeIn.getSelectedVehicleToSell()
        shop = self._itemsCache.items.shop
        money = self._tradeIn.addTradeInPriceIfNeeded(veh, stats.money)
        priceType, price = getPriceTypeAndValue(veh, money, shop.defaults.exchangeRate)
        if veh.isInInventory:
            if veh.isOnlyForEventBattles or veh.isOnlyForEpicBattles:
                action = ResearchPurchaseModel.ACTION_STATE_DISABLED
                actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
            elif veh.isRented and not veh.isHidden and not veh.isPremiumIGR and not veh.isWotPlus and not veh.isDisabledForBuy:
                currency = price.getCurrency()
                vehPrice = price.price.get(currency)
                oldPrice = price.defPrice.get(currency)
                priceDiscount = price.getActionPrc()
                action = ResearchPurchaseModel.ACTION_PURCHASE_CAN_VIEW_IN_GARAGE
                actionState, actionStateReason = self.__setActionState(actionState, actionStateReason, veh, vehPrice, currency, money, shop, info)
            else:
                action = ResearchPurchaseModel.ACTION_IN_GARAGE
        elif self.__isHeroTank:
            action = ResearchPurchaseModel.ACTION_PURCHASE_SHOP
            if not (self._heroTanks.getCurrentShopUrl() or self._heroTanks.getCurrentRelatedURL()):
                actionState = ResearchPurchaseModel.ACTION_STATE_DISABLED
        elif self.currentVehicle.canTradeIn and tradeInVehicleToSell is not None and tradeInVehicleToSell.canTradeOff:
            action = ResearchPurchaseModel.ACTION_READY_FOR_TRADE_IN
            tradeInPrice = self._tradeIn.getTradeInPrice(self.currentVehicle)
            currency = tradeInPrice.getCurrency()
            vehPrice = tradeInPrice.price.get(currency)
            oldPrice = tradeInPrice.defPrice.get(currency)
            priceDiscount = tradeInPrice.getActionPrc()
            actionState, actionStateReason = self.__setActionState(actionState, actionStateReason, veh, vehPrice, currency, money, shop, info)
        elif veh.isUnlocked or veh.isCollectible:
            currency = price.getCurrency()
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
            actionState, actionStateReason = self.__setActionState(actionState, actionStateReason, veh, vehPrice, currency, money, shop, info)
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
        model.setAction(action)
        model.setActionState(actionState)
        model.setActionStateReason(actionStateReason)
        model.setCanTradeIn(self.currentVehicle.canTradeIn)
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
        else:
            model.setPromoFinishTime(0)
        return

    def __setActionState(self, actionState, actionStateReason, veh, vehPrice, currency, money, shop, info):
        isCurrencyAvailable = self.__walletAvailableForCurrency(currency)
        isGoldAvailable = self.__walletAvailableForCurrency(Currency.GOLD)
        mayObtainForMoney, _ = veh.mayObtainForMoney(money)
        mayObtainWithExchange = veh.mayObtainWithMoneyExchange(money, proxy=shop)
        isBuyingAvailable = not veh.isHidden or veh.isRentable or veh.isRestorePossible()
        if vehPrice <= 0:
            return (actionState, actionStateReason)
        if not isCurrencyAvailable:
            return (ResearchPurchaseModel.ACTION_STATE_DISABLED, ResearchPurchaseModel.ACTION_DESC_WALLET_UNAVAILABLE)
        if mayObtainForMoney:
            return (actionState, actionStateReason)
        if not isGoldAvailable:
            return (ResearchPurchaseModel.ACTION_STATE_DISABLED, ResearchPurchaseModel.ACTION_DESC_WALLET_UNAVAILABLE)
        if mayObtainWithExchange:
            return (actionState, actionStateReason)
        if currency == Currency.GOLD and isBuyingAvailable:
            return (actionState, actionStateReason)
        return (ResearchPurchaseModel.ACTION_STATE_DISABLED, ResearchPurchaseModel.ACTION_DESC_RESTORE_REQUESTED) if info and info.isInCooldown() else (ResearchPurchaseModel.ACTION_STATE_DISABLED, ResearchPurchaseModel.ACTION_DESC_NOT_ENOUGH_CREDITS)

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

    @args2params(str)
    def __onAction(self, action):
        veh = self.currentVehicle
        if action == ResearchPurchaseModel.ACTION_RESEARCH:
            unlockProps = g_techTreeDP.getUnlockProps(veh.intCD, veh.level)
            factory.doAction(factory.UNLOCK_ITEM, veh.intCD, unlockProps)
        elif action in (ResearchPurchaseModel.ACTION_PURCHASE, ResearchPurchaseModel.ACTION_RESTORE, ResearchPurchaseModel.ACTION_READY_FOR_TRADE_IN):
            factory.doAction(factory.BUY_VEHICLE, self.currentVehicle.intCD)
        elif action == ResearchPurchaseModel.ACTION_PURCHASE_SHOP:
            self.__purchaseHeroTank()
        elif action == ResearchPurchaseModel.ACTION_IN_GARAGE:
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

    def __onTradeInVehicleToSellSelected(self, _=None):
        self.__fillViewModel()

    def __onSyncCompleted(self, reason, diff):
        self.__fillViewModel()

    def __onWalletStatusChanged(self, *args):
        self.__fillViewModel()

    def __onRestoreChanged(self, vehicles):
        if self.currentVehicle.intCD in vehicles:
            self.__fillViewModel()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/pet/ny_pet_shop_view.py
import SoundGroups
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import IndicatorType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.pet_shop.ny_pet_shop import NyPetShop
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.pet_shop.shop_card import ShopCard
from new_year.gui.impl.new_year.sounds import RaccoonStates
from new_year.gui.impl.lobby.new_year.sub_model_presenter import SubModelPresenter
from gui.customization.shared import getPurchaseMoneyState, MoneyForPurchase
from new_year.skeletons.new_year import INewYearCurrencyController, ITamagotchiDataProvider, ITamagotchiWebRequester
from gui.shared.money import Money
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NyPetShopView(SubModelPresenter):
    __slots__ = ()
    _INTERNAL_VIEW_STATE = None
    _nyCurrencyController = dependency.descriptor(INewYearCurrencyController)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _webRequester = dependency.descriptor(ITamagotchiWebRequester)
    _itemsCache = dependency.descriptor(IItemsCache)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onBuy, self.__onBuy),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onAmountChange, self.__onAmountChange),
         (self.viewModel.onDialogClose, self.__onDialogClose),
         (self.viewModel.onDialogSubmit, self.__onDialogSubmit),
         (self._itemsCache.onSyncCompleted, self.__onSyncCompleted),
         (self._dataProvider.onItemsPurchased, self.__onItemsPurchased))

    def initialize(self, *args, **kwargs):
        self.toggleVisibility(False)
        super(NyPetShopView, self).initialize(*args, **kwargs)

    def finalize(self):
        super(NyPetShopView, self).finalize()
        if self.viewModel.getIsShopEnabled():
            self.__closeAction()
        self.clear()

    def toggleVisibility(self, enable):
        self.viewModel.setIsShopEnabled(enable)
        self._dataProvider.onUpdateTipsRequested(not enable)
        if enable:
            SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.SHOP)
            self.__initShopCards()

    def __onSyncCompleted(self, *_, **__):
        with self.viewModel.transaction() as tx:
            for card in self.viewModel.getShopCards():
                count = self._dataProvider.getIndicatorCurrency(card.getType().value)
                card.setItemsInInventory(count)

            canBuy = self.__canBuy(tx.getFullPrice())
            tx.setIsBuyButtonEnabled(canBuy)
            tx.setIsEnough(canBuy)

    def __initShopCards(self):
        with self.viewModel.transaction() as model:
            cards = model.getShopCards()
            cards.clear()
            pInfo = self._dataProvider.playerInfo
            for name, _ in pInfo.indicators.iteritems():
                card = self.__makeShopCard(name)
                cards.addViewModel(card)

            cards.invalidate()

    def __makeShopCard(self, indicatorName):
        card = ShopCard()
        config = self._dataProvider.config.indicators[indicatorName]
        indicatorType = IndicatorType(indicatorName.lower())
        giftsLeft = config.giftCountUnlock - self._dataProvider.initialPlayerInfo.giftCollected
        card.setType(indicatorType)
        card.setLettersToUnlock(max(0, giftsLeft))
        card.setCurrentPointPrice(config.item.price)
        card.setCurrentPrice(config.item.price)
        card.setId(config.item.id)
        card.setLoyaltyPoints(config.item.leaderboardPoint)
        card.setVitalityPoints(config.item.scalePoint)
        card.setItemsInInventory(self._dataProvider.getIndicatorCurrency(indicatorName))
        card.setIsLocked(giftsLeft > 0)
        return card

    def __onBuy(self):
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.ITEMS)
        self.viewModel.setIsDialogScreen(True)

    def __onClose(self):
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.MAIN)
        self.__closeAction()

    def __closeAction(self):
        self.toggleVisibility(False)
        self._nyCurrencyController.setVisibleCurrencies()

    def __onAmountChange(self, args):
        if not self.viewModel.getIsShopEnabled():
            return
        cardType, amount = args.values()
        indicatorType = IndicatorType(cardType)
        with self.viewModel.transaction() as model:
            fullPrice = 0
            for card in model.getShopCards():
                if card.getIsLocked():
                    card.setCount(0)
                    card.setCurrentPrice(0)
                    continue
                if card.getType() == indicatorType:
                    card.setCurrentPrice(amount * card.getCurrentPointPrice())
                    card.setCount(amount)
                fullPrice += card.getCurrentPrice()

            model.setFullPrice(fullPrice)
            canBuy = self.__canBuy(fullPrice)
            model.setIsBuyButtonEnabled(canBuy)
            model.setIsEnough(canBuy)

    def __onDialogClose(self):
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.SHOP)
        self.viewModel.setIsDialogScreen(False)

    def __onDialogSubmit(self):
        SoundGroups.g_instance.setState(RaccoonStates.GROUP, RaccoonStates.MAIN)
        self.__purchase()
        with self.viewModel.transaction() as tx:
            self.viewModel.setIsDialogScreen(False)
            self.__toggleWaiting(True, tx)

    def __onItemsPurchased(self, *_, **__):
        with self.viewModel.transaction() as tx:
            self.__toggleWaiting(False, tx)
        self.__closeAction()

    @staticmethod
    def __toggleWaiting(state, model):
        cards = model.getShopCards()
        if cards:
            cards[0].setIsWaiting(state)
            cards.invalidate()

    @staticmethod
    def __canBuy(totalPrice):
        price = Money(credits=totalPrice)
        moneyState = getPurchaseMoneyState(price)
        return moneyState == MoneyForPurchase.ENOUGH

    def __purchase(self):
        body = dict()
        for card in self.viewModel.getShopCards():
            count = card.getCount()
            if count > 0:
                body[card.getId()] = count

        self._webRequester.buyItems(body)

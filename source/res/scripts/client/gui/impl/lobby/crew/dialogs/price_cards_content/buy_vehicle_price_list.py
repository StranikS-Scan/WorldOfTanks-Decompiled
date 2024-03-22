# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/price_cards_content/buy_vehicle_price_list.py
from gui.impl.gen.view_models.views.lobby.crew.dialogs.price_card_model import CardState
from gui.impl.lobby.crew.dialogs.price_cards_content.recruit_new_tankman_price_list import RecruitNewTankmanPriceList
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Currency, Money
from helpers import dependency
from skeletons.gui.game_control import IWalletController

class BuyVehiclePriceList(RecruitNewTankmanPriceList):
    __wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__hasFreePremiumCrew', '__defaultSelectedCardIndex', '__amount', '__vehicleLevel')

    def __init__(self, vehicleLevel, amount=1, selectedCardIndex=0):
        self.__hasFreePremiumCrew = False
        self.__amount = amount
        self.__vehicleLevel = vehicleLevel
        super(BuyVehiclePriceList, self).__init__()
        self._selectedCardIndex = selectedCardIndex
        self.__defaultSelectedCardIndex = selectedCardIndex

    def setHasFreePremiumCrew(self, value):
        if self.__hasFreePremiumCrew != value:
            self.__hasFreePremiumCrew = value
            self._fillPrices()
            self._selectedCardIndex = self._getAvailableCardIndex() if value else self.__defaultSelectedCardIndex
            self._updateViewModel()

    def _getEvents(self):
        events = super(BuyVehiclePriceList, self)._getEvents()
        return events + ((self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),)

    def _deselectCurrentCard(self, vm):
        if self._selectedCardIndex is None:
            return
        else:
            cardData = self.selectedOperationData
            state = CardState.DISABLED if cardData.get('disabled', False) else CardState.DEFAULT
            self._getCard(vm, self._selectedCardIndex).setCardState(state)
            return

    def _getCustomData(self, xp, itemPrice):
        isPremium = itemPrice.defPrice.get(Currency.GOLD, 0) > 0
        isPriceAvailable = self.__isAvailablePrice(itemPrice.price)
        return {'xp': xp,
         'disabled': self.__hasFreePremiumCrew and not isPremium or not isPriceAvailable,
         'isFreeCrew': self.__hasFreePremiumCrew and isPremium}

    def _getAvailableCardIndex(self):
        for _, cardData, index in self._priceData:
            if not cardData.get('disabled', False):
                return index

        return None

    def _fillPrices(self):
        shopRequester = self._itemsCache.items.shop
        opts = shopRequester.tankman['recruit']['options']
        optsDef = shopRequester.defaults.tankman['recruit']['options']
        self._priceData = []
        for idx, (option, optionDef) in enumerate(zip(opts, optsDef)):
            itemPrice = ItemPrice(price=Money(credits=option.get(Currency.CREDITS, 0), gold=option.get(Currency.GOLD, 0)), defPrice=Money(credits=optionDef.get(Currency.CREDITS, 0), gold=optionDef.get(Currency.GOLD, 0)))
            self._priceData.append((itemPrice * self.__amount, self._getCustomData(option['xp'], itemPrice), idx))

    def _updateCustomData(self):
        updated = []
        for itemPrice, customData, idx in self._priceData:
            updated.append((itemPrice, self._getCustomData(customData['xp'], itemPrice), idx))

        self._priceData = updated

    def _updateViewModel(self):
        self._updateCustomData()
        super(BuyVehiclePriceList, self)._updateViewModel()

    def _selectCard(self, vm, index=None):
        super(BuyVehiclePriceList, self)._selectCard(vm, self.__defaultSelectedCardIndex if index is None else index)
        return

    def __isAvailablePrice(self, money):
        isPurchaseCurrencyAvailable = money.isDefined()
        statsMoney = self._itemsCache.items.stats.money
        for currency in Currency.ALL:
            currencyValue = money.get(currency)
            if currencyValue and currencyValue > statsMoney.get(currency, 0):
                isPurchaseCurrencyAvailable &= self.__isPurchaseCurrencyAvailable(currency)

        return statsMoney >= money or isPurchaseCurrencyAvailable

    def __isPurchaseCurrencyAvailable(self, currencyType):
        return currencyType == Currency.GOLD and self.__wallet.isAvailable

    def __onWalletStatusChanged(self, *_):
        self._updateViewModel()

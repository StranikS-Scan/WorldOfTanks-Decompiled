# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/exchange_coins_view.py
import typing
from adisp import adisp_process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.footer.single_price_footer import SinglePriceFooter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import TooltipType
from gui.impl.gen.view_models.views.dialogs.sub_views.currency_view_model import CurrencySize
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.gui_items.items_actions.factory import asyncDoAction
from gui.shared.money import Money
from helpers import dependency
from historical_battles.gui.impl.dialogs.sub_views.content.exchange_coins import ExchangeCoins, getPotentiallyAvailableCoinsAmount
from historical_battles.gui.impl.dialogs.sub_views.top_right.hb_money_balance import HBMoneyBalance
from historical_battles.gui.shared.gui_items.items_actions.hb_coin import ExchangeHBCoinsAction
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.dialogs.dialog_template_button import ButtonPresenter
    from frameworks.wulf import View

class ExchangeCoinsView(DialogTemplateView):
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    leftCoin = ''
    rightCoin = ''

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.historical_battles.gui.maps.icons.backgrounds.shopBackground())
        self.setSubView(Placeholder.TOP_RIGHT, HBMoneyBalance(isGoldVisible=True, isCreditsVisible=True))
        if not ExchangeCoinsView.leftCoin or not ExchangeCoinsView.rightCoin or not self._isCoinAvailable(ExchangeCoinsView.leftCoin) or not self._isCoinAvailable(ExchangeCoinsView.rightCoin):
            availableCoins = self._pickAvailableCoins()
            ExchangeCoinsView.leftCoin = availableCoins[0]
            ExchangeCoinsView.rightCoin = availableCoins[1]
        self.setSubView(Placeholder.CONTENT, ExchangeCoins(ExchangeCoinsView.leftCoin, ExchangeCoinsView.rightCoin))
        self.setSubView(Placeholder.FOOTER, SinglePriceFooter(R.strings.hb_shop.coins_exchange.cost, ItemPrice(Money(), Money()), CurrencySize.BIG))
        self.addButton(ConfirmButton(label=R.strings.hb_lobby.coinExchangeWidget.exchangeBtn()))
        self.addButton(CancelButton())
        super(ExchangeCoinsView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        self.content.onCountChanged += self._countChangeHandler
        self._countChangeHandler()

    def _pickAvailableCoins(self):
        result = []
        for front in self._gameEventController.frontController.getOrderedFrontsList():
            coinName = front.getCoinsName()
            if self._isCoinAvailable(front.getCoinsName()):
                result.append(coinName)

        return result

    def _isCoinAvailable(self, coinName):
        return self._gameEventController.coins.isExchangeEnabled(coinName) and self._gameEventController.coins.isExchangeStarted(coinName)

    @property
    def content(self):
        return self.getSubView(Placeholder.CONTENT)

    @property
    def footer(self):
        return self.getSubView(Placeholder.FOOTER)

    @property
    def confirmButton(self):
        return self.getButton(DialogButtons.SUBMIT)

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.content.onCountChanged -= self._countChangeHandler
        super(ExchangeCoinsView, self)._finalize()

    @adisp_process
    def _setResult(self, result):
        yield lambda callback: callback(True)
        if result == DialogButtons.SUBMIT:
            success = yield asyncDoAction(ExchangeHBCoinsAction(self.content.leftCoin, self.content.rightCoin, self.content.count))
            if success:
                ExchangeCoinsView.leftCoin = self.content.leftCoin
                ExchangeCoinsView.rightCoin = self.content.rightCoin
            else:
                return
        super(ExchangeCoinsView, self)._setResult(result)

    def _moneyChangeHandler(self, *_):
        self._handleConfirmButton()

    def _countChangeHandler(self):
        currency, amount = self._gameEventController.coins.getExchangePrice(self.content.leftCoin)
        exchangePrice = Money.makeFrom(currency, amount) * self.content.count
        self.footer.updatePrice(ItemPrice(exchangePrice, exchangePrice))
        self._handleConfirmButton()

    def _handleConfirmButton(self):
        availableCoinsAmount = getPotentiallyAvailableCoinsAmount(self.content.leftCoin)
        isDisabled = self.content.count > availableCoinsAmount or self.content.count == 0
        self.confirmButton.isDisabled = isDisabled
        if self.content.count == 0:
            self.confirmButton.tooltip.tooltipType = TooltipType.UNBOUND
            self.confirmButton.tooltip.factory = self._noCoinsTooltipFactory
        elif self.content.count > availableCoinsAmount:
            self.confirmButton.tooltip.tooltipType = TooltipType.BACKPORT
            self.confirmButton.tooltip.factory = self._notEnoughMoneyTooltipFactory if bool(self.footer.getShortage()) else None
        else:
            self.confirmButton.tooltip.factory = None
        return

    def _notEnoughMoneyTooltipFactory(self):
        shortage = self.footer.getShortage()
        currency = shortage.getCurrency()
        return createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (shortage.get(currency), currency))

    def _noCoinsTooltipFactory(self):
        front = self._gameEventController.frontController.getFrontByCoinName(self.content.leftCoin)
        frontName = backport.text(R.strings.hb_lobby.battleModeSmall.dyn(front.getName())())
        rNoCoins = R.strings.hb_shop.coins_exchange.tooltip.noCoins
        return SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), header=backport.text(rNoCoins.header()), body=backport.text(rNoCoins.body(), name=frontName))

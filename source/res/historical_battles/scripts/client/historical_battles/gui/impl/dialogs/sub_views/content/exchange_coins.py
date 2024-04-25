# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/dialogs/sub_views/content/exchange_coins.py
import typing
from helpers.dependency import replace_none_kwargs
from helpers.time_utils import ONE_MINUTE
from Event import Event
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.backport import text
from gui.impl.dialogs.dialog_template_tooltip import DialogTemplateTooltip
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.shared.money import Currency
from helpers import dependency, time_utils
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.exchange_coin_data_model import ExchangeCoinDataModel
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.exchange_coins_model import ExchangeCoinsModel
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.exchange_coins_side_model import Side
from historical_battles.gui.shared.formatters.time_formatter import getFormattedTimeLeft, TIMER_TYPE_3
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Callable
    from historical_battles.gui.server_events.game_event.front_progress import FrontProgress
    from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.exchange_coins_side_model import ExchangeCoinsSideModel
    from frameworks.wulf import View
STEPPER_MAX_VALUE = 99999
FIVE_MINUTES = 5 * ONE_MINUTE

@replace_none_kwargs(itemsCache=IItemsCache, gameEventController=IGameEventController)
def getPotentiallyAvailableCoinsAmount(coinName, itemsCache=None, gameEventController=None):
    currency, amount = gameEventController.coins.getExchangePrice(coinName)
    msg = 'Unsupported exchange price!'
    if amount == 0:
        return gameEventController.coins.getCount(coinName)
    canExchangeCreditsAmount = itemsCache.items.shop.exchangeRate * itemsCache.items.stats.money.gold
    availableCredits = canExchangeCreditsAmount + itemsCache.items.stats.money.credits
    return int(availableCredits / amount)


class ExchangeCoins(ViewImpl):
    _LAYOUT_DYN_ACCESSOR = R.views.historical_battles.dialogs.sub_views.content.ExchangeCoinsView
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    onCountChanged = Event()

    def __init__(self, leftCoin, rightCoin, layoutID=None):
        settings = ViewSettings(layoutID or self._LAYOUT_DYN_ACCESSOR())
        settings.model = ExchangeCoinsModel()
        super(ExchangeCoins, self).__init__(settings)
        self._count = 1
        self._leftCoin = leftCoin
        self._rightCoin = rightCoin
        self._tooltips = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def count(self):
        return self._count

    @property
    def leftCoin(self):
        return self._leftCoin

    @property
    def rightCoin(self):
        return self._rightCoin

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            coinName = event.getArgument('name')
            side = event.getArgument('side')
            tooltip = self._tooltips.get((Side(side), coinName))
            if tooltip and tooltip.factory:
                return tooltip.factory()
        return super(ExchangeCoins, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(ExchangeCoins, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self._moneyChangeHandler)
        self._gameEventController.coins.onCoinsCountChanged += self._coinsCountChangeHandler
        self._gameEventController.onGameParamsChanged += self._gameParamsChangeHandler
        self.viewModel.onStepperValueChanged += self._stepperChangeHandler
        self.viewModel.left.onDropdownItemClicked += self._leftDropdownItemClickHandler
        self.viewModel.right.onDropdownItemClicked += self._rightDropdownItemClickHandler
        self._initDropdownList(self.viewModel.left)
        self._initDropdownList(self.viewModel.right)
        self._updateNumericStepper()
        self._updateDropdowns()

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        coins = self._gameEventController.coins
        if coins:
            coins.onCoinsCountChanged -= self._coinsCountChangeHandler
        self._gameEventController.onGameParamsChanged -= self._gameParamsChangeHandler
        self.viewModel.onStepperValueChanged -= self._stepperChangeHandler
        self.viewModel.left.onDropdownItemClicked -= self._leftDropdownItemClickHandler
        self.viewModel.right.onDropdownItemClicked -= self._rightDropdownItemClickHandler
        super(ExchangeCoins, self)._finalize()

    def _gameParamsChangeHandler(self):
        self._updateViewModel()

    def _moneyChangeHandler(self, *_):
        self._updateViewModel()

    def _coinsCountChangeHandler(self, *_):
        self._updateViewModel()

    def _getSide(self, sideVM):
        return Side.RIGHT if sideVM == self.viewModel.right else Side.LEFT

    def _initDropdownList(self, sideVM):
        side = self._getSide(sideVM)
        sideVM.setSide(side)
        array = sideVM.getDropdownList()
        for front in self._gameEventController.frontController.getFronts().itervalues():
            coinsName = front.getCoinsName()
            coinDataModel = ExchangeCoinDataModel()
            coinDataModel.setName(coinsName)
            self._tooltips[side, coinsName] = DialogTemplateTooltip(viewModel=coinDataModel.tooltip)
            array.addViewModel(coinDataModel)

    def _updateDropdownList(self, sideVM, selectedCoinName):
        side = self._getSide(sideVM)
        sideVM.setCoinName(selectedCoinName)
        array = sideVM.getDropdownList()
        getCoinsCount = self._gameEventController.coins.getCount
        for index, front in enumerate(self._gameEventController.frontController.getFronts().itervalues()):
            coinName = front.getCoinsName()
            coinDataModel = array[index]
            isExchangeEnabled = self._gameEventController.coins.isExchangeEnabled(coinName)
            isExchangeStarted = self._gameEventController.coins.isExchangeStarted(coinName)
            isEnabled = front.isEnabled() and front.isStarted() and isExchangeEnabled and isExchangeStarted
            coinDataModel.setEnabled(isEnabled)
            tooltip = self._tooltips[side, coinName]
            if isEnabled:
                tooltip.factory = None
            elif not front.isStarted():
                tooltip.factory = self._getNoFrontTooltipFactory(front)
            else:
                tooltip.factory = self._coinsDisabledTooltipFactory
            count = getCoinsCount(front.getCoinsName())
            if coinName == selectedCoinName and side == Side.RIGHT:
                count += self._count
            coinDataModel.setAmount(count)

        array.invalidate()
        return

    def _stepperChangeHandler(self, args):
        value = args.get('value', 0)
        self._count = value
        with self.viewModel.transaction():
            self._updateDropdowns()
            self.viewModel.setStepperValue(self._count)
        self.onCountChanged()

    def _leftDropdownItemClickHandler(self, args):
        clickedCoin = args.get('coinName')
        if self._rightCoin == clickedCoin:
            self._rightCoin = self._leftCoin
        self._leftCoin = clickedCoin
        self._updateViewModel()

    def _rightDropdownItemClickHandler(self, args):
        clickedCoin = args.get('coinName')
        if self._leftCoin == clickedCoin:
            self._leftCoin = self._rightCoin
        self._rightCoin = clickedCoin
        self._updateViewModel()

    def _updateViewModel(self):
        with self.viewModel.transaction():
            self._updateNumericStepper()
            self._updateDropdowns()

    def _updateDropdowns(self):
        vm = self.viewModel
        self._updateDropdownList(vm.left, self._leftCoin)
        self._updateDropdownList(vm.right, self._rightCoin)

    def _updateNumericStepper(self):
        vm = self.viewModel
        availableCoinAmount = getPotentiallyAvailableCoinsAmount(self._leftCoin)
        availableCoinAmount += 1
        coinCount = self._gameEventController.coins.getCount(self._leftCoin)
        stepperMaxValue = min(STEPPER_MAX_VALUE, coinCount, availableCoinAmount)
        vm.setStepperMaxValue(stepperMaxValue)
        leftFront = self._gameEventController.frontController.getFrontByCoinName(self._leftCoin)
        stepperMinValue = 1 if leftFront.isEnabled() and coinCount > 0 else 0
        vm.setStepperMinValue(stepperMinValue)
        self._count = min(stepperMaxValue, max(stepperMinValue, self._count))
        vm.setStepperValue(self._count)
        self.onCountChanged()

    @staticmethod
    def _coinsDisabledTooltipFactory():
        return SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), body=text(R.strings.hb_shop.coins_exchange.tooltip.turnedOff.body()))

    @staticmethod
    def _getNoFrontTooltipFactory(front):
        startTimeLeft = time_utils.getTimeDeltaFromNow(front.getStartTime())
        timeLeftFormatted = getFormattedTimeLeft(startTimeLeft, TIMER_TYPE_3, FIVE_MINUTES)

        def create():
            return SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), body=text(R.strings.hb_shop.coins_exchange.tooltip.noFront.body(), name=text(R.strings.hb_lobby.battleModeSmall.dyn(front.getName())()), time=timeLeftFormatted))

        return create

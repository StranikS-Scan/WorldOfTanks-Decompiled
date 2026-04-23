# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/dialogs/sub_views/top_right/hb_money_balance.py
import logging
import typing
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.dialog_template_generic_tooltip_view_model import TooltipType
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.hb_money_balance_coin_model import HbMoneyBalanceCoinModel
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.hb_money_balance_model import HbMoneyBalanceModel
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

class HBMoneyBalance(MoneyBalance):
    __slots__ = ()
    _VIEW_MODEL = HbMoneyBalanceModel
    _LAYOUT_DYN_ACC = R.views.historical_battles.dialogs.sub_views.topRight.HBMoneyBalance
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID=None, isCrystalsVisible=False, isGoldVisible=False, isCreditsVisible=False, isFreeExpVisible=False):
        super(HBMoneyBalance, self).__init__(layoutID=layoutID or self._LAYOUT_DYN_ACC())
        model = self.viewModel
        model.setIsCrystalsVisible(isCrystalsVisible)
        model.setIsGoldVisible(isGoldVisible)
        model.setIsCreditsVisible(isCreditsVisible)
        model.setIsFreeExpVisible(isFreeExpVisible)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            name = event.getArgument('name')
            if name:
                return HbCoinTooltip(name)
        return super(HBMoneyBalance, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(HBMoneyBalance, self)._onLoading(*args, **kwargs)
        self._gameEventController.coins.onCoinsCountChanged += self.__coinsCountChangeHandler
        self.__updateCoins()

    def _finalize(self):
        coins = self._gameEventController.coins
        if coins:
            coins.onCoinsCountChanged -= self.__coinsCountChangeHandler
        super(HBMoneyBalance, self)._finalize()

    def __coinsCountChangeHandler(self, *_):
        with self.viewModel.transaction():
            self.__updateCoins()

    def __updateCoins(self):
        coins = self.viewModel.getCoins()
        coins.clear()
        for front in self._gameEventController.frontController.getFronts().itervalues():
            coinName = front.getCoinsName()
            coinVM = HbMoneyBalanceCoinModel()
            coinVM.setName(coinName)
            count = self._gameEventController.coins.getCount(coinName)
            coinVM.setCount(count)
            coinVM.tooltip.setType(TooltipType.GAMEFACE)
            coins.addViewModel(coinVM)

        coins.invalidate()

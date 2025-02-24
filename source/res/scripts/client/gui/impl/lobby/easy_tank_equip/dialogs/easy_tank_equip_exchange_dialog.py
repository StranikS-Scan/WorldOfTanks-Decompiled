# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/dialogs/easy_tank_equip_exchange_dialog.py
from typing import TYPE_CHECKING
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.buy_and_exchange_bottom_content_type import BuyAndExchangeBottomContentType
from gui.impl.gen.view_models.views.lobby.common.dialog_with_exchange import DialogWithExchange
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.dialogs.buy_and_exchange import BuyAndExchange
from gui.impl.lobby.dialogs.contents.exchange_content import ExchangeContentResult, ExchangeMoneyInfo
from gui.impl.lobby.easy_tank_equip.dialogs.contents.easy_tank_equip_exchange_content import EasyTankEquipExchangeContent
from gui.shared.money import ZERO_MONEY, Currency
if TYPE_CHECKING:
    from gui.shared.money import Money

class ExchangeToApplyEasyTankEquip(BuyAndExchange):
    __slots__ = ('__availableGoldAmount',)

    def __init__(self, *args, **kwargs):
        price = kwargs.pop('price', ZERO_MONEY)
        self.__availableGoldAmount = kwargs.pop('availableGoldAmount', 0)
        settings = ViewSettings(layoutID=R.views.lobby.tanksetup.dialogs.ExchangeToApplyEasyTankEquip(), model=DialogWithExchange(), args=args, kwargs=kwargs)
        super(ExchangeToApplyEasyTankEquip, self).__init__(settings=settings, price=price, startState=BuyAndExchangeStateEnum.EXCHANGE_CONTENT)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _createExchangeContent(self):
        return EasyTankEquipExchangeContent(fromItem=ExchangeMoneyInfo(currencyType=Currency.GOLD), toItem=ExchangeMoneyInfo(Currency.CREDITS), viewModel=self.viewModel.exchangePanel, needItem=self._needItemsForExchange(), availableGoldAmount=self.__availableGoldAmount)

    def _exchangeComplete(self, result):
        if result == ExchangeContentResult.IS_OK:
            self._onAccept()

    def _stateToContent(self):
        return {BuyAndExchangeStateEnum.EXCHANGE_CONTENT: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.NEED_EXCHANGE: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_NOT_REQUIRED: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.EXCHANGE_IN_PROCESS: BuyAndExchangeBottomContentType.EXCHANGE_PANEL,
         BuyAndExchangeStateEnum.GOLD_NOT_ENOUGH: BuyAndExchangeBottomContentType.EXCHANGE_PANEL}

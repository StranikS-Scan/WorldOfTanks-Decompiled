# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/shared/gui_items/items_actions/actions.py
from __future__ import absolute_import
from adisp import adisp_async
import wg_async as future_async
from gui.shared.gui_items.items_actions.actions import BuyAndInstallConsumables
from gui.shared.gui_items.items_actions.actions import _needExchangeForBuy
from gui.shared.money import ZERO_MONEY
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from halloween.gui.shared.event_dispatcher import showHWTankSetupConfirmDialog
from gui.shared.utils import decorators
from gui.shared.gui_items.processors.vehicle import BuyAndInstallConsumablesProcessor
from gui.shared.gui_items.processors.messages.items_processor_messages import ItemBuyProcessorMessage
from gui.shared.money import Money
from gui.shared.gui_items.processors import makeSuccess
from gui.impl import backport
from gui.impl.gen import R

class HWBuyAndInstallConsumables(BuyAndInstallConsumables):
    __slots__ = ('__confirmOnlyExchange',)

    def __init__(self, vehicle, confirmOnlyExchange=False):
        super(HWBuyAndInstallConsumables, self).__init__(vehicle, confirmOnlyExchange=confirmOnlyExchange)
        self.__confirmOnlyExchange = confirmOnlyExchange

    @adisp_async
    @future_async.wg_async
    def _confirm(self, callback):
        if self._changedItems and _needExchangeForBuy(sum([ item.getBuyPrice().price for item in self._changedItems if not item.isInInventory ], ZERO_MONEY)):
            startState = BuyAndExchangeStateEnum.EXCHANGE_CONTENT
        elif self._changedItems:
            startState = BuyAndExchangeStateEnum.BUY_CONTENT
        else:
            startState = BuyAndExchangeStateEnum.BUY_NOT_REQUIRED
        if self.__confirmOnlyExchange and startState != BuyAndExchangeStateEnum.EXCHANGE_CONTENT:
            callback(True)
        else:
            result = yield future_async.wg_await(showHWTankSetupConfirmDialog(items=self._changedItems, vehicle=self._vehicle, startState=startState))
            callback(result.result[0] if not result.busy else False)

    @adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield HWBuyAndInstallConsumablesProcessor(self._vehicle).request()
        callback(result)


class HWBuyAndInstallConsumablesProcessor(BuyAndInstallConsumablesProcessor):

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        if ctx:
            additionalMessages = [ HWItemBuyProcessorMessage(self.itemsCache.items.getItemByCD(cd), count, Money.makeFromMoneyTuple(price)).makeSuccessMsg() for cd, price, count in ctx.get('eqs', []) ]
        return makeSuccess(auxData=additionalMessages)


class HWItemBuyProcessorMessage(ItemBuyProcessorMessage):

    def _getMsgCtx(self):
        res = super(HWItemBuyProcessorMessage, self)._getMsgCtx()
        res['kind'] = backport.text(R.strings.halloween_system_messages.hw_equipment.title())
        return res

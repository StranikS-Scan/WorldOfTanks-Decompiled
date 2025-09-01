# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/gui_items/items_actions/actions.py
import BigWorld
from adisp import adisp_async
import wg_async as future_async
from gui.shared.gui_items.items_actions.actions import BuyAndInstallConsumables
from gui.shared.gui_items.items_actions.actions import _needExchangeForBuy
from gui.shared.money import ZERO_MONEY
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from last_stand.gui.shared.event_dispatcher import showTankSetupConfirmDialog
from gui.shared.utils import decorators
from gui.shared.gui_items.processors.vehicle import BuyAndInstallConsumablesProcessor
from gui.shared.money import Money
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.processors.messages.items_processor_messages import ItemBuyProcessorMessage
from gui.shared.gui_items.processors import plugins as proc_plugs, makeSuccess
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
from LSAccountEquipmentController import getLSConsumables

class LSItemBuyProcessorMessage(ItemBuyProcessorMessage):

    def _getMsgCtx(self):
        res = super(LSItemBuyProcessorMessage, self)._getMsgCtx()
        res['kind'] = backport.text(R.strings.last_stand_system_messages.ls_equipment.title())
        return res


def getConsumablesPrice(consumables):
    result = sum([ item.getBuyPrice() for item in consumables.layout.getItems() if not item.isInInventory and item not in consumables.installed ], ITEM_PRICE_ZERO)
    return result


class LSConsumablesInstallValidator(proc_plugs.ConsumablesInstallValidator):

    def _getLayout(self):
        return getLSConsumables(self._vehicle).layout

    def _getInstalled(self):
        return getLSConsumables(self._vehicle).installed


class LSBuyAndInstallConsumablesProcessor(BuyAndInstallConsumablesProcessor):

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        if ctx:
            additionalMessages = [ LSItemBuyProcessorMessage(self.itemsCache.items.getItemByCD(cd), count, Money.makeFromMoneyTuple(price)).makeSuccessMsg() for cd, price, count in ctx.get('eqs', []) ]
        return makeSuccess(auxData=additionalMessages)

    def _setupPlugins(self):
        self.addPlugins((proc_plugs.VehicleValidator(self._vehicle), proc_plugs.MoneyValidator(getConsumablesPrice(getLSConsumables(self._vehicle)).price, byCurrencyError=False), LSConsumablesInstallValidator(self._vehicle)))

    def _request(self, callback):
        eqCtrl = BigWorld.player().LSAccountEquipmentController
        eqCtrl.updateSelectedEquipment(self._vehicle.invID, self.__getLayoutRaw(), lambda _, code, errStr, ext={}: self._response(code, callback, errStr=errStr, ctx=ext))

    def __getLayoutRaw(self):
        return [ (item.intCD if item is not None else 0) for item in getLSConsumables(self._vehicle).layout ]


class LSBuyAndInstallConsumables(BuyAndInstallConsumables):
    __slots__ = ('__confirmOnlyExchange',)

    def __init__(self, vehicle, confirmOnlyExchange=False):
        super(LSBuyAndInstallConsumables, self).__init__(vehicle, confirmOnlyExchange)
        consumables = getLSConsumables(vehicle)
        self._changedItems = [ item for item in consumables.layout.getItems() if item not in consumables.installed ]
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
            result = yield future_async.wg_await(showTankSetupConfirmDialog(items=self._changedItems, vehicle=self._vehicle, startState=startState))
            callback(result.result[0] if not result.busy else False)

    @adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield LSBuyAndInstallConsumablesProcessor(self._vehicle).request()
        callback(result)

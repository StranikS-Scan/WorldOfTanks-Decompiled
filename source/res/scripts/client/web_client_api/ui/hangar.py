# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/hangar.py
import logging
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsSingleItemMeta, ExchangeCreditsWebProductMeta
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from web_client_api import W2CSchema, w2c, Field
from helpers import dependency
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class _OpenHangarTabSchema(W2CSchema):
    vehicle_id = Field(required=False, type=int)


_EXCHANGE_WINDOW_SIMPLE = 'simple'
_EXCHANGE_WINDOW_PLATFORM = 'platform'
_EXCHANGE_WINDOW_TYPES = frozenset([_EXCHANGE_WINDOW_SIMPLE, _EXCHANGE_WINDOW_PLATFORM])

class _ExchangeWindowSchema(W2CSchema):
    id = Field(required=False, type=int, default=None)
    amount = Field(required=False, type=int, default=1)
    price = Field(required=False, type=int, default=0)
    name = Field(required=False, type=basestring, default='')
    type = Field(required=False, type=basestring, default=_EXCHANGE_WINDOW_SIMPLE)


class HangarTabWebApiMixin(object):

    @w2c(_OpenHangarTabSchema, 'hangar')
    def openHangar(self, cmd):
        if cmd.vehicle_id:
            shared_events.selectVehicleInHangar(cmd.vehicle_id)
        else:
            shared_events.showHangar()


class HangarWindowsWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_ExchangeWindowSchema, 'currency_exchange')
    def openCurrencyExchangeWindow(self, cmd):
        if cmd.id is not None:
            if not self.validateItems(cmd.id):
                return
            isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsSingleItemMeta(itemCD=cmd.id, count=cmd.amount))
            yield {'completed': isOk}
        elif cmd.type == _EXCHANGE_WINDOW_PLATFORM:
            isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsWebProductMeta(name=cmd.name, count=cmd.amount, price=cmd.price))
            yield {'completed': isOk}
        else:
            shared_events.showExchangeCurrencyWindow()
        return

    @w2c(W2CSchema, 'show_xp_exchange_window')
    def openXPExchangeWindow(self, _):
        shared_events.showExchangeXPWindow()

    @w2c(W2CSchema, 'show_buy_slot_window')
    def openBuySlotWindow(self, _):
        ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE_SLOT)

    @w2c(W2CSchema, 'show_buy_berth_window')
    def openBuyBerthWindow(self, _):
        ActionsFactory.doAction(ActionsFactory.BUY_BERTHS)

    def validateItems(self, itemCD):
        item = self.itemsCache.items.getItemByCD(itemCD)
        if item is None or item.itemTypeID == GUI_ITEM_TYPE.FUEL_TANK:
            _logger.error('Incorrect item is given, intCD: %s', itemCD)
            return False
        else:
            return True

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/trade.py
from collections import namedtuple
from gui import SystemMessages
from gui.SystemMessages import pushMessagesFromResult
from gui.shared.gui_items.processors.common import GoldToCreditsExchanger, PremiumAccountBuyer
from gui.shared.gui_items.processors.goodies import BoosterBuyer
from gui.shared.gui_items.processors.module import ModuleBuyer
from gui.shared.gui_items.processors.vehicle import VehicleBuyer, showVehicleReceivedResultMessages
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from web.web_client_api import Field, W2CSchema, w2c
from web.web_client_api.common import ShopItemType
_ItemBuySpec = namedtuple('ItemBuySpec', ('type', 'id', 'count'))
_EXCHANGER = {Currency.GOLD: lambda value: GoldToCreditsExchanger(value, withConfirm=False)}

def parseItemsSpec(specList):
    specList = specList or tuple()
    fields = {'type', 'id', 'count'}
    if not all((set(spec).issubset(fields) for spec in specList)):
        raise SoftException('invalid item buy spec')
    for spec in specList:
        if not ShopItemType.hasValue(spec['type']):
            raise SoftException('unsupported item type "{}"'.format(spec['type']))

    return [ _ItemBuySpec(spec['type'], spec['id'], spec['count']) for spec in specList ]


def itemsSpecValidator(specList):
    try:
        parseItemsSpec(specList)
    except SoftException:
        raise

    return True


def _currencyExchangeValidator(_, data):
    return all((v > 0 and c in _EXCHANGER.iterkeys() for c, v in data.get('currencies', {}).iteritems()))


class _BuyItemsSchema(W2CSchema):
    items = Field(required=True, type=list, validator=lambda value, _: itemsSpecValidator(value))


class _CurrencyExchangeSchema(W2CSchema):
    currencies = Field(required=True, type=dict, validator=_currencyExchangeValidator)


class TradeWebApiMixin(object):
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_CurrencyExchangeSchema, 'exchange')
    def exchange(self, cmd):
        exchangeResults = {}
        for currencyType, currencyValue in cmd.currencies.iteritems():
            result = yield _EXCHANGER[currencyType](currencyValue).request()
            exchangeResults[currencyType] = {'success': result.success,
             'message': result.userMsg}
            pushMessagesFromResult(result)

        yield exchangeResults

    @w2c(_BuyItemsSchema, 'buy_items')
    def buyItems(self, cmd):
        responses = []
        items = self._itemsCache.items
        for spec in parseItemsSpec(cmd.items):
            if spec.type in (ShopItemType.DEVICE, ShopItemType.EQUIPMENT, ShopItemType.BATTLE_BOOSTER):
                item = items.getItemByCD(spec.id)
                currency = item.buyPrices.itemPrice.price.getCurrency()
                buyer = ModuleBuyer(item, spec.count, currency)
            elif spec.type == ShopItemType.BOOSTER:
                item = self._goodiesCache.getBooster(spec.id)
                currency = item.buyPrices.itemPrice.price.getCurrency()
                buyer = BoosterBuyer(item, spec.count, currency)
            elif spec.type == ShopItemType.VEHICLE:
                item = items.getItemByCD(spec.id)
                buyer = VehicleBuyer(item, buySlot=False, showNotEnoughSlotMsg=False)
            elif spec.type == ShopItemType.PREMIUM:
                daysCount = spec.count
                buyer = PremiumAccountBuyer(daysCount, price=items.shop.getPremiumCostWithDiscount()[daysCount], requireConfirm=False)
            else:
                raise SoftException('Invalid item type: "{}".'.format(spec.type))
            if buyer:
                response = yield buyer.request()
                responses.append(self.__makeResult(spec.type, spec.id, response))
            responses.append(None)

        results = []
        for response in responses:
            status = response['success']
            if status and status.userMsg:
                if response['type'] == ShopItemType.VEHICLE:
                    showVehicleReceivedResultMessages(status)
                else:
                    SystemMessages.pushI18nMessage(status.userMsg, type=status.sysMsgType)
                statusData = status.auxData
                if statusData is None or 'errStr' not in statusData or not statusData['errStr']:
                    result = 'success'
                else:
                    result = statusData['errStr']
                results.append(self.__makeResult(response['type'], response['id'], status.success, result))
            results.append(self.__makeResult(response['type'], response['id'], False))

        yield results
        return

    @staticmethod
    def __makeResult(itemType, itemId, success, result='error'):
        return {'type': itemType,
         'id': itemId,
         'success': success,
         'result': result}

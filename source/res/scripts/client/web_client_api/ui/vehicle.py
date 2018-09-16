# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/vehicle.py
from itertools import groupby
from types import NoneType
from logging import getLogger
from constants import NC_MESSAGE_PRIORITY
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import getCDFromId
from gui.Scaleform.locale.W2C import W2C
from gui.shared import event_dispatcher
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from helpers import dependency, i18n
from helpers.time_utils import getTimestampFromISO, getDateTimeInUTC, utcToLocalDatetime, getDateTimeInLocal
from items import ITEM_TYPES
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
from web_client_api import W2CSchema, Field, w2c
from soft_exception import SoftException
from web_client_api.common import ItemPackType, CompensationType, CompensationSpec, ItemPackTypeGroup, ItemPackEntry
_logger = getLogger(__name__)
REQUIRED_ITEM_FIELDS = {'type',
 'id',
 'count',
 'groupID'}
REQUIRED_COMPENSATION_FIELDS = {'type', 'value', 'count'}

class _ItemPackValidationError(SoftException):
    pass


class _ItemPackEntry(ItemPackEntry):

    def replace(self, values):
        return self._replace(**values)


def _validateItemsPack(items):
    _validateItemsRequiredFields(items)
    _validateItemsPackTypes(items)
    _validateItemsCompensationRequiredFields(items)
    _validateItemsCompensation(items)
    return True


def _validateItemsRequiredFields(items):
    if not all((REQUIRED_ITEM_FIELDS.issubset(item) for item in items)):
        raise SoftException('Invalid item preview spec')


def _validateItemsPackTypes(items):
    validTypes = {v for _, v in ItemPackType.getIterator()}
    specTypes = {item['type'] for item in items}
    invalidTypes = specTypes - validTypes
    if invalidTypes:
        raise _ItemPackValidationError('Unexpected item types {}, valid type identifiers: {}'.format(', '.join(invalidTypes), ', '.join(validTypes)))


def _validateItemsCompensationRequiredFields(items):
    for item in items:
        if 'compensation' in item:
            for compensationSpec in item['compensation']:
                if not REQUIRED_COMPENSATION_FIELDS.issubset(compensationSpec):
                    raise SoftException('Invalid compensation spec')
                if not CompensationType.hasValue(compensationSpec['type']):
                    raise SoftException('Unsupported compensation type "{}"'.format(compensationSpec['type']))


def _validateItemsCompensation(items):
    for _, groups in groupby(sorted(items, key=_getItemKey), key=_getItemKey):
        group = list(groups)
        if len(group) > 1:
            item = group[0]
            for i in range(1, len(group)):
                if not _equalsCompensations(item, group[i]):
                    raise SoftException("Compensations isn't equals")


def _getItemKey(item):
    return (item['id'], item['type'])


def _equalsCompensations(itemA, itemB):
    compKey = 'compensation'
    itemAHasComp = compKey in itemA
    itemBHasComp = compKey in itemB
    if not itemAHasComp and not itemBHasComp:
        return True
    if itemAHasComp and itemBHasComp:
        compensationsA = itemA[compKey]
        compensationsB = itemB[compKey]
        if len(compensationsA) != len(compensationsB):
            return False
        for compA, compB in zip(compensationsA, compensationsB):
            if compA['type'] != compB['type']:
                return False
            compAValue = compA['value']
            compBValue = compB['value']
            for currency in Currency.ALL:
                if currency in compAValue:
                    if currency not in compBValue:
                        return False
                    if compAValue[currency] != compBValue[currency]:
                        return False

        return True
    return False


def _parseItemsPack(items):
    specList = items
    result = []
    for spec in specList:
        spec['type'] = str(spec['type'])
        tempId = spec.pop('id')
        itemId = getCDFromId(spec['type'], tempId)
        if 'compensation' in spec:
            compensations = []
            for compensationSpec in spec['compensation']:
                compensations.append(CompensationSpec(**compensationSpec))

            tempComp = spec.pop('compensation')
            result.append(_ItemPackEntry(id=itemId, compensation=compensations, **spec))
            spec['compensation'] = tempComp
        else:
            result.append(_ItemPackEntry(id=itemId, **spec))
        spec['id'] = tempId

    return result


def _parseBuyPrice(buyPrice):
    buyPrice = buyPrice.copy()
    discount = buyPrice.pop('discount', None)
    return (Money(**buyPrice), MONEY_UNDEFINED) if discount is None else (Money(**discount), Money(**buyPrice))


class _VehicleSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)


def _buyPriceValidator(value):
    value = value.copy()

    def __validatePrice(tData, errorStr=''):
        for pKey, pValue in tData.iteritems():
            if pValue is not None:
                if isinstance(pValue, dict):
                    __validatePrice(pValue, 'Field "{}". '.format(pKey))
                elif not isinstance(pValue, int):
                    errorStr = '{}Incorrect type of "{}" price value. Int type expected!'.format(errorStr, pKey)
                    raise SoftException(errorStr)

        return

    __validatePrice(value)
    value.pop('discount', None)
    return Money(**value).isDefined()


class _VehiclePreviewSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)
    back_url = Field(required=False, type=basestring)


class _VehiclePackPreviewSchema(W2CSchema):
    title = Field(required=True, type=basestring)
    end_date = Field(required=False, type=basestring)
    buy_price = Field(required=True, type=dict, validator=lambda value, _: _buyPriceValidator(value))
    items = Field(required=True, type=(list, NoneType), validator=lambda value, _: _validateItemsPack(value))
    back_url = Field(required=False, type=basestring)
    buy_params = Field(required=False, type=dict)


class VehicleSellWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_VehicleSchema, 'vehicle_sell')
    def vehicleSellDialog(self, cmd):
        item = self.itemsCache.items.getItemByCD(cmd.vehicle_id)
        if item.isInInventory and item.itemTypeID == ITEM_TYPES.vehicle:
            event_dispatcher.showVehicleSellDialog(int(item.invID))


class VehicleCompareWebApiMixin(object):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    @w2c(_VehicleSchema, 'vehicle_add_to_comparison')
    def addVehicleToCompare(self, cmd):
        self.comparisonBasket.addVehicle(cmd.vehicle_id)

    @w2c(W2CSchema, 'get_comparison_basket')
    def getVehicleComparisonBasket(self, cmd):
        return {'basketMaxCount': self.comparisonBasket.maxVehiclesToCompare,
         'basketContents': self.comparisonBasket.getVehiclesCDs()}


class VehicleComparisonBasketWebApiMixin(object):

    @w2c(W2CSchema, 'comparison_basket')
    def openVehicleComparisonBasket(self, _):
        event_dispatcher.showVehicleCompare()


def _pushInvalidPreviewMessage():
    SystemMessages.pushMessage(i18n.makeString(W2C.ERROR_INVALIDPREVIEWVEHICLE), SystemMessages.SM_TYPE.Error, NC_MESSAGE_PRIORITY.MEDIUM)


class VehiclePreviewWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_VehiclePreviewSchema, 'vehicle_preview')
    def openVehiclePreview(self, cmd):
        vehicleID = cmd.vehicle_id
        if self.__validVehiclePreview(vehicleID):
            event_dispatcher.showVehiclePreview(vehTypeCompDescr=vehicleID, previewAlias=self._getVehiclePreviewReturnAlias(cmd), previewBackCb=self._getVehiclePreviewReturnCallback(cmd))
        else:
            _pushInvalidPreviewMessage()

    @w2c(_VehiclePackPreviewSchema, 'vehicle_pack_preview')
    def openVehiclePackPreview(self, cmd):
        items = _parseItemsPack(cmd.items)
        price, oldPrice = _parseBuyPrice(cmd.buy_price)
        vehiclesID = []
        for item in items:
            if item.type in ItemPackTypeGroup.VEHICLE:
                vehiclesID.append(item.id)

        if vehiclesID and self.__validVehiclePreviewPack(vehiclesID):
            localEndTime = None
            if cmd.end_date:
                timestamp = getTimestampFromISO(cmd.end_date)
                datetimeInUTC = getDateTimeInUTC(timestamp)
                localDatetime = utcToLocalDatetime(datetimeInUTC)
                localEndTime = (localDatetime - getDateTimeInLocal(0)).total_seconds()
            event_dispatcher.showVehiclePreview(vehTypeCompDescr=vehiclesID[0], itemsPack=items, price=price, oldPrice=oldPrice, title=cmd.title, endTime=localEndTime, previewAlias=self._getVehiclePreviewReturnAlias(cmd), previewBackCb=self._getVehiclePreviewReturnCallback(cmd), buyParams=cmd.buy_params)
        else:
            _pushInvalidPreviewMessage()
        return

    def _getVehiclePreviewReturnCallback(self, cmd):
        return None

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.LOBBY_HANGAR

    def __validVehiclePreview(self, intCD):
        vehicle = None
        try:
            vehicle = self.itemsCache.items.getStockVehicle(intCD, useInventory=True)
        except Exception:
            pass

        if not vehicle:
            LOG_ERROR("Couldn't find vehicle intCD={}".format(intCD))
            return False
        else:
            return True

    def __validVehiclePreviewPack(self, vehiclesID):
        for vehID in vehiclesID:
            if not self.__validVehiclePreview(vehID):
                return False

        return True

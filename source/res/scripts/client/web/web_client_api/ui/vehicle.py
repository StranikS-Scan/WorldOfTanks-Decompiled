# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/vehicle.py
import random
from itertools import groupby
from types import NoneType
from logging import getLogger
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import STYLE_PREVIEW_VEHICLES_POOL
from constants import NC_MESSAGE_PRIORITY
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.items_kit_helper import getCDFromId, canInstallStyle
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import checkIfVehicleIsHidden
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.customization.shared import C11nId, SEASON_TYPE_TO_IDX
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showStylePreview, showHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.outfit import Area
from gui.shared.money import Money, MONEY_UNDEFINED, Currency
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.time_utils import getCurrentLocalServerTimestamp, getTimeStructInLocal
from helpers.time_utils import getTimestampFromISO, getDateTimeInUTC, utcToLocalDatetime, getDateTimeInLocal
from items import ITEM_TYPES, vehicles
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IVehicleComparisonBasket, IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import W2CSchema, Field, w2c
from soft_exception import SoftException
from web.web_client_api.common import ItemPackType, CompensationType, CompensationSpec, ItemPackTypeGroup
from web.web_client_api.common import ItemPackEntry, VehicleOfferEntry
_logger = getLogger(__name__)
REQUIRED_ITEM_FIELDS = {'type',
 'id',
 'count',
 'groupID'}
REQUIRED_COMPENSATION_FIELDS = {'type', 'value'}
REQUIRED_CUSTOMCREW_FIELDS = {'extra'}
REQUIRED_TANKMAN_FIELDS = {'isPremium',
 'role',
 'roleLevel',
 'gId',
 'nationID',
 'vehicleTypeID'}
DEFAULT_STYLED_VEHICLES = (15697, 6193, 19969, 3937)

class _ItemPackValidationError(SoftException):
    pass


class _ItemPackEntry(ItemPackEntry):

    def replace(self, values):
        return self._replace(**values)


class _VehicleOfferEntry(VehicleOfferEntry):

    def replace(self, values):
        return self._replace(**values)


def _doesVehicleCDExist(vehicleCD):
    itemTypeID, nationID, innationID = vehicles.parseIntCompactDescr(vehicleCD)
    if itemTypeID == GUI_ITEM_TYPE.VEHICLE and innationID in vehicles.g_list.getList(nationID):
        return True
    raise SoftException('Invalid vehicle CD: %d' % vehicleCD)


def _validateVehiclesCDList(vehiclesCDs):
    return all((_doesVehicleCDExist(vehicleCD) for vehicleCD in vehiclesCDs))


def _validateItemsPack(items):
    _validateItemsRequiredFields(items)
    _validateItemsPackTypes(items)
    _validateItemsCompensationRequiredFields(items)
    _validateItemsCustomCrewRequiredFields(items)
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


def _validateItemsCustomCrewRequiredFields(items):
    for item in items:
        if item['type'] == ItemPackType.CREW_CUSTOM:
            if not REQUIRED_CUSTOMCREW_FIELDS.issubset(item):
                raise SoftException('Invalid custom crew spec')
            if 'tankmen' not in item['extra']:
                raise SoftException('Invalid custom crew extra spec')
            if not all([ REQUIRED_TANKMAN_FIELDS.issubset(tankman) for tankman in item['extra']['tankmen'] ]):
                raise SoftException('Invalid custom crew tankman spec')


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


def _parseOffers(offers):
    return [ _VehicleOfferEntry(id=_getOfferID(offer) or str(ndx), eventType=offer.get('event_type'), rent=offer.get('rent'), crew=_getOfferCrew(offer), name=_getOfferStr(offer, VEHICLE_PREVIEW.getOfferName), label=_getOfferStr(offer, VEHICLE_PREVIEW.getOfferLabel), left=_getRentLeft(offer), buyPrice=Money(**offer.get('buy_price', MONEY_UNDEFINED)), bestOffer=offer.get('best_offer'), buyParams=offer.get('buy_params'), preferred=bool(offer.get('preferred', False))) for ndx, offer in enumerate(offers) ]


def _getOfferID(offer):
    buyParams = offer.get('buy_params')
    return buyParams.get('transactionID') if buyParams else None


@dependency.replace_none_kwargs(epicCtrl=IEpicBattleMetaGameController)
def _getOfferStr(offer, getKey, epicCtrl=None):
    key, values = _parseRent(offer)
    if key == 'cycle':
        indexes = str(epicCtrl.getCycleOrdinalNumber(first(values)))
    elif key == 'cycles':
        indexes = [ epicCtrl.getCycleOrdinalNumber(value) for value in values ]
        indexes = '{}-{}'.format(min(indexes), max(indexes))
    else:
        _, endTimestamp = epicCtrl.getSeasonTimeRange()
        indexes = str(getTimeStructInLocal(endTimestamp).tm_year)
    return _ms(key=getKey(key), value=indexes)


@dependency.replace_none_kwargs(epicCtrl=IEpicBattleMetaGameController)
def _getRentLeft(offer, epicCtrl=None):
    key, values = _parseRent(offer)
    value = max(values)
    currentTimestamp = getCurrentLocalServerTimestamp()
    season = epicCtrl.getCurrentSeason()
    if season:
        if key == 'season':
            lastCycle = season.getLastCycleInfo()
            endDate = season.getEndDate() if lastCycle else 0
        elif key in ('cycle', 'cycles'):
            lastCycle = season.getCycleInfo(value)
            endDate = lastCycle.endDate if lastCycle else 0
        else:
            lastCycle = None
            endDate = 0
        if lastCycle is not None:
            currentCycle = season.getCycleInfo()
            if currentCycle is not None:
                cyclesLeft = lastCycle.ordinalNumber + 1 - currentCycle.ordinalNumber
                timeLeft = endDate - currentTimestamp
                return (cyclesLeft, timeLeft if timeLeft >= 0 else 0)
    return (0, 0)


def _parseRent(offer):
    rentInfo = offer.get('rent')
    if rentInfo:
        if len(rentInfo) > 1:
            key = 'cycles'
            values = (int(rent['cycle']) for rent in rentInfo)
        else:
            key, value = first(rentInfo).iteritems().next()
            values = (int(value),)
        return (key, values)
    raise SoftException('invalid rent collection')


def _getOfferCrew(offer):
    return ItemPackEntry(type=ItemPackType.CREW_100 if Money(**offer.get('buy_price', MONEY_UNDEFINED)).gold else ItemPackType.CREW_75, groupID=1)


def _parseBuyPrice(buyPrice):
    buyPrice = buyPrice.copy()
    discount = buyPrice.pop('discount', None)
    return (Money(**buyPrice), MONEY_UNDEFINED) if discount is None else (Money(**discount), Money(**buyPrice))


class _VehicleSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)


def _buyPriceValidator(value):
    value = value.copy()
    _validatePrice(value)
    value.pop('discount', None)
    return Money(**value).isDefined()


def _validatePrice(tData, errorStr=''):
    for pKey, pValue in tData.iteritems():
        if pValue is not None:
            if isinstance(pValue, dict):
                _validatePrice(pValue, 'Field "{}". '.format(pKey))
            elif not isinstance(pValue, int):
                errorStr = '{}Incorrect type of "{}" price value. Int type expected!'.format(errorStr, pKey)
                raise SoftException(errorStr)

    return


class _VehiclePreviewSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)
    back_url = Field(required=False, type=basestring)


class _VehicleOffersPreviewSchema(W2CSchema):
    vehicle_id = Field(required=True, type=int)
    offers = Field(required=True, type=(list, NoneType))
    buy_params = Field(required=False, type=dict)
    back_url = Field(required=False, type=basestring)


class _VehiclePackPreviewSchema(W2CSchema):
    title = Field(required=True, type=basestring)
    end_date = Field(required=False, type=basestring)
    buy_price = Field(required=True, type=dict, validator=lambda value, _: _buyPriceValidator(value))
    items = Field(required=True, type=(list, NoneType), validator=lambda value, _: _validateItemsPack(value))
    back_url = Field(required=False, type=basestring)
    buy_params = Field(required=False, type=dict)


class _MarathonVehiclePackPreviewSchema(W2CSchema):
    title = Field(required=True, type=basestring)
    items = Field(required=True, type=(list, NoneType), validator=lambda value, _: _validateItemsPack(value))
    marathon_prefix = Field(required=True, type=basestring)


class _VehicleStylePreviewSchema(W2CSchema):
    vehicle_cd = Field(required=False, type=int)
    style_id = Field(required=True, type=int)
    back_btn_descr = Field(required=True, type=basestring)
    back_url = Field(required=False, type=basestring)


class _VehicleListStylePreviewSchema(W2CSchema):
    style_id = Field(required=True, type=int)
    vehicle_min_level = Field(required=False, type=int, default=10)
    vehicle_list = Field(required=False, type=(list, NoneType), validator=lambda value, _: _validateVehiclesCDList(value), default=DEFAULT_STYLED_VEHICLES)
    back_btn_descr = Field(required=True, type=basestring)
    back_url = Field(required=False, type=basestring)


class _VehicleCustomizationPreviewSchema(W2CSchema):
    style_id = Field(required=True, type=int)


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
    SystemMessages.pushMessage(backport.text(R.strings.w2c.error.invalidPreviewVehicle()), SystemMessages.SM_TYPE.Error, NC_MESSAGE_PRIORITY.MEDIUM)


class VehiclePreviewWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)
    c11n = dependency.descriptor(ICustomizationService)

    @w2c(_VehiclePreviewSchema, 'vehicle_preview')
    def openVehiclePreview(self, cmd):
        vehicleID = cmd.vehicle_id
        if self.__validVehiclePreview(vehicleID):
            event_dispatcher.showVehiclePreview(vehTypeCompDescr=vehicleID, previewAlias=self._getVehiclePreviewReturnAlias(cmd), previewBackCb=self._getVehiclePreviewReturnCallback(cmd))
        else:
            _pushInvalidPreviewMessage()

    @w2c(_VehiclePreviewSchema, 'vehicle_frontline_preview')
    def openFrontLineVehiclePreview(self, cmd):
        vehicleID = cmd.vehicle_id
        if self.__validVehiclePreview(vehicleID):
            if not checkIfVehicleIsHidden(vehicleID):
                event_dispatcher.showVehiclePreview(vehTypeCompDescr=vehicleID, previewAlias=cmd.back_url, previewBackCb=self._getVehiclePreviewReturnCallback(cmd), isFrontline=True)
        else:
            _pushInvalidPreviewMessage()

    @w2c(_VehicleOffersPreviewSchema, 'vehicle_offers_preview')
    def openVehicleOffersPreview(self, cmd):
        event_dispatcher.showVehiclePreview(vehTypeCompDescr=int(cmd.vehicle_id), offers=_parseOffers(cmd.offers), price=MONEY_UNDEFINED, oldPrice=MONEY_UNDEFINED, previewAlias=self._getVehiclePreviewReturnAlias(cmd), previewBackCb=self._getVehiclePreviewReturnCallback(cmd))

    @w2c(_MarathonVehiclePackPreviewSchema, 'marathon_vehicle_pack_preview')
    def openMarathonVehiclePackPreview(self, cmd):
        items = _parseItemsPack(cmd.items)
        vehiclesIDs = self.__getVehiclesIDs(items)
        if vehiclesIDs:
            event_dispatcher.showMarathonVehiclePreview(vehTypeCompDescr=vehiclesIDs[0], itemsPack=items, title=cmd.title, marathonPrefix=cmd.marathon_prefix)
        else:
            _pushInvalidPreviewMessage()

    @w2c(_VehiclePackPreviewSchema, 'vehicle_pack_preview')
    def openVehiclePackPreview(self, cmd):
        items = _parseItemsPack(cmd.items)
        price, oldPrice = _parseBuyPrice(cmd.buy_price)
        vehiclesIDs = self.__getVehiclesIDs(items)
        if vehiclesIDs:
            localEndTime = None
            if cmd.end_date:
                timestamp = getTimestampFromISO(cmd.end_date)
                datetimeInUTC = getDateTimeInUTC(timestamp)
                localDatetime = utcToLocalDatetime(datetimeInUTC)
                localEndTime = (localDatetime - getDateTimeInLocal(0)).total_seconds()
            event_dispatcher.showVehiclePreview(vehTypeCompDescr=vehiclesIDs[0], itemsPack=items, price=price, oldPrice=oldPrice, title=cmd.title, endTime=localEndTime, previewAlias=self._getVehiclePreviewReturnAlias(cmd), previewBackCb=self._getVehiclePreviewReturnCallback(cmd), buyParams=cmd.buy_params)
        else:
            _pushInvalidPreviewMessage()
        return

    @w2c(_VehicleStylePreviewSchema, 'vehicle_style_preview')
    def openVehicleStylePreview(self, cmd):
        if cmd.vehicle_cd:
            return self._showStylePreview(cmd.vehicle_cd, cmd)
        styledVehicleCD = self.__getStyledVehicleCD(cmd.style_id)
        return False if not styledVehicleCD else self._showStylePreview(styledVehicleCD, cmd)

    @w2c(_VehicleListStylePreviewSchema, 'vehicle_list_style_preview')
    def openVehicleListStylePreview(self, cmd):
        styledVehicleCD = None
        if g_currentVehicle.isPresent() and g_currentVehicle.item.level >= cmd.vehicle_min_level:
            styledVehicleCD = g_currentVehicle.item.intCD
        else:
            accDossier = self.itemsCache.items.getAccountDossier()
            vehiclesStats = accDossier.getRandomStats().getVehicles()
            vehicleGetter = self.itemsCache.items.getItemByCD
            vehiclesStats = {vehicle:value for vehicle, value in vehiclesStats.iteritems() if vehicleGetter(vehicle).level >= cmd.vehicle_min_level}
            if vehiclesStats:
                sortedVehicles = sorted(vehiclesStats.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
                styledVehicleCD = sortedVehicles[0][0]
            if not styledVehicleCD:
                vehiclesPool = AccountSettings.getSettings(STYLE_PREVIEW_VEHICLES_POOL)
                if not vehiclesPool or set(vehiclesPool) != set(cmd.vehicle_list):
                    vehiclesPool = list(cmd.vehicle_list)
                styledVehicleCD = vehiclesPool.pop(0)
                vehiclesPool.append(styledVehicleCD)
                AccountSettings.setSettings(STYLE_PREVIEW_VEHICLES_POOL, vehiclesPool)
        self._showStylePreview(styledVehicleCD, cmd)
        return

    @w2c(_VehicleCustomizationPreviewSchema, 'vehicle_customization_preview')
    def openVehicleCustomizationPreview(self, cmd):
        result = canInstallStyle(cmd.style_id)
        if not result.canInstall:
            return {'installed': result.canInstall}

        def styleCallback():
            if result.style is not None:
                self.c11n.getCtx().switchToStyle()
                season = SEASON_TYPE_TO_IDX[self.c11n.getCtx().currentSeason]
                styleSlot = C11nId(areaId=Area.MISC, slotType=GUI_ITEM_TYPE.STYLE, regionIdx=0)
                self.c11n.getCtx().installItem(result.style.intCD, styleSlot, season)
            return

        self.c11n.showCustomization(result.vehicle.invID, callback=styleCallback)
        return {'installed': result.canInstall}

    def __getStyledVehicleCD(self, styleId):
        styledVehicleCD = None
        style = self.c11n.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
        vehicle = g_currentVehicle.item if g_currentVehicle.isPresent() else None
        if vehicle is not None and style.mayInstall(vehicle):
            styledVehicleCD = vehicle.intCD
        else:
            accDossier = self.itemsCache.items.getAccountDossier()
            vehiclesStats = accDossier.getRandomStats().getVehicles()
            vehicleGetter = self.itemsCache.items.getItemByCD
            vehiclesStats = {vehicleCD:value for vehicleCD, value in vehiclesStats.iteritems() if style.mayInstall(vehicleGetter(vehicleCD))}
            if vehiclesStats:
                sortedVehicles = sorted(vehiclesStats.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
                styledVehicleCD = sortedVehicles[0][0] if sortedVehicles else None
            if not styledVehicleCD:
                criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.FOR_ITEM(style)
                vehicle = first(self.__getVehiclesForStylePreview(criteria=criteria))
                styledVehicleCD = vehicle.intCD if vehicle else None
            if not styledVehicleCD:
                criteria = ~REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.EVENT | REQ_CRITERIA.VEHICLE.FOR_ITEM(style)
                vehicle = random.choice(self.__getVehiclesForStylePreview(criteria=criteria))
                styledVehicleCD = vehicle.intCD if vehicle else None
        return styledVehicleCD

    def __getVehiclesForStylePreview(self, criteria=None):
        vehs = self.itemsCache.items.getVehicles(criteria=criteria).values()
        return sorted(vehs, key=lambda item: item.level, reverse=True)

    def _getVehicleStylePreviewCallback(self, cmd):
        return showHangar

    def _getVehiclePreviewReturnCallback(self, cmd):
        return None

    def _getVehiclePreviewReturnAlias(self, cmd):
        return VIEW_ALIAS.LOBBY_HANGAR

    def _showStylePreview(self, vehicleCD, cmd):
        style = self.c11n.getItemByID(GUI_ITEM_TYPE.STYLE, cmd.style_id)
        vehicle = self.itemsCache.items.getItemByCD(vehicleCD)
        if vehicle is not None and style.mayInstall(vehicle):
            showStylePreview(vehicleCD, style, style.getDescription(), self._getVehicleStylePreviewCallback(cmd), backBtnDescrLabel=backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.dyn(cmd.back_btn_descr)()))
            return True
        else:
            return False

    def __getVehiclesIDs(self, items):
        vehiclesIDs = [ item.id for item in items if item.type in ItemPackTypeGroup.VEHICLE ]
        return vehiclesIDs if vehiclesIDs and self.__validVehiclePreviewPack(vehiclesIDs) else None

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

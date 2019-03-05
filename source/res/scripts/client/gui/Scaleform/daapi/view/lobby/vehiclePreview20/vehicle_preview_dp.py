# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/vehicle_preview_dp.py
import logging
import BigWorld
import nations
from gui.Scaleform import MENU
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.formatters.currency import getStyle, getBWFormatter
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, func_utils
from helpers.i18n import makeString as _ms
from helpers.time_utils import getTillTimeString
from items_kit_helper import getCompensateItemsCount, getDataOneVehicle, getDataMultiVehicles, collapseItemsPack
from skeletons.gui.shared import IItemsCache
from web_client_api.common import CompensationType, ItemPackTypeGroup
_logger = logging.getLogger(__name__)
_CUSTOM_OFFER_ACTION_PERCENT = 100

def _createVehicleVO(rawItem, itemsCache):
    vehicle = itemsCache.items.getStockVehicle(rawItem.id, useInventory=True)
    if vehicle is not None:
        icon = func_utils.makeFlashPath(vehicle.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL))
        cd = vehicle.intCD
        label = vehicle.shortUserName
        nation = vehicle.nationID
    else:
        icon = rawItem.iconSource
        cd = 0
        label = ''
        nation = nations.NONE_INDEX
    return {'icon': icon,
     'iconAlt': RES_ICONS.MAPS_ICONS_LIBRARY_VEHICLE_DEFAULT,
     'intCD': cd,
     'label': label,
     'nation': nation,
     'hasCompensation': getCompensateItemsCount(rawItem, itemsCache) > 0,
     'level': RES_ICONS.getLevelIcon(vehicle.level),
     'tankType': Vehicle.getTypeSmallIconPath(vehicle.type, vehicle.isElite)}


def _createOfferVO(offer, setActive=False):
    return {'id': offer.id,
     'label': offer.label,
     'active': setActive,
     'tooltipData': makeTooltip(header=offer.name, body=_ms(**_getRentTooltipData(offer)))}


def _getRentTooltipData(offer):
    rents = offer.rent
    if rents:
        seasons = [ rent['season'] for rent in rents if rent.get('season') ]
        cycles = [ rent['cycle'] for rent in rents if rent.get('cycle') ]
        cyclesLeft, timeLeft = offer.left
        if seasons or len(cycles) > 1:
            key = backport.text(R.strings.vehicle_preview.buyingPanel.offer.rent.frontline.tooltip.body.cyclesLeft())
            value = str(cyclesLeft)
        else:
            key = backport.text(R.strings.vehicle_preview.buyingPanel.offer.rent.frontline.tooltip.body.timeLeft())
            value = getTillTimeString(timeLeft, MENU.TIME_TIMEVALUE)
        return {'key': key,
         'value': text_styles.stats(value)}
    else:
        return None


def _vehicleComparisonKey(vehicle):
    return (tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
     vehicle.level,
     GUI_NATIONS_ORDER_INDEX_REVERSED[vehicle.nationName],
     vehicle.intCD)


class IVehPreviewDataProvider(object):

    def getBuyType(self, vehicle):
        raise NotImplementedError

    def getBuyingPanelData(self, item, data=None, isHeroTank=False, itemsPack=None):
        raise NotImplementedError


class DefaultVehPreviewDataProvider(IVehPreviewDataProvider):
    __itemsCache = dependency.descriptor(IItemsCache)

    def getBuyType(self, vehicle):
        return factory.BUY_VEHICLE if vehicle.isUnlocked else factory.UNLOCK_ITEM

    def getBuyingPanelData(self, item, data=None, isHeroTank=False, itemsPack=None):
        isBuyingAvailable = not isHeroTank and (not item.isHidden or item.isRentable or item.isRestorePossible())
        uniqueVehicleTitle = ''
        buyingLabel = ''
        if isBuyingAvailable or isHeroTank:
            if item.canTradeIn:
                buyingLabel = text_styles.main(backport.text(R.strings.vehicle_preview.buyingPanel.tradeInLabel()))
        else:
            uniqueVehicleTitle = text_styles.tutorial(backport.text(R.strings.vehicle_preview.buyingPanel.uniqueVehicleLabel()))
        compensationData = self.__getCompensationData(itemsPack)
        resultVO = {'setTitle': data.title,
         'uniqueVehicleTitle': uniqueVehicleTitle,
         'buyingLabel': buyingLabel,
         'vehicleId': item.intCD,
         'isCanTrade': item.canTradeIn,
         'isBuyingAvailable': isBuyingAvailable,
         'isMoneyEnough': data.isMoneyEnough,
         'buyButtonEnabled': data.enabled,
         'buyButtonLabel': data.label,
         'buyButtonTooltip': data.tooltip,
         'itemPrice': data.itemPrice,
         'isUnlock': data.isUnlock,
         'showAction': data.isAction,
         'hasCompensation': compensationData is not None,
         'compensation': compensationData if compensationData is not None else {},
         'showCannotResearchWarning': data.isUnlock and not data.isPrevItemsUnlock}
        customOfferData = self.__getCustomOfferData(data)
        if customOfferData is not None:
            resultVO.update({'customOffer': customOfferData})
        return resultVO

    def getItemPackBuyingPanelData(self, item, data=None, itemsPack=None):
        compensationData = self.__getCompensationData(itemsPack)
        return {'setTitle': data.title,
         'uniqueVehicleTitle': '',
         'buyingLabel': '',
         'vehicleId': 0,
         'isCanTrade': False,
         'isBuyingAvailable': True,
         'isMoneyEnough': data.enabled,
         'buyButtonEnabled': data.enabled,
         'buyButtonLabel': data.label,
         'buyButtonTooltip': data.tooltip,
         'itemPrice': data.itemPrice,
         'isUnlock': False,
         'showAction': data.isAction,
         'hasCompensation': compensationData is not None,
         'compensation': compensationData if compensationData is not None else {},
         'showCannotResearchWarning': False}

    def getOffersBuyingPanelData(self, data):
        return {'setTitle': data.title,
         'uniqueVehicleTitle': '',
         'buyingLabel': '',
         'vehicleId': 0,
         'isCanTrade': False,
         'isBuyingAvailable': True,
         'isMoneyEnough': data.enabled,
         'buyButtonEnabled': data.enabled,
         'buyButtonLabel': data.label,
         'buyButtonTooltip': data.tooltip,
         'itemPrice': data.itemPrice,
         'showAction': data.isAction,
         'actionTooltip': data.actionTooltip,
         'hasCompensation': False,
         'compensation': {},
         'showCannotResearchWarning': False}

    def getOffersData(self, offers, activeID):
        return [ _createOfferVO(offer, offer.id == activeID) for offer in offers ]

    @staticmethod
    def separateItemsPack(packItems):
        ordinaryItems = []
        vehiclesItems = []
        if packItems:
            for item in packItems:
                if item.type in ItemPackTypeGroup.VEHICLE:
                    vehiclesItems.append(item)
                ordinaryItems.append(item)

        return (vehiclesItems, ordinaryItems)

    def getItemsPackData(self, vehicle, items, vehicleItems):
        vehiclesCount = len(vehicleItems)
        if vehiclesCount == 0:
            _logger.error('No any vehicle in the pack.')
            return ([], [], [])
        collapsedItemsVOs = getDataMultiVehicles(items, vehicle) if items else []
        if vehiclesCount == 1:
            vehiclesVOs = []
            itemsVOs = getDataOneVehicle(items, vehicle, vehicleItems[0].groupID)
        else:
            getVehicle = self.__itemsCache.items.getStockVehicle
            vehicleItems = sorted(vehicleItems, key=lambda veh: _vehicleComparisonKey(getVehicle(veh.id, useInventory=True)), reverse=True)
            vehiclesVOs = [ _createVehicleVO(packedVeh, self.__itemsCache) for packedVeh in vehicleItems ]
            itemsVOs = collapsedItemsVOs
        return (vehiclesVOs, itemsVOs, collapsedItemsVOs)

    def __getCompensationData(self, itemsPack):
        compensationMoney = MONEY_UNDEFINED
        if itemsPack is not None:
            for item in collapseItemsPack(itemsPack):
                compensateItemsCount = getCompensateItemsCount(item, self.__itemsCache)
                if compensateItemsCount > 0:
                    for compensation in item.compensation:
                        if compensation.type == CompensationType.MONEY:
                            compensationMoney += Money(**compensation.value) * compensateItemsCount

        if compensationMoney.isDefined():
            currency = compensationMoney.getCurrency()
            val = compensationMoney.get(currency)
            if val is not None:
                return self.__packCompensation(val, currency)
        return

    @staticmethod
    def __packCompensation(value, currency):
        isGold = currency == Currency.GOLD
        currencyFormatter = getBWFormatter(currency)
        currencyStyle = getStyle(currency)
        iconInfo = RES_ICONS.MAPS_ICONS_LIBRARY_INFO_YELLOW if isGold else RES_ICONS.MAPS_ICONS_LIBRARY_INFO
        return {'value': currencyStyle('-{}'.format(currencyStyle(currencyFormatter(value)))),
         'tooltip': makeTooltip(body=backport.text(R.strings.vehicle_preview.buyingPanel.compensation.body())),
         'iconInfo': iconInfo}

    @staticmethod
    def __getCustomOfferData(data):
        for price in data.itemPrice:
            actions = price.get('action')
            if not actions:
                return None
            for action in actions:
                actionType, actionValue = action
                if actionValue == _CUSTOM_OFFER_ACTION_PERCENT:
                    return {'name': backport.text(R.strings.vehicle_preview.buyingPanel.customOffer.buy()) if actionType in Currency.ALL else backport.text(R.strings.vehicle_preview.buyingPanel.customOffer.research()),
                     'value': '{}%'.format(BigWorld.wg_getIntegralFormat(actionValue))}

        return None

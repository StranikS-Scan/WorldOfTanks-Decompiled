# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/vehicle_preview_dp.py
import logging
import nations
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.shared.formatters import text_styles
from gui.shared.formatters.currency import getStyle, getBWFormatter
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from web_client_api.common import CompensationType
from items_kit_helper import getCompensateItemsCount, getDataOneVehicle, getDataMultiVehicles, collapseItemsPack
from gui import GUI_NATIONS_ORDER_INDEX_REVERSED
_logger = logging.getLogger(__name__)

def _createVehicleVO(rawItem, itemsCache):
    vehicle = itemsCache.items.getStockVehicle(rawItem.id, useInventory=True)
    if vehicle is not None:
        icon = vehicle.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL)
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
    itemsCache = dependency.descriptor(IItemsCache)

    def getBuyType(self, vehicle):
        return factory.BUY_VEHICLE if vehicle.isUnlocked else factory.UNLOCK_ITEM

    def getBuyingPanelData(self, item, data=None, isHeroTank=False, itemsPack=None):
        isBuyingAvailable = not isHeroTank and (not item.isHidden or item.isRentable or item.isRestorePossible())
        isAction = data.action is not None
        uniqueVehicleTitle = ''
        buyingLabel = ''
        if isBuyingAvailable or isHeroTank:
            if item.canTradeIn:
                buyingLabel = text_styles.main(VEHICLE_PREVIEW.BUYINGPANEL_TRADEINLABEL)
        else:
            uniqueVehicleTitle = text_styles.tutorial(VEHICLE_PREVIEW.BUYINGPANEL_UNIQUEVEHICLELABEL)
        compensationData = self.__getCompensationData(itemsPack)
        return {'setTitle': data.title,
         'uniqueVehicleTitle': uniqueVehicleTitle,
         'buyingLabel': buyingLabel,
         'vehicleId': item.intCD,
         'isCanTrade': item.canTradeIn,
         'isBuyingAvailable': isBuyingAvailable,
         'isMoneyEnough': data.enabled,
         'buyButtonEnabled': data.enabled,
         'buyButtonLabel': data.label,
         'buyButtonTooltip': data.tooltip,
         'price': data.price,
         'showGlow': isHeroTank or item.isPremium and (not item.isHidden or item.isRentable or item.isRestorePossible()),
         'showAction': isAction,
         'actionTooltipType': TOOLTIPS_CONSTANTS.ACTION_PRICE if isAction else None,
         'actionData': data.action,
         'hasCompensation': compensationData is not None,
         'compensation': compensationData if compensationData is not None else {},
         'showCannotResearchWarning': not item.isUnlocked}

    def getItemPackBuyingPanelData(self, item, data=None, itemsPack=None):
        isAction = data.action is not None
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
         'price': data.price,
         'showGlow': True,
         'showAction': isAction,
         'actionTooltipType': TOOLTIPS_CONSTANTS.ACTION_PRICE if isAction else None,
         'actionData': data.action,
         'hasCompensation': compensationData is not None,
         'compensation': compensationData if compensationData is not None else {},
         'showCannotResearchWarning': False}

    def getItemsPackData(self, vehicle, items, vehicleItems):
        vehiclesCount = len(vehicleItems)
        if vehiclesCount == 0:
            _logger.error('No any vehicle in the pack.')
            return ([], [])
        else:
            if vehiclesCount == 1:
                vehiclesVOs = []
                itemsVOs = getDataOneVehicle(items, vehicle, vehicleItems[0].groupID)
            else:
                getVehicle = self.itemsCache.items.getStockVehicle
                vehicleItems = sorted(vehicleItems, key=lambda veh: _vehicleComparisonKey(getVehicle(veh.id, useInventory=True)), reverse=True)
                vehiclesVOs = [ _createVehicleVO(packedVeh, self.itemsCache) for packedVeh in vehicleItems ]
                if items:
                    itemsVOs = getDataMultiVehicles(items, vehicle)
                else:
                    itemsVOs = None
            return (vehiclesVOs, itemsVOs)

    def __getCompensationData(self, itemsPack):
        compensationMoney = MONEY_UNDEFINED
        if itemsPack is not None:
            for item in collapseItemsPack(itemsPack):
                compensateItemsCount = getCompensateItemsCount(item, self.itemsCache)
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
         'tooltip': makeTooltip(body=VEHICLE_PREVIEW.BUYINGPANEL_COMPENSATION_BODY),
         'iconInfo': iconInfo}

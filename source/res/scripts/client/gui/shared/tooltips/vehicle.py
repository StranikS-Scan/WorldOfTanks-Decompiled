# Embedded file name: scripts/client/gui/shared/tooltips/vehicle.py
import BigWorld
import constants
from debug_utils import LOG_ERROR
from gui.shared.formatters.time_formatters import RentLeftFormatter
from helpers import i18n
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.shared import g_itemsCache
from gui.shared.tooltips import ToolTipDataField, ToolTipParameterField, ToolTipAttrField, ToolTipData, getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils import ItemsParameters, ParametersCache
from gui.prb_control.dispatcher import g_prbLoader

class VehicleStatusField(ToolTipDataField):

    def _getValue(self):
        vehicle = self._tooltip.item
        config = self._tooltip.context.getStatusConfiguration(self._tooltip.item)
        if config.node is not None:
            return self.__getTechTreeVehicleStatus(config, vehicle)
        else:
            return self.__getVehicleStatus(config.showCustomStates, vehicle)

    def __getTechTreeVehicleStatus(self, config, vehicle):
        nodeState = int(config.node.state)
        tooltip, level = None, Vehicle.VEHICLE_STATE_LEVEL.WARNING
        parentCD = None
        if config.node is not None:
            parentCD = config.node.unlockProps.parentID
        _, _, need2Unlock = getUnlockPrice(vehicle.intCD, parentCD)
        if not nodeState & NODE_STATE.UNLOCKED:
            if not nodeState & NODE_STATE.NEXT_2_UNLOCK:
                tooltip = '#tooltips:researchPage/vehicle/status/parentModuleIsLocked'
            elif need2Unlock > 0:
                tooltip = '#tooltips:researchPage/module/status/notEnoughXP'
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
        else:
            if nodeState & NODE_STATE.IN_INVENTORY:
                return self.__getVehicleStatus(False, vehicle)
            canRentOrBuy, reason = vehicle.mayRentOrBuy(g_itemsCache.items.stats.money)
            if not canRentOrBuy:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                if reason == 'gold_error':
                    tooltip = '#tooltips:moduleFits/gold_error'
                elif reason == 'credit_error':
                    tooltip = '#tooltips:moduleFits/credit_error'
                else:
                    tooltip = '#tooltips:moduleFits/operation_error'
        header, text = getComplexStatus(tooltip)
        if header is None and text is None:
            return
        else:
            return {'header': header,
             'text': text,
             'level': level}

    def __getVehicleStatus(self, showCustomStates, vehicle):
        if showCustomStates:
            isUnlocked = vehicle.isUnlocked
            isInInventory = vehicle.isInInventory
            credits, gold = g_itemsCache.items.stats.money
            price = vehicle.minRentPrice or vehicle.buyPrice
            msg = None
            level = Vehicle.VEHICLE_STATE_LEVEL.WARNING
            if not isUnlocked:
                msg = 'notUnlocked'
            elif isInInventory:
                msg = 'inHangar'
            elif credits < price[0]:
                msg = 'notEnoughCredits'
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
            elif gold < price[1]:
                msg = 'notEnoughGold'
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
            if msg is not None:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % msg)
                return {'header': header,
                 'text': text,
                 'level': level}
            return
        state, level = vehicle.getState()
        if state == Vehicle.VEHICLE_STATE.SERVER_RESTRICTION:
            return
        state, level = self.__preprocessState(state, level)
        header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state)
        if header is None and text is None:
            return
        else:
            return {'header': header,
             'text': text,
             'level': level}

    def __preprocessState(self, state, level):
        config = self._tooltip.context.getStatusConfiguration(self._tooltip.item)
        preQueue = g_prbLoader.getDispatcher().getPreQueueFunctional()
        return (state, level)


class VehicleStatsField(ToolTipDataField):

    def _getValue(self):
        result = []
        vehicle = self._tooltip.item
        configuration = self._tooltip.context.getStatsConfiguration(vehicle)
        xp = configuration.xp
        dailyXP = configuration.dailyXP
        unlockPrice = configuration.unlockPrice
        buyPrice = configuration.buyPrice
        sellPrice = configuration.sellPrice
        techTreeNode = configuration.node
        minRentPrice = configuration.minRentPrice
        rentals = configuration.rentals
        if buyPrice and sellPrice:
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
            return
        else:
            isUnlocked = vehicle.isUnlocked
            isInInventory = vehicle.isInInventory
            isRented = vehicle.isRented
            isNextToUnlock = False
            parentCD = None
            if techTreeNode is not None:
                isNextToUnlock = bool(int(techTreeNode.state) & NODE_STATE.NEXT_2_UNLOCK)
                parentCD = techTreeNode.unlockProps.parentID
            if xp:
                xpValue = vehicle.xp
                if xpValue:
                    result.append(('xp', xpValue))
            if dailyXP:
                attrs = g_itemsCache.items.stats.attributes
                if attrs & constants.ACCOUNT_ATTR.DAILY_MULTIPLIED_XP and vehicle.dailyXPFactor:
                    result.append(('dailyXPFactor', vehicle.dailyXPFactor))
            if unlockPrice:
                isAvailable, cost, need = getUnlockPrice(vehicle.intCD, parentCD)
                unlockPriceStat = [cost]
                if isAvailable and not isUnlocked and need > 0 and techTreeNode is not None:
                    unlockPriceStat.append(need)
                if cost > 0:
                    result.append(('unlock_price', unlockPriceStat))
            if buyPrice and not (vehicle.isDisabledForBuy or vehicle.isPremiumIGR):
                price = vehicle.buyPrice
                needed = (0, 0)
                if not isInInventory and (isNextToUnlock or isUnlocked) or isRented:
                    credits, gold = g_itemsCache.items.stats.money
                    creditsNeeded = price[0] - credits if price[0] else 0
                    goldNeeded = price[1] - gold if price[1] else 0
                    needed = (max(0, creditsNeeded), max(0, goldNeeded))
                result.append(('buy_price', (price, needed)))
                result.append(('def_buy_price', vehicle.defaultPrice))
                result.append(('action_prc', vehicle.actionPrc))
            if sellPrice:
                result.append(('sell_price', vehicle.sellPrice))
                result.append(('def_sell_price', vehicle.defaultSellPrice))
                result.append(('action_prc', vehicle.sellActionPrc))
            if minRentPrice and not vehicle.isPremiumIGR:
                minRentPricePackage = vehicle.getRentPackage()
                if minRentPricePackage:
                    minRentPriceValue = minRentPricePackage['rentPrice']
                    minDefaultRentPriceValue = minRentPricePackage['defaultRentPrice']
                    rentActionPrc = vehicle.getRentPackageActionPrc(minRentPricePackage['days'])
                    credits, gold = g_itemsCache.items.stats.money
                    enoughGoldForRent = gold - minRentPriceValue[1] >= 0
                    enoughCreditsForRent = credits - minRentPriceValue[0] >= 0
                    result.append(('minRentalsPrice', (minRentPriceValue, (enoughCreditsForRent, enoughGoldForRent))))
                    result.append(('defRentPrice', minDefaultRentPriceValue))
                    result.append(('rentActionPrc', rentActionPrc))
            if rentals and not vehicle.isPremiumIGR:
                rentFormatter = RentLeftFormatter(vehicle.rentInfo)
                rentLeftInfo = rentFormatter.getRentLeftStr('#tooltips:vehicle/rentLeft/%s', formatter=lambda key, countType, count, _ = None: {'left': count,
                 'descr': i18n.makeString(key % countType)})
                if rentLeftInfo:
                    result.append(('rentals', rentLeftInfo))
            return result


class VehicleParamsField(ToolTipParameterField):
    PARAMS = {'lightTank': ('speedLimits', 'enginePowerPerTon', 'chassisRotationSpeed', 'circularVisionRadius'),
     'mediumTank': ('speedLimits', 'enginePowerPerTon', 'chassisRotationSpeed', 'damageAvgPerMinute'),
     'heavyTank': ('hullArmor', 'turretArmor', 'damageAvg', 'piercingPower'),
     'SPG': ('damageAvg', 'explosionRadius', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs'),
     'AT-SPG': ('speedLimits', 'chassisRotationSpeed', 'damageAvgPerMinute', 'shotDispersionAngle', 'piercingPower'),
     'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}

    def _getValue(self):
        result = list()
        vehicle = self._tooltip.item
        configuration = self._tooltip.context.getParamsConfiguration(vehicle)
        params = configuration.params
        crew = configuration.crew
        eqs = configuration.eqs
        devices = configuration.devices
        vehicleCommonParams = dict(ItemsParameters.g_instance.getParameters(vehicle.descriptor))
        vehicleRawParams = dict(ParametersCache.g_instance.getParameters(vehicle.descriptor))
        result.append([])
        if params:
            for paramName in self.PARAMS.get(vehicle.type, 'default'):
                if paramName in vehicleCommonParams or paramName in vehicleRawParams:
                    result[-1].append(self._getParameterValue(paramName, vehicleCommonParams, vehicleRawParams))

        result.append([])
        if crew:
            currentCrewSize = 0
            if vehicle.isInInventory:
                currentCrewSize = len([ x for _, x in vehicle.crew if x is not None ])
            result[-1].append({'label': 'crew',
             'current': currentCrewSize,
             'total': len(vehicle.descriptor.type.crewRoles)})
        if eqs:
            result[-1].append({'label': 'equipments',
             'current': len([ x for x in vehicle.eqs if x ]),
             'total': len(vehicle.eqs)})
        if devices:
            result[-1].append({'label': 'devices',
             'current': len([ x for x in vehicle.descriptor.optionalDevices if x ]),
             'total': len(vehicle.descriptor.optionalDevices)})
        return result

    def _getParameterValue(self, paramName, paramsDict, rawParamsDict):
        htmlText = makeHtmlString('html_templates:lobby/tank_params', paramName)
        if paramName == 'enginePowerPerTon':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        if paramName == 'damageAvgPerMinute':
            return (htmlText, BigWorld.wg_getIntegralFormat(rawParamsDict[paramName]))
        if paramName == 'damageAvg':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        if paramName == 'reloadTimeSecs':
            return (htmlText, BigWorld.wg_getIntegralFormat(rawParamsDict[paramName]))
        if paramName == 'explosionRadius':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        if paramName == 'shotDispersionAngle':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        if paramName in paramsDict:
            return (htmlText, paramsDict.get(paramName))
        return (htmlText, rawParamsDict.get(paramName))


class VehicleLocksField(ToolTipParameterField):

    def _getValue(self):
        vehicle = self._tooltip.item
        return {'CLAN': vehicle.clanLock or None,
         'ROAMING': vehicle.isDisabledInRoaming}


class VehicleTooltipData(ToolTipData):

    def __init__(self, context):
        super(VehicleTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self.fields = (ToolTipAttrField(self, 'name', 'userName'),
         ToolTipAttrField(self, 'type'),
         ToolTipAttrField(self, 'isElite'),
         ToolTipAttrField(self, 'isPremium'),
         ToolTipAttrField(self, 'level'),
         ToolTipAttrField(self, 'isFavorite'),
         VehicleStatusField(self, 'status'),
         VehicleStatsField(self, 'stats'),
         VehicleParamsField(self, 'params'),
         VehicleLocksField(self, 'locks'))

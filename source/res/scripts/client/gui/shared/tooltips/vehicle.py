# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/vehicle.py
import BigWorld
import constants
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import i18n, time_utils, int2roman
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.shared import g_itemsCache
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils import ItemsParameters, ParametersCache
from gui.shared.tooltips import formatters
from helpers.i18n import makeString as _ms
from BigWorld import wg_getIntegralFormat as _int

class VehicleInfoTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=10, right=0)
        self._setMargins(10, 15)
        self._setWidth(400)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(VehicleInfoTooltipData, self)._packBlocks()
        vehicle = self.item
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        statusConfig = self.context.getStatusConfiguration(vehicle)
        leftPadding = 20
        rightPadding = 0
        valueWidth = 60
        if vehicle.type == 'heavyTank':
            valueWidth = 75
        textGap = -2
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct()))
        telecomBlock = TelecomBlockConstructor(vehicle, valueWidth, leftPadding, rightPadding).construct()
        if telecomBlock.__len__() > 0:
            items.append(formatters.packBuildUpBlockData(telecomBlock))
        priceBlock = PriceBlockConstructor(vehicle, statsConfig, valueWidth, leftPadding, rightPadding).construct()
        if priceBlock.__len__() > 0:
            items.append(formatters.packBuildUpBlockData(priceBlock, gap=textGap))
        items.append(formatters.packBuildUpBlockData(CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct(), gap=textGap))
        items.append(formatters.packBuildUpBlockData(AdditionalStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct(), gap=textGap))
        statusBlock = StatusBlockConstructor(vehicle, statusConfig).construct()
        if statusBlock is not None:
            items.append(formatters.packBuildUpBlockData(statusBlock))
        else:
            self._setContentMargin(bottom=20)
        return items


class VehicleTooltipBlockConstructor(object):

    def __init__(self, vehicle, configuration, leftPadding=20, rightPadding=20):
        self.vehicle = vehicle
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding

    def construct(self):
        return None


class HeaderBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, leftPadding, rightPadding):
        super(HeaderBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)

    def construct(self):
        block = []
        if self.vehicle.isElite:
            vehicleType = TOOLTIPS.tankcaruseltooltip_vehicletype_elite(self.vehicle.type)
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_ELITE_VEHICLE_FAVORITE_BG_LINKAGE if self.vehicle.isFavorite else BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_ELITE_VEHICLE_BG_LINKAGE
        else:
            vehicleType = TOOLTIPS.tankcaruseltooltip_vehicletype_normal(self.vehicle.type)
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_FAVORITE_BG_LINKAGE if self.vehicle.isFavorite else BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE
        nameStr = text_styles.highTitle(self.vehicle.userName)
        typeStr = text_styles.main(vehicleType)
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(self.vehicle.level)), text_styles.standard(_ms(TOOLTIPS.VEHICLE_LEVEL)))
        icon = '../maps/icons/vehicleTypes/big/' + self.vehicle.type + ('_elite.png' if self.vehicle.isElite else '.png')
        imgOffset = 4
        textOffset = 82
        if self.vehicle.type == 'heavyTank':
            imgOffset = 11
            textOffset = 99
        iconBlock = formatters.packImageTextBlockData(title=nameStr, desc=text_styles.concatStylesToMultiLine(typeStr, levelStr), img=icon, imgPadding={'left': imgOffset,
         'top': -15}, txtGap=-2, txtOffset=textOffset, padding=formatters.packPadding(top=15, bottom=-15))
        block.append(formatters.packBuildUpBlockData([iconBlock], stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-19 + self.leftPadding, top=-1)))
        return block


class TelecomBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, valueWidth, leftPadding, rightPadding):
        super(TelecomBlockConstructor, self).__init__(vehicle, None, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        return

    def construct(self):
        if self.vehicle.isTelecom:
            return [formatters.packTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_DEAL_TELECOM_MAIN)), value='', valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding))]
        else:
            return []


class PriceBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        xp = self.configuration.xp
        dailyXP = self.configuration.dailyXP
        buyPrice = self.configuration.buyPrice
        sellPrice = self.configuration.sellPrice
        unlockPrice = self.configuration.unlockPrice
        techTreeNode = self.configuration.node
        minRentPrice = self.configuration.minRentPrice
        rentals = self.configuration.rentals
        if buyPrice and sellPrice:
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
            return
        else:
            priceBlock = []
            isUnlocked = self.vehicle.isUnlocked
            isInInventory = self.vehicle.isInInventory
            isRented = self.vehicle.isRented
            isNextToUnlock = False
            parentCD = None
            if techTreeNode is not None:
                isNextToUnlock = bool(int(techTreeNode.state) & NODE_STATE.NEXT_2_UNLOCK)
                parentCD = techTreeNode.unlockProps.parentID
            if xp:
                xpValue = self.vehicle.xp
                if xpValue:
                    xPText = text_styles.expText(_int(xpValue))
                    icon = ICON_TEXT_FRAMES.FREE_XP if self.vehicle.isPremium else ICON_TEXT_FRAMES.XP
                    priceBlock.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_XP)), value=xPText, icon=icon, valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding)))
            if dailyXP:
                attrs = g_itemsCache.items.stats.attributes
                if attrs & constants.ACCOUNT_ATTR.DAILY_MULTIPLIED_XP and self.vehicle.dailyXPFactor > 0:
                    dailyXPText = text_styles.main(text_styles.expText('x' + _int(self.vehicle.dailyXPFactor)))
                    priceBlock.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_DAILYXPFACTOR)), value=dailyXPText, icon=ICON_TEXT_FRAMES.DOUBLE_XP_FACTOR, valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding)))
            if unlockPrice:
                isAvailable, cost, need = getUnlockPrice(self.vehicle.intCD, parentCD)
                if cost > 0:
                    neededValue = None
                    if isAvailable and not isUnlocked and need > 0 and techTreeNode is not None:
                        neededValue = need
                    block = self._makePriceBlock(cost, _ms(TOOLTIPS.VEHICLE_UNLOCK_PRICE), ICON_TEXT_FRAMES.XP, neededValue)
                    priceBlock.append(block)
            if buyPrice and not (self.vehicle.isDisabledForBuy or self.vehicle.isPremiumIGR or self.vehicle.isTelecom):
                price = self.vehicle.buyPrice
                credits, gold = g_itemsCache.items.stats.money
                creditsBuyPrice = price[0]
                goldBuyPrice = price[1]
                creditsNeeded = creditsBuyPrice - credits if creditsBuyPrice else 0
                goldNeeded = goldBuyPrice - gold if goldBuyPrice else 0
                neededValue = None
                actionPrc = self.vehicle.actionPrc
                defaultPrice = self.vehicle.defaultPrice
                if goldBuyPrice == 0:
                    currencyType = ICON_TEXT_FRAMES.CREDITS
                    buyPriceText = creditsBuyPrice
                    oldPrice = defaultPrice[0]
                    if creditsNeeded > 0:
                        neededValue = creditsNeeded
                else:
                    currencyType = ICON_TEXT_FRAMES.GOLD
                    buyPriceText = goldBuyPrice
                    oldPrice = defaultPrice[1]
                    if goldNeeded > 0:
                        neededValue = goldNeeded
                text = _ms(TOOLTIPS.VEHICLE_BUY_PRICE)
                if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                    neededValue = None
                block = self._makePriceBlock(buyPriceText, text, currencyType, neededValue, oldPrice, actionPrc)
                priceBlock.append(block)
            if sellPrice and not self.vehicle.isTelecom:
                creditsPrice = self.vehicle.sellPrice[0]
                goldPrice = self.vehicle.sellPrice[1]
                if goldPrice == 0:
                    sellPriceText = text_styles.credits(_int(creditsPrice))
                    sellPriceIcon = ICON_TEXT_FRAMES.CREDITS
                else:
                    sellPriceText = text_styles.gold(_int(goldPrice))
                    sellPriceIcon = ICON_TEXT_FRAMES.GOLD
                priceBlock.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_SELL_PRICE)), value=sellPriceText, icon=sellPriceIcon, valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding)))
            if minRentPrice and not self.vehicle.isPremiumIGR:
                minRentPricePackage = self.vehicle.getRentPackage()
                if minRentPricePackage:
                    minRentPriceValue = minRentPricePackage['rentPrice']
                    minDefaultRentPriceValue = minRentPricePackage['defaultRentPrice']
                    rentActionPrc = self.vehicle.getRentPackageActionPrc(minRentPricePackage['days'])
                    credits, gold = g_itemsCache.items.stats.money
                    creditsPrice = minRentPriceValue[0]
                    goldPrice = minRentPriceValue[1]
                    enoughCreditsForRent = credits - creditsPrice >= 0
                    enoughGoldForRent = gold - goldPrice >= 0
                    neededValue = None
                    if goldPrice == 0:
                        price = creditsPrice
                        oldPrice = minDefaultRentPriceValue[0]
                        currencyType = ICON_TEXT_FRAMES.CREDITS
                        if not enoughCreditsForRent:
                            neededValue = credits - creditsPrice
                    else:
                        price = goldPrice
                        oldPrice = minDefaultRentPriceValue[1]
                        currencyType = ICON_TEXT_FRAMES.GOLD
                        if not enoughGoldForRent:
                            neededValue = gold - goldPrice
                    text = _ms(TOOLTIPS.VEHICLE_MINRENTALSPRICE)
                    block = self._makePriceBlock(price, text, currencyType, neededValue, oldPrice, rentActionPrc)
                    priceBlock.append(block)
            if rentals and not self.vehicle.isPremiumIGR:
                rentFormatter = RentLeftFormatter(self.vehicle.rentInfo)
                rentLeftInfo = rentFormatter.getRentLeftStr('#tooltips:vehicle/rentLeft/%s', formatter=lambda key, countType, count, _=None: {'left': count,
                 'descr': i18n.makeString(key % countType)})
                if rentLeftInfo:
                    priceBlock.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(rentLeftInfo['descr']), value=text_styles.main(rentLeftInfo['left']), icon=ICON_TEXT_FRAMES.RENTALS, valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding)))
            return priceBlock

    def _makePriceBlock(self, price, text, currencyType, neededValue=None, oldPrice=None, percent=0):
        needFormatted = ''
        oldPriceText = ''
        hasAction = percent != 0
        if currencyType == ICON_TEXT_FRAMES.CREDITS:
            valueFormatted = text_styles.credits(_int(price))
            icon = icons.credits()
            if neededValue is not None:
                needFormatted = text_styles.credits(_int(neededValue))
            if hasAction:
                oldPriceText = text_styles.concatStylesToSingleLine(icons.credits(), text_styles.credits(_int(oldPrice)))
        elif currencyType == ICON_TEXT_FRAMES.GOLD:
            valueFormatted = text_styles.gold(_int(price))
            icon = icons.gold()
            if neededValue is not None:
                needFormatted = text_styles.gold(_int(neededValue))
            if hasAction:
                oldPriceText = text_styles.concatStylesToSingleLine(icons.gold(), text_styles.gold(_int(oldPrice)))
        elif currencyType == ICON_TEXT_FRAMES.XP:
            valueFormatted = text_styles.expText(_int(price))
            icon = icons.xp()
            if neededValue is not None:
                needFormatted = text_styles.expText(_int(neededValue))
        else:
            LOG_ERROR('Unsupported currency type "' + currencyType + '"!')
            return
        neededText = ''
        if neededValue is not None:
            neededText = text_styles.concatStylesToSingleLine(text_styles.main('( '), text_styles.error(TOOLTIPS.VEHICLE_GRAPH_BODY_NOTENOUGH), ' ', needFormatted, ' ', icon, text_styles.main(' )'))
        text = text_styles.concatStylesWithSpace(text_styles.main(text), neededText)
        if hasAction:
            actionText = text_styles.main(_ms(TOOLTIPS.VEHICLE_ACTION_PRC, actionPrc=text_styles.stats(str(percent) + '%'), oldPrice=oldPriceText))
            text = text_styles.concatStylesToMultiLine(text, actionText)
        return formatters.packTextParameterWithIconBlockData(name=text, value=valueFormatted, icon=currencyType, valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=20))


class CommonStatsBlockConstructor(VehicleTooltipBlockConstructor):
    PARAMS = {'lightTank': ('speedLimits', 'enginePowerPerTon', 'chassisRotationSpeed', 'circularVisionRadius'),
     'mediumTank': ('speedLimits', 'enginePowerPerTon', 'chassisRotationSpeed', 'damageAvgPerMinute'),
     'heavyTank': ('hullArmor', 'turretArmor', 'damageAvg', 'piercingPower'),
     'SPG': ('damageAvg', 'explosionRadius', 'shotDispersionAngle', 'aimingTime', 'reloadTimeSecs'),
     'AT-SPG': ('speedLimits', 'chassisRotationSpeed', 'damageAvgPerMinute', 'shotDispersionAngle', 'piercingPower'),
     'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        params = self.configuration.params
        vehicleCommonParams = dict(ItemsParameters.g_instance.getParameters(self.vehicle.descriptor))
        vehicleRawParams = dict(ParametersCache.g_instance.getParameters(self.vehicle.descriptor))
        block = [formatters.packTitleDescBlock(text_styles.middleTitle(_ms(TOOLTIPS.TANKCARUSEL_MAINPROPERTY)), padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding, bottom=8))]
        if params:
            for paramName in self.PARAMS.get(self.vehicle.type, 'default'):
                if paramName in vehicleCommonParams or paramName in vehicleRawParams:
                    param = self._getParameterValue(paramName, vehicleCommonParams, vehicleRawParams)
                    block.append(formatters.packTextParameterBlockData(name=text_styles.main(param[0]), value=text_styles.stats(param[1]), valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding)))

        return block

    def _getParameterValue(self, paramName, paramsDict, rawParamsDict):
        paramsMap = {'speedLimits': MENU.TANK_PARAMS_MPH,
         'enginePowerPerTon': MENU.TANK_PARAMS_PT,
         'chassisRotationSpeed': MENU.TANK_PARAMS_GPS,
         'circularVisionRadius': MENU.TANK_PARAMS_M,
         'damageAvgPerMinute': MENU.TANK_PARAMS_VPM,
         'hullArmor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
         'turretArmor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
         'damageAvg': MENU.TANK_PARAMS_VAL,
         'piercingPower': MENU.TANK_PARAMS_MM,
         'explosionRadius': MENU.TANK_PARAMS_M,
         'shotDispersionAngle': MENU.TANK_PARAMS_M,
         'aimingTime': MENU.TANK_PARAMS_S,
         'reloadTimeSecs': MENU.TANK_PARAMS_S,
         'enginePower': MENU.TANK_PARAMS_P}
        if paramName not in paramsMap:
            LOG_ERROR('There is no key "' + paramName + '" in paramsMap')
            return None
        htmlText = text_styles.main(_ms(MENU.tank_params(paramName))) + text_styles.standard(_ms(paramsMap[paramName]))
        if paramName == 'enginePowerPerTon':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        elif paramName == 'damageAvgPerMinute':
            return (htmlText, _int(rawParamsDict[paramName]))
        elif paramName == 'damageAvg':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        elif paramName == 'reloadTimeSecs':
            return (htmlText, _int(rawParamsDict[paramName]))
        elif paramName == 'explosionRadius':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        elif paramName == 'shotDispersionAngle':
            return (htmlText, BigWorld.wg_getNiceNumberFormat(rawParamsDict[paramName]))
        else:
            return (htmlText, paramsDict.get(paramName)) if paramName in paramsDict else (htmlText, rawParamsDict.get(paramName))


class AdditionalStatsBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(AdditionalStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        crew = self.configuration.crew
        eqs = self.configuration.eqs
        devices = self.configuration.devices
        isInInventory = self.vehicle.isInInventory
        block = []
        if crew:
            totalCrewSize = len(self.vehicle.descriptor.type.crewRoles)
            if isInInventory:
                currentCrewSize = len([ x for _, x in self.vehicle.crew if x is not None ])
                block.append(self._makeStatBlock(currentCrewSize, totalCrewSize, TOOLTIPS.VEHICLE_CREW))
            else:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_CREW)), value=text_styles.stats(str(totalCrewSize)), valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding)))
        if eqs:
            block.append(self._makeStatBlock(len([ x for x in self.vehicle.eqs if x ]), len(self.vehicle.eqs), TOOLTIPS.VEHICLE_EQUIPMENTS))
        if devices:
            block.append(self._makeStatBlock(len([ x for x in self.vehicle.descriptor.optionalDevices if x ]), len(self.vehicle.descriptor.optionalDevices), TOOLTIPS.VEHICLE_DEVICES))
        lockBlock = self._makeLockBlock()
        if lockBlock is not None:
            block.append(lockBlock)
        return block

    def _makeLockBlock(self):
        isClanLock = self.vehicle.clanLock or None
        isDisabledInRoaming = self.vehicle.isDisabledInRoaming
        if isClanLock or isDisabledInRoaming:
            headerLock = text_styles.concatStylesToMultiLine(text_styles.warning(_ms(TOOLTIPS.TANKCARUSEL_LOCK_HEADER)))
            if isDisabledInRoaming:
                textLock = text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROAMING))
            else:
                time = time_utils.getDateTimeFormat(isClanLock + time_utils.getCurrentTimestamp())
                timeStr = text_styles.main(text_styles.concatStylesWithSpace(_ms(TOOLTIPS.TANKCARUSEL_LOCK_TO), time))
                textLock = text_styles.concatStylesToMultiLine(timeStr, text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_CLAN)))
            lockHeaderBlock = formatters.packTextBlockData(headerLock, padding=formatters.packPadding(left=77 + self.leftPadding, top=5))
            lockTextBlock = formatters.packTextBlockData(textLock, padding=formatters.packPadding(left=77 + self.leftPadding))
            return formatters.packBuildUpBlockData([lockHeaderBlock, lockTextBlock], stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LOCK_BG_LINKAGE, padding=formatters.packPadding(left=-17 + self.leftPadding, top=20, bottom=0))
        else:
            return
            return

    def _makeStatBlock(self, current, total, text):
        return formatters.packTextParameterBlockData(name=text_styles.main(_ms(text)), value=text_styles.stats(str(current) + '/' + str(total)), valueWidth=self._valueWidth, padding=formatters.packPadding(left=self.leftPadding, right=self.rightPadding))


class StatusBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        isClanLock = self.vehicle.clanLock or None
        isDisabledInRoaming = self.vehicle.isDisabledInRoaming
        if isClanLock or isDisabledInRoaming:
            return
        else:
            if self.configuration.node is not None:
                result = self.__getTechTreeVehicleStatus(self.configuration, self.vehicle)
            else:
                result = self.__getVehicleStatus(self.configuration.showCustomStates, self.vehicle)
            if result is not None:
                statusLevel = result['level']
                if statusLevel == Vehicle.VEHICLE_STATE_LEVEL.INFO:
                    headerFormatter = text_styles.statInfo
                elif statusLevel == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL:
                    headerFormatter = text_styles.critical
                elif statusLevel == Vehicle.VEHICLE_STATE_LEVEL.WARNING:
                    headerFormatter = text_styles.warning
                elif statusLevel == Vehicle.VEHICLE_STATE_LEVEL.RENTED:
                    headerFormatter = text_styles.warning
                else:
                    LOG_ERROR('Unknown status type "' + statusLevel + '"!')
                    headerFormatter = text_styles.statInfo
                header = headerFormatter(result['header'])
                text = result['text']
                if text is not None:
                    text = text_styles.standard(text)
                    padding = formatters.packPadding(left=self.leftPadding, right=self.leftPadding)
                else:
                    header = makeHtmlString('html_templates:lobby/textStyle', 'alignText', {'align': 'center',
                     'message': header})
                    padding = formatters.packPadding(left=0, right=0)
                return [formatters.packTextBlockData(header, padding=padding), formatters.packTextBlockData(text, padding=padding)]
            return
            return

    def __getTechTreeVehicleStatus(self, config, vehicle):
        nodeState = int(config.node.state)
        tooltip, level = None, Vehicle.VEHICLE_STATE_LEVEL.WARNING
        parentCD = None
        if config.node is not None:
            parentCD = config.node.unlockProps.parentID
        _, _, need2Unlock = getUnlockPrice(vehicle.intCD, parentCD)
        if not nodeState & NODE_STATE.UNLOCKED:
            if not nodeState & NODE_STATE.NEXT_2_UNLOCK:
                tooltip = TOOLTIPS.RESEARCHPAGE_VEHICLE_STATUS_PARENTMODULEISLOCKED
            elif need2Unlock > 0:
                tooltip = TOOLTIPS.RESEARCHPAGE_MODULE_STATUS_NOTENOUGHXP
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
        else:
            if nodeState & NODE_STATE.IN_INVENTORY:
                return self.__getVehicleStatus(False, vehicle)
            canRentOrBuy, reason = vehicle.mayRentOrBuy(g_itemsCache.items.stats.money)
            if not canRentOrBuy:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                if reason == 'gold_error':
                    tooltip = TOOLTIPS.MODULEFITS_GOLD_ERROR
                elif reason == 'credit_error':
                    tooltip = TOOLTIPS.MODULEFITS_CREDIT_ERROR
                else:
                    tooltip = TOOLTIPS.MODULEFITS_OPERATION_ERROR
        header, text = getComplexStatus(tooltip)
        return None if header is None and text is None else {'header': header,
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
        else:
            state, level = vehicle.getState()
            if state == Vehicle.VEHICLE_STATE.SERVER_RESTRICTION:
                return
            header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state)
            return None if header is None and text is None else {'header': header,
             'text': text,
             'level': level}

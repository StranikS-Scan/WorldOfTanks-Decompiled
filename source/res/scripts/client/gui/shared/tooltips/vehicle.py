# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/vehicle.py
import constants
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.game_control import getFalloutCtrl
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.items_parameters import RELATIVE_PARAMS, MAX_RELATIVE_VALUE, formatters as param_formatter, params_helper
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from helpers import i18n, time_utils, int2roman
from gui.Scaleform.daapi.view.lobby.techtree.settings import NODE_STATE
from gui.shared import g_itemsCache
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips import formatters
from gui.shared.money import Money, Currency
from helpers.i18n import makeString as _ms
from BigWorld import wg_getIntegralFormat as _int
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.items_parameters.formatters import MEASURE_UNITS
from gui.shared.gui_items.Tankman import Tankman
from debug_utils import LOG_DEBUG
_EQUIPMENT = 'equipment'
_OPTION_DEVICE = 'optionalDevice'
_ARTEFACT_TYPES = (_EQUIPMENT, _OPTION_DEVICE)
_SKILL_BONUS_TYPE = 'skill'
_ROLE_BONUS_TYPE = 'role'
_EXTRA_BONUS_TYPE = 'extra'
_TOOLTIP_MIN_WIDTH = 420
_TOOLTIP_MAX_WIDTH = 460
_CREW_TOOLTIP_PARAMS = {Tankman.ROLES.COMMANDER: (TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_RECONNAISSANCE, '10%', '1%'),
 Tankman.ROLES.GUNNER: (TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_FIREPOWER,),
 Tankman.ROLES.DRIVER: (TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_MOBILITY,),
 Tankman.ROLES.RADIOMAN: (TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_RECONNAISSANCE,),
 Tankman.ROLES.LOADER: (TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_FIREPOWER,)}

def _bonusCmp(x, y):
    return cmp(x[1], y[1]) or cmp(x[0], y[0])


class VehicleInfoTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=20, right=0)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(VehicleInfoTooltipData, self)._packBlocks()
        vehicle = self.item
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        statusConfig = self.context.getStatusConfiguration(vehicle)
        leftPadding = 20
        rightPadding = 20
        bottomPadding = 20
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 75
        textGap = -2
        items.append(formatters.packBuildUpBlockData(HeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding))
        telecomBlock = TelecomBlockConstructor(vehicle, valueWidth, leftPadding, rightPadding).construct()
        if len(telecomBlock) > 0:
            items.append(formatters.packBuildUpBlockData(telecomBlock, padding=leftRightPadding))
        priceBlock, invalidWidth = PriceBlockConstructor(vehicle, statsConfig, valueWidth, leftPadding, rightPadding).construct()
        if len(priceBlock) > 0:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, gap=textGap, padding=blockPadding))
        items.append(formatters.packBuildUpBlockData(SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct(), gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        commonStatsBlock = CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct()
        if len(commonStatsBlock) > 0:
            items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=textGap, padding=blockPadding))
        footnoteBlock = FootnoteBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if len(footnoteBlock):
            items.append(formatters.packBuildUpBlockData(footnoteBlock, gap=textGap, padding=blockPadding))
        items.append(formatters.packBuildUpBlockData(AdditionalStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct(), gap=textGap, padding=blockPadding))
        statusBlock = StatusBlockConstructor(vehicle, statusConfig).construct()
        if len(statusBlock) > 0:
            items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding))
        else:
            self._setContentMargin(bottom=bottomPadding)
        return items


class VehicleParametersTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleParametersTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setMargins(11, 14)
        self._setWidth(360)
        self.__paramName = None
        return

    def _packBlocks(self, paramName):
        extendedData = self.context.getComparator().getExtendedData(paramName)
        self.__paramName = extendedData.name
        title = text_styles.highTitle(MENU.tank_params(paramName))
        if param_formatter.isRelativeParameter(paramName):
            value = param_formatter.colorizedFormatParameter(extendedData, self.context.formatters)
            title += ' ' + text_styles.warning(_ms(TOOLTIPS.VEHICLEPARAMS_TITLE_VALUETEMPLATE, value=value))
        else:
            title += ' ' + text_styles.middleTitle(MEASURE_UNITS.get(paramName, ''))
        desc = _ms(TOOLTIPS.tank_params_desc(paramName))
        possibleBonuses = sorted(extendedData.possibleBonuses, _bonusCmp)
        if possibleBonuses is not None and len(possibleBonuses) > 0:
            desc += ' ' + _ms(TOOLTIPS.VEHICLEPARAMS_POSSIBLEBONUSES_DESC)
            desc += '\n' + self.__createBonusesStr(possibleBonuses)
        blocks = [formatters.packTitleDescBlock(title, text_styles.main(desc))]
        bonuses = sorted(extendedData.bonuses, _bonusCmp)
        if bonuses is not None and len(bonuses) > 0:
            blocks.append(formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.VEHICLEPARAMS_BONUSES_TITLE), text_styles.main(self.__createBonusesStr(bonuses))))
        penalties = extendedData.penalties
        actualPenalties, nullPenaltyTypes = self.__getNumNotNullPenaltyTankman(penalties)
        penaltiesLen = len(penalties)
        numNotNullPenaltyTankman = len(actualPenalties)
        if numNotNullPenaltyTankman > 0:
            blocks.append(formatters.packTitleDescBlock(text_styles.critical(TOOLTIPS.VEHICLEPARAMS_PENALTIES_TITLE), text_styles.main(self.__createPenaltiesStr(actualPenalties))))
        if penaltiesLen > numNotNullPenaltyTankman:
            blocks.append(formatters.packImageTextBlockData(self.__createTankmanIsOutStr(nullPenaltyTypes), img=RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICONFILLED, imgPadding=formatters.packPadding(top=2, left=3, right=6)))
        return blocks

    def __createBonusesStr(self, bonuses):
        result = []
        for bnsId, bnsType in bonuses:
            if bnsType in _ARTEFACT_TYPES:
                bnsTypeStr = ''
                if bnsType == _EQUIPMENT:
                    bnsTypeStr = TOOLTIPS.VEHICLE_EQUIPMENTS
                if bnsType == _OPTION_DEVICE:
                    bnsTypeStr = TOOLTIPS.VEHICLE_DEVICES
                result.append(text_styles.main(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_ARTEFACT_TEMPLATE, name=_ms('#artefacts:%s/name' % bnsId), type=text_styles.standard(bnsTypeStr))))
            if bnsType == _SKILL_BONUS_TYPE:
                result.append(text_styles.main(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_SKILL_TEMPLATE, name=_ms(ITEM_TYPES.tankman_skills(bnsId)), type=text_styles.standard(_ms(TOOLTIPS.VEHICLEPARAMS_SKILL_NAME)))))
            if bnsType == _ROLE_BONUS_TYPE:
                result.append(text_styles.main(_ms('#tooltips:vehicleParams/bonus/role/template', name=_ms('#tooltips:vehicleParams/bonus/tankmanLevel/%s' % bnsId))))
            if bnsType == _EXTRA_BONUS_TYPE:
                result.append(text_styles.main(_ms('#tooltips:vehicleParams/bonus/role/template', name=_ms('#tooltips:vehicleParams/bonus/extra/%s' % bnsId))))

        return '\n'.join(result)

    def __getNumNotNullPenaltyTankman(self, penalties):
        nullPenaltyTypes = []
        actualPenalties = []
        for penalty in penalties:
            if penalty[1] != 0:
                actualPenalties.append(penalty)
            nullPenaltyTypes.append(penalty[0])

        return (actualPenalties, nullPenaltyTypes)

    def __createPenaltiesStr(self, penalties):
        result = []
        for tankmanType, value, isOtherVehicle in penalties:
            if not param_formatter.isRelativeParameter(self.__paramName):
                valueStr = str(param_formatter.baseFormatParameter(self.__paramName, value))
                if value > 0:
                    valueStr = '+' + valueStr
                valueStr = text_styles.error(_ms(TOOLTIPS.VEHICLEPARAMS_PENALTY_TANKMANLEVEL_VALUE, value=valueStr))
            else:
                valueStr = ''
            if isOtherVehicle:
                locKey = TOOLTIPS.VEHICLEPARAMS_PENALTY_TANKMANDIFFERENTVEHICLE_TEMPLATE
            else:
                locKey = TOOLTIPS.VEHICLEPARAMS_PENALTY_TANKMANLEVEL_TEMPLATE
            result.append(text_styles.main(_ms(locKey, tankmanType=_ms(ITEM_TYPES.tankman_roles(tankmanType)), value=valueStr)))

        return '\n'.join(result)

    def __createTankmanIsOutStr(self, types):
        men = ''
        typesLen = len(types)
        for i, type in enumerate(types):
            men += _ms(ITEM_TYPES.tankman_roles(type))
            if i < typesLen - 1:
                men += ', '

        return text_styles.alert(_ms(TOOLTIPS.VEHICLEPARAMS_WARNING_TANKMANISOUT, tankmen=men))


class VehiclePreviewCrewMemberTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehiclePreviewCrewMemberTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(360)
        self._setMargins(13, 13)

    def _packBlocks(self, role):
        blocks = []
        bodyStr = '%s/%s' % (TOOLTIPS.VEHICLEPREVIEW_CREW, role)
        crewParams = [ text_styles.neutral(param) for param in _CREW_TOOLTIP_PARAMS[role] ]
        blocks.append(formatters.packTitleDescBlock(text_styles.highTitle(ITEM_TYPES.tankman_roles(role)), text_styles.main(_ms(bodyStr, *crewParams))))
        vehicle = self.context.getVehicle()
        for idx, tankman in vehicle.crew:
            if tankman.role == role:
                otherRoles = list(vehicle.descriptor.type.crewRoles[idx])
                otherRoles.remove(tankman.role)
                if otherRoles:
                    rolesStr = ', '.join([ text_styles.stats(_ms(ITEM_TYPES.tankman_roles(r))) for r in otherRoles ])
                    blocks.append(formatters.packTextBlockData(text_styles.main(_ms(TOOLTIPS.VEHICLEPREVIEW_CREW_ADDITIONALROLES, roles=rolesStr))))

        return blocks


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
        headerBlocks = []
        if self.vehicle.isElite:
            vehicleType = TOOLTIPS.tankcaruseltooltip_vehicletype_elite(self.vehicle.type)
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_ELITE_VEHICLE_BG_LINKAGE
        else:
            vehicleType = TOOLTIPS.tankcaruseltooltip_vehicletype_normal(self.vehicle.type)
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE
        nameStr = text_styles.highTitle(self.vehicle.userName)
        typeStr = text_styles.main(vehicleType)
        levelStr = text_styles.concatStylesWithSpace(text_styles.stats(int2roman(self.vehicle.level)), text_styles.standard(_ms(TOOLTIPS.VEHICLE_LEVEL)))
        icon = '../maps/icons/vehicleTypes/big/' + self.vehicle.type + ('_elite.png' if self.vehicle.isElite else '.png')
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc=text_styles.concatStylesToMultiLine(levelStr + ' ' + typeStr, ''), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-2, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        if self.vehicle.isFavorite:
            headerBlocks.append(formatters.packImageTextBlockData(title=text_styles.neutral(TOOLTIPS.VEHICLE_FAVORITE), img=RES_ICONS.MAPS_ICONS_TOOLTIP_MAIN_TYPE, imgPadding=formatters.packPadding(top=-15), imgAtLeft=False, txtPadding=formatters.packPadding(left=10), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=-28, bottom=-27)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class TelecomBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, valueWidth, leftPadding, rightPadding):
        super(TelecomBlockConstructor, self).__init__(vehicle, None, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        return

    def construct(self):
        if self.vehicle.isTelecom:
            return [formatters.packTextBlockData(text=text_styles.main(TOOLTIPS.VEHICLE_DEAL_TELECOM_MAIN))]
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
        paddings = formatters.packPadding(left=-4)
        neededValue = 0
        actionPrc = 0
        if buyPrice and sellPrice:
            LOG_ERROR('You are not allowed to use buyPrice and sellPrice at the same time')
            return
        else:
            block = []
            isUnlocked = self.vehicle.isUnlocked
            isInInventory = self.vehicle.isInInventory
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
                    block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_XP), value=xPText, icon=icon, valueWidth=self._valueWidth, padding=paddings))
            if dailyXP:
                attrs = g_itemsCache.items.stats.attributes
                if attrs & constants.ACCOUNT_ATTR.DAILY_MULTIPLIED_XP and self.vehicle.dailyXPFactor > 0:
                    dailyXPText = text_styles.main(text_styles.expText('x' + _int(self.vehicle.dailyXPFactor)))
                    block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_DAILYXPFACTOR), value=dailyXPText, icon=ICON_TEXT_FRAMES.DOUBLE_XP_FACTOR, valueWidth=self._valueWidth, padding=paddings))
            if unlockPrice:
                isAvailable, cost, need = getUnlockPrice(self.vehicle.intCD, parentCD)
                if cost > 0:
                    neededValue = None
                    if isAvailable and not isUnlocked and need > 0 and techTreeNode is not None:
                        neededValue = need
                    block.append(makePriceBlock(cost, CURRENCY_SETTINGS.UNLOCK_PRICE, neededValue, valueWidth=self._valueWidth))
            if buyPrice and not (self.vehicle.isDisabledForBuy or self.vehicle.isPremiumIGR or self.vehicle.isTelecom or self.vehicle.isOnlyForEventBattles):
                price = self.vehicle.buyPrice
                money = g_itemsCache.items.stats.money
                actionPrc = self.vehicle.actionPrc
                defaultPrice = self.vehicle.defaultPrice
                currency = price.getCurrency()
                buyPriceText = price.get(currency)
                oldPrice = defaultPrice.get(currency)
                neededValue = price.get(currency) - money.get(currency)
                neededValue = neededValue if neededValue > 0 else None
                if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                    neededValue = None
                block.append(makePriceBlock(buyPriceText, CURRENCY_SETTINGS.getBuySetting(currency), neededValue, oldPrice, actionPrc, valueWidth=self._valueWidth))
            if sellPrice and not (self.vehicle.isTelecom or self.vehicle.isOnlyForEventBattles):
                sellPrice = self.vehicle.sellPrice
                if sellPrice.isSet(Currency.GOLD):
                    sellPriceText = text_styles.gold(_int(sellPrice.gold))
                    sellPriceIcon = ICON_TEXT_FRAMES.GOLD
                else:
                    sellPriceText = text_styles.credits(_int(sellPrice.credits))
                    sellPriceIcon = ICON_TEXT_FRAMES.CREDITS
                block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_SELL_PRICE), value=sellPriceText, icon=sellPriceIcon, valueWidth=self._valueWidth, padding=paddings))
            if minRentPrice and not self.vehicle.isPremiumIGR:
                minRentPricePackage = self.vehicle.getRentPackage()
                if minRentPricePackage:
                    minRentPriceValue = Money(*minRentPricePackage['rentPrice'])
                    minDefaultRentPriceValue = Money(*minRentPricePackage['defaultRentPrice'])
                    actionPrc = self.vehicle.getRentPackageActionPrc(minRentPricePackage['days'])
                    money = g_itemsCache.items.stats.money
                    currency = minRentPriceValue.getCurrency()
                    price = minRentPriceValue.get(currency)
                    oldPrice = minDefaultRentPriceValue.get(currency)
                    neededValue = minRentPriceValue.get(currency) - money.get(currency)
                    neededValue = neededValue if neededValue > 0 else None
                    block.append(makePriceBlock(price, CURRENCY_SETTINGS.getRentSetting(currency), neededValue, oldPrice, actionPrc, valueWidth=self._valueWidth))
            if rentals and not self.vehicle.isPremiumIGR:
                rentFormatter = RentLeftFormatter(self.vehicle.rentInfo)
                rentLeftInfo = rentFormatter.getRentLeftStr('#tooltips:vehicle/rentLeft/%s', formatter=lambda key, countType, count, _=None: {'left': count,
                 'descr': i18n.makeString(key % countType)})
                if rentLeftInfo:
                    block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(rentLeftInfo['descr']), value=text_styles.main(rentLeftInfo['left']), icon=ICON_TEXT_FRAMES.RENTALS, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-4, bottom=-16)))
            notEnoughMoney = neededValue > 0
            hasAction = actionPrc > 0
            return (block, notEnoughMoney or hasAction)


class CommonStatsBlockConstructor(VehicleTooltipBlockConstructor):
    PARAMS = {VEHICLE_CLASS_NAME.LIGHT_TANK: ('enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'circularVisionRadius'),
     VEHICLE_CLASS_NAME.MEDIUM_TANK: ('damageAvgPerMinute', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed'),
     VEHICLE_CLASS_NAME.HEAVY_TANK: ('damageAvg', 'piercingPower', 'hullArmor', 'turretArmor'),
     VEHICLE_CLASS_NAME.SPG: ('damageAvg', 'reloadTimeSecs', 'aimingTime', 'explosionRadius'),
     VEHICLE_CLASS_NAME.AT_SPG: ('piercingPower', 'shotDispersionAngle', 'damageAvgPerMinute', 'speedLimits', 'chassisRotationSpeed'),
     'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        paramsDict = dict(params_helper.getParameters(self.vehicle))
        block = []
        comparator = params_helper.idealCrewComparator(self.vehicle)
        if self.configuration.params:
            for paramName in self.PARAMS.get(self.vehicle.type, 'default'):
                if paramName in paramsDict:
                    paramInfo = comparator.getExtendedData(paramName)
                    fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.BASE_FORMATTERS)
                    if fmtValue is not None:
                        block.append(formatters.packTextParameterBlockData(name=param_formatter.formatVehicleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-1)))

        if len(block) > 0:
            title = text_styles.middleTitle(TOOLTIPS.VEHICLEPARAMS_COMMON_TITLE)
            block.insert(0, formatters.packTextBlockData(title, padding=formatters.packPadding(bottom=8)))
        return block


class SimplifiedStatsBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, leftPadding, rightPadding):
        super(SimplifiedStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)

    def construct(self):
        block = []
        comparator = params_helper.idealCrewComparator(self.vehicle)
        stockParams = params_helper.getParameters(g_itemsCache.items.getStockVehicle(self.vehicle.intCD))
        for paramName in RELATIVE_PARAMS:
            paramInfo = comparator.getExtendedData(paramName)
            fmtValue = param_formatter.simlifiedVehicleParameter(paramInfo)
            if fmtValue is not None:
                block.append(formatters.packStatusDeltaBlockData(title=param_formatter.formatVehicleParamName(paramName), valueStr=fmtValue, statusBarData={'value': paramInfo.value,
                 'delta': 0,
                 'minValue': 0,
                 'markerValue': stockParams[paramName],
                 'maxValue': MAX_RELATIVE_VALUE,
                 'useAnim': False}, showDecreaseArrow=any((penalty[1] != 0 for penalty in paramInfo.penalties)), padding=formatters.packPadding(left=74, top=8)))

        if len(block) > 0:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(_ms(TOOLTIPS.VEHICLEPARAMS_SIMPLIFIED_TITLE)), padding=formatters.packPadding(top=-4)))
        return block


class FootnoteBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, leftPadding, rightPadding):
        super(FootnoteBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)

    def construct(self):
        currentCrewSize = len([ x for _, x in self.vehicle.crew if x is not None ])
        return [formatters.packImageTextBlockData(title='', desc=text_styles.standard(TOOLTIPS.VEHICLE_STATS_FOOTNOTE), img=RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_OFF, imgPadding=formatters.packPadding(top=4), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=20))] if currentCrewSize < len(self.vehicle.descriptor.type.crewRoles) else []


class AdditionalStatsBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(AdditionalStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        block = []
        if self.configuration.crew:
            totalCrewSize = len(self.vehicle.descriptor.type.crewRoles)
            if self.vehicle.isInInventory:
                currentCrewSize = len([ x for _, x in self.vehicle.crew if x is not None ])
                currentCrewSizeStr = str(currentCrewSize)
                if currentCrewSize < totalCrewSize:
                    currentCrewSizeStr = text_styles.error(currentCrewSizeStr)
                block.append(self._makeStatBlock(currentCrewSizeStr, totalCrewSize, TOOLTIPS.VEHICLE_CREW))
            else:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_CREW)), value=text_styles.stats(str(totalCrewSize)), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-2)))
        lockBlock = self._makeLockBlock()
        if lockBlock is not None:
            block.append(lockBlock)
        return block

    def _makeLockBlock(self):
        clanLockTime = self.vehicle.clanLock
        if clanLockTime and clanLockTime <= time_utils.getCurrentTimestamp():
            LOG_DEBUG('clan lock time is less than current time: %s' % clanLockTime)
            clanLockTime = None
        isDisabledInRoaming = self.vehicle.isDisabledInRoaming
        if clanLockTime or isDisabledInRoaming:
            headerLock = text_styles.concatStylesToMultiLine(text_styles.warning(_ms(TOOLTIPS.TANKCARUSEL_LOCK_HEADER)))
            if isDisabledInRoaming:
                textLock = text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROAMING))
            else:
                time = time_utils.getDateTimeFormat(clanLockTime)
                timeStr = text_styles.main(text_styles.concatStylesWithSpace(_ms(TOOLTIPS.TANKCARUSEL_LOCK_TO), time))
                textLock = text_styles.concatStylesToMultiLine(timeStr, text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_CLAN)))
            lockHeaderBlock = formatters.packTextBlockData(headerLock, padding=formatters.packPadding(left=77 + self.leftPadding, top=5))
            lockTextBlock = formatters.packTextBlockData(textLock, padding=formatters.packPadding(left=77 + self.leftPadding))
            return formatters.packBuildUpBlockData([lockHeaderBlock, lockTextBlock], stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LOCK_BG_LINKAGE, padding=formatters.packPadding(left=-17, top=20, bottom=0))
        else:
            return
            return

    def _makeStatBlock(self, current, total, text):
        return formatters.packTextParameterBlockData(name=text_styles.main(_ms(text)), value=text_styles.stats(str(current) + '/' + str(total)), valueWidth=self._valueWidth)


class StatusBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        block = []
        isClanLock = self.vehicle.clanLock or None
        isDisabledInRoaming = self.vehicle.isDisabledInRoaming
        if isClanLock or isDisabledInRoaming:
            return block
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
                if text is not None and len(text) > 0:
                    block.append(formatters.packTextBlockData(text=header))
                    block.append(formatters.packTextBlockData(text=text_styles.standard(text)))
                else:
                    block.append(formatters.packAlignedTextBlockData(header, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
            return block

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
                elif reason == 'credits_error':
                    tooltip = TOOLTIPS.MODULEFITS_CREDITS_ERROR
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
            money = g_itemsCache.items.stats.money
            price = vehicle.minRentPrice or vehicle.buyPrice
            needMoney = price - money
            needMoney = needMoney.toNonNegative()
            msg = None
            level = Vehicle.VEHICLE_STATE_LEVEL.WARNING
            if not isUnlocked:
                msg = 'notUnlocked'
            elif isInInventory:
                msg = 'inHangar'
            elif needMoney:
                currency = needMoney.getCurrency(byWeight=False)
                if currency == Currency.CREDITS:
                    msg = 'notEnoughCredits'
                    level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                elif currency == Currency.GOLD:
                    msg = 'notEnoughGold'
                    level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                else:
                    msg = 'notEnough'
                    level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                    LOG_WARNING('Unsupported currency: ', currency)
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
            isSuitableVeh = getFalloutCtrl().isSuitableVeh(vehicle)
            if not isSuitableVeh:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % Vehicle.VEHICLE_STATE.NOT_SUITABLE)
                level = Vehicle.VEHICLE_STATE_LEVEL.WARNING
            else:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state)
                if header is None and text is None:
                    return
            return {'header': header,
             'text': text,
             'level': level}

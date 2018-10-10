# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/vehicle.py
import collections
import BigWorld
import constants
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, moneyWithIcon, icons
from gui.shared.formatters.time_formatters import RentLeftFormatter, getTimeLeftInfo
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.gui_items.Vehicle import Vehicle, getBattlesLeft, getTypeBigIconPath
from gui.shared.gui_items.fitting_item import RentalInfoProvider
from gui.shared.items_parameters import RELATIVE_PARAMS, formatters as param_formatter, params_helper, bonus_helper
from gui.shared.items_parameters.bonus_helper import isSituationalBonus
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.formatters import isRelativeParameter, SITUATIONAL_SCHEME, EXTRACTED_BONUS_SCHEME
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.money import Currency
from gui.shared.tooltips import formatters, ToolTipBaseData
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makePriceBlock, CURRENCY_SETTINGS
from helpers import i18n, time_utils, int2roman, dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
_EQUIPMENT = 'equipment'
_OPTION_DEVICE = 'optionalDevice'
_BATTLE_BOOSTER = 'battleBooster'
_ARTEFACT_TYPES = (_EQUIPMENT, _OPTION_DEVICE)
_SKILL_BONUS_TYPE = 'skill'
_ROLE_BONUS_TYPE = 'role'
_EXTRA_BONUS_TYPE = 'extra'
_TOOLTIP_MIN_WIDTH = 420
_TOOLTIP_MAX_WIDTH = 460
_TOOLTIP_ANNOUNCEMENT_MAX_WIDTH = 310
_CREW_TOOLTIP_PARAMS = {Tankman.ROLES.COMMANDER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_RECONNAISSANCE,
                           'commanderPercents': '10%',
                           'crewPercents': '1%'},
 Tankman.ROLES.GUNNER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_FIREPOWER},
 Tankman.ROLES.DRIVER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_MOBILITY},
 Tankman.ROLES.RADIOMAN: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_RECONNAISSANCE},
 Tankman.ROLES.LOADER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_FIREPOWER}}

def _bonusCmp(x, y):
    return cmp(x[1], y[1]) or cmp(x[0], y[0])


def _makeModuleFitTooltipError(reason):
    return '#tooltips:moduleFits/{}'.format(reason)


_SHORTEN_TOOLTIP_CASES = ('shopVehicle',)

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
        if telecomBlock:
            items.append(formatters.packBuildUpBlockData(telecomBlock, padding=leftRightPadding))
        priceBlock, invalidWidth = PriceBlockConstructor(vehicle, statsConfig, self.context.getParams(), valueWidth, leftPadding, rightPadding).construct()
        shouldBeCut = self.calledBy and self.calledBy in _SHORTEN_TOOLTIP_CASES
        if priceBlock and not shouldBeCut:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, gap=textGap, padding=blockPadding))
        simplifiedStatsBlock = SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if simplifiedStatsBlock:
            items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        if not vehicle.isRotationGroupLocked:
            commonStatsBlock = CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct()
            if commonStatsBlock:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=textGap, padding=blockPadding))
        footnoteBlock = FootnoteBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if footnoteBlock:
            items.append(formatters.packBuildUpBlockData(footnoteBlock, gap=textGap, padding=blockPadding))
        if vehicle.isRotationGroupLocked:
            statsBlockConstructor = RotationLockAdditionalStatsBlockConstructor
        elif vehicle.isDisabledInRoaming:
            statsBlockConstructor = RoamingLockAdditionalStatsBlockConstructor
        elif vehicle.clanLock and vehicle.clanLock > time_utils.getCurrentTimestamp():
            statsBlockConstructor = ClanLockAdditionalStatsBlockConstructor
        else:
            statsBlockConstructor = AdditionalStatsBlockConstructor
        items.append(formatters.packBuildUpBlockData(statsBlockConstructor(vehicle, paramsConfig, self.context.getParams(), valueWidth, leftPadding, rightPadding).construct(), gap=textGap, padding=blockPadding))
        if not vehicle.isRotationGroupLocked:
            statusBlock, operationError = StatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not (operationError and shouldBeCut):
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding))
            else:
                self._setContentMargin(bottom=bottomPadding)
        return items


class BaseVehicleParametersTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BaseVehicleParametersTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setMargins(11, 14)
        self._setWidth(520)
        self.__paramName = None
        self.__iconPadding = formatters.packPadding(left=6, top=-2)
        self.__titlePadding = formatters.packPadding(left=8)
        self.__listPadding = formatters.packPadding(bottom=6)
        return

    def _packBlocks(self, paramName):
        self._extendedData = self.context.getComparator().getExtendedData(paramName)
        self.__paramName = self._extendedData.name
        return []

    def _getPenalties(self):
        notFullCrew = False
        result = []
        penalties = self._extendedData.penalties
        actualPenalties, _ = _getNumNotNullPenaltyTankman(penalties)
        penaltiesLen = len(penalties)
        numNotNullPenaltyTankman = len(actualPenalties)
        if penaltiesLen > numNotNullPenaltyTankman:
            notFullCrew = True
            result.append(formatters.packTitleDescParameterWithIconBlockData(text_styles.main(_ms(TOOLTIPS.VEHICLEPARAMS_PENALTY_CREWNOTFULL_TEMPLATE)), icon=RES_ICONS.MAPS_ICONS_VEHPARAMS_TOOLTIPS_PENALTIES_ALL, iconPadding=self.__iconPadding, titlePadding=self.__titlePadding, padding=self.__listPadding))
        if numNotNullPenaltyTankman > 0:
            for penalty in penalties:
                valueStr = _formatValueChange(self.__paramName, penalty.value)
                if valueStr:
                    if penalty.vehicleIsNotNative:
                        locKey = TOOLTIPS.VEHICLEPARAMS_PENALTY_TANKMANDIFFERENTVEHICLE_TEMPLATE
                    else:
                        locKey = TOOLTIPS.VEHICLEPARAMS_PENALTY_TANKMANLEVEL_TEMPLATE
                    penaltyStr = text_styles.main(_ms(locKey, tankmanType=_ms(ITEM_TYPES.tankman_roles(penalty.roleName))))
                    result.append(formatters.packTitleDescParameterWithIconBlockData(penaltyStr, text_styles.warning(_ms(TOOLTIPS.VEHICLEPARAMS_TITLE_VALUETEMPLATE, value=valueStr)), icon=param_formatter.getPenaltyIcon(penalty.roleName), iconPadding=self.__iconPadding, titlePadding=self.__titlePadding, padding=self.__listPadding))

        return (notFullCrew, result)


class VehicleSimpleParametersTooltipData(BaseVehicleParametersTooltipData):

    def _packBlocks(self, paramName):
        blocks = super(VehicleSimpleParametersTooltipData, self)._packBlocks(paramName)
        title = text_styles.highTitle(MENU.tank_params(paramName))
        value = param_formatter.colorizedFormatParameter(self._extendedData, self.context.formatters)
        desc = text_styles.main(_ms(TOOLTIPS.tank_params_desc(paramName)))
        comparator = self.context.getComparator()
        icon = param_formatter.getGroupPenaltyIcon(comparator.getExtendedData(paramName), comparator)
        valueLeftPadding = -3 if icon else 6
        blocks.append(formatters.packTitleDescParameterWithIconBlockData(title, text_styles.warning(_ms(TOOLTIPS.VEHICLEPARAMS_TITLE_VALUETEMPLATE, value=value)), icon=icon, desc=desc, valueAtRight=True, iconPadding=formatters.packPadding(left=0, top=6), valuePadding=formatters.packPadding(left=valueLeftPadding, top=4)))
        return blocks


class VehicleAnnouncementParametersTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleAnnouncementParametersTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(_TOOLTIP_ANNOUNCEMENT_MAX_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        announcement = self.context.buildItem(*args, **kwargs)
        items = super(VehicleAnnouncementParametersTooltipData, self)._packBlocks()
        items.append(formatters.packTextBlockData(text_styles.main(_ms(announcement.tooltip))))
        return items


class BaseVehicleAdvancedParametersTooltipData(BaseVehicleParametersTooltipData):

    def _packBlocks(self, paramName):
        blocks = super(BaseVehicleAdvancedParametersTooltipData, self)._packBlocks(paramName)
        title = text_styles.highTitle(MENU.tank_params(paramName))
        title += text_styles.middleTitle(param_formatter.MEASURE_UNITS.get(paramName, ''))
        desc = text_styles.main(_ms(TOOLTIPS.tank_params_desc(paramName)))
        if isRelativeParameter(paramName):
            blocks.append(formatters.packTitleDescBlock(title, desc))
        else:
            blocks.append(formatters.packImageTextBlockData(title, desc, img=param_formatter.getParameterBigIconPath(paramName), imgPadding=formatters.packPadding(top=10, left=1), txtPadding=formatters.packPadding(left=10)))
        return blocks


class VehicleAvgParameterTooltipData(BaseVehicleAdvancedParametersTooltipData):
    _AVG_TO_RANGE_PARAMETER_NAME = {'avgDamage': 'damage',
     'avgPiercingPower': 'piercingPower'}

    def _packBlocks(self, paramName):
        blocks = super(VehicleAvgParameterTooltipData, self)._packBlocks(paramName)
        rangeParamName = self._AVG_TO_RANGE_PARAMETER_NAME[paramName]
        value = self.context.getComparator().getExtendedData(rangeParamName).value
        fmtValue = param_formatter.formatParameter(rangeParamName, value)
        blocks.append(formatters.packBuildUpBlockData([formatters.packTextParameterBlockData(text_styles.main(_ms(TOOLTIPS.getAvgParameterCommentKey(rangeParamName), units=_ms(param_formatter.MEASURE_UNITS.get(rangeParamName)))), text_styles.stats(fmtValue), valueWidth=80)]))
        return blocks


def _packBonusName(bnsType, bnsId, enabled=True, inactive=False):
    itemStr = None
    textStyle = text_styles.main if enabled else text_styles.standard
    if bnsType in (_EQUIPMENT, _OPTION_DEVICE):
        itemStr = textStyle(_ms('#artefacts:%s/name' % bnsId))
    elif bnsType == _SKILL_BONUS_TYPE:
        itemStr = textStyle(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_SKILL_TEMPLATE, name=_ms(ITEM_TYPES.tankman_skills(bnsId)), type=text_styles.standard(_ms(TOOLTIPS.VEHICLEPARAMS_SKILL_NAME))))
    elif bnsType == _ROLE_BONUS_TYPE:
        itemStr = textStyle(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_ROLE_TEMPLATE, name=_ms(TOOLTIPS.vehicleparams_bonus_tankmanlevel(bnsId))))
    elif bnsType == _EXTRA_BONUS_TYPE:
        itemStr = textStyle(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_ROLE_TEMPLATE, name=_ms(TOOLTIPS.vehicleparams_bonus_extra(bnsId))))
    elif bnsType == _BATTLE_BOOSTER:
        itemStr = textStyle(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_BATTLEBOOSTER_TEMPLATE, name=_ms('#artefacts:{boosterId}/name'.format(boosterId=bnsId))))
    if inactive:
        itemStr += _ms(TOOLTIPS.VEHICLEPARAMS_BONUS_POSSIBLE_ISINACTIVE)
        icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_RED, 16, 16, 0, 2)
        itemStr = param_formatter.packSituationalIcon(itemStr, icon)
    elif not enabled:
        itemStr += _ms(TOOLTIPS.VEHICLEPARAMS_BONUS_POSSIBLE_NOTINSTALLED)
    return textStyle(itemStr)


class VehicleAdvancedParametersTooltipData(BaseVehicleAdvancedParametersTooltipData):

    def __init__(self, context):
        super(VehicleAdvancedParametersTooltipData, self).__init__(context)
        self.__paramName = None
        self.__iconPadding = formatters.packPadding(left=6, top=-2)
        self.__titlePadding = formatters.packPadding(left=8)
        self.__listPadding = formatters.packPadding(bottom=6)
        self.__iconDisabledAlpha = 0.5
        return

    def _packBlocks(self, paramName):
        blocks = super(VehicleAdvancedParametersTooltipData, self)._packBlocks(paramName)
        self.__paramName = self._extendedData.name
        bonuses, hasSituational = self._getBonuses()
        self._packListBlock(blocks, bonuses, text_styles.warning(_ms(TOOLTIPS.VEHICLEPARAMS_BONUSES_TITLE)))
        notFullCrew, penalties = self._getPenalties()
        if notFullCrew:
            blocks.append(formatters.packImageTextBlockData(title='', desc=text_styles.standard(TOOLTIPS.VEHICLE_STATS_FOOTNOTE), img=RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_OFF, imgPadding=formatters.packPadding(top=4), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=20)))
        self._packListBlock(blocks, penalties, text_styles.critical(_ms(TOOLTIPS.VEHICLEPARAMS_PENALTIES_TITLE)))
        if self._extendedData.inactiveBonuses:
            blocks.append(formatters.packBuildUpBlockData(self._getFootNoteBlock('inactive'), padding=0))
        if hasSituational:
            blocks.append(formatters.packBuildUpBlockData(self._getFootNoteBlock('optional'), padding=0))
        return blocks

    def _packListBlock(self, blocks, listBlock, title):
        if listBlock:
            titlePadding = formatters.packPadding(bottom=15)
            listPadding = formatters.packPadding(left=90)
            blockPadding = formatters.packPadding(left=5, top=15, bottom=5)
            blocks.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(title, padding=titlePadding), formatters.packBuildUpBlockData(listBlock, padding=listPadding)], padding=blockPadding))

    def _getFootNoteBlock(self, noteType):
        if noteType == 'optional':
            desc = text_styles.standard(TOOLTIPS.VEHICLEPARAMS_BONUS_SITUATIONAL)
            img = RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_OPTIONAL
        else:
            conditionsToActivate = set(self._extendedData.inactiveBonuses.values())
            conditionsToActivate = [ _ms(ITEM_TYPES.tankman_skills(bnsID)) for bnsID, _ in conditionsToActivate ]
            desc = text_styles.standard(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_INACTIVEDESCRIPTION, skillName=', '.join(conditionsToActivate)))
            img = RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_RED
        return [formatters.packImageTextBlockData(title='', desc=desc, img=img, imgPadding=formatters.packPadding(left=4, top=3), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=20))]

    def _getBonuses(self):
        result = []
        bonuses = sorted(self._extendedData.bonuses, cmp=_bonusCmp)
        item = self.context.buildItem()
        bonusExtractor = bonus_helper.BonusExtractor(item, bonuses, self.__paramName)
        hasSituational = False
        for bnsType, bnsId, pInfo in bonusExtractor.getBonusInfo():
            isSituational = isSituationalBonus(bnsId)
            scheme = SITUATIONAL_SCHEME if isSituational else EXTRACTED_BONUS_SCHEME
            valueStr = param_formatter.formatParameterDelta(pInfo, scheme)
            if valueStr is not None:
                hasSituational = hasSituational or isSituational
                bonusName = _packBonusName(bnsType, bnsId)
                if isSituational:
                    icon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_TOOLTIP_ASTERISK_OPTIONAL, 16, 16, 0, 2)
                    bonusName = param_formatter.packSituationalIcon(bonusName, icon)
                    titlePadding = formatters.packPadding(left=8, top=-2)
                else:
                    titlePadding = self.__titlePadding
                result.append(self.__packBonusField(bnsId, bonusName, value=_ms(TOOLTIPS.VEHICLEPARAMS_TITLE_VALUETEMPLATE, value=valueStr), padding=titlePadding))

        possibleBonuses = sorted(self._extendedData.possibleBonuses, cmp=_bonusCmp)
        inactiveBonuses = self._extendedData.inactiveBonuses
        for bnsId, bnsType in possibleBonuses:
            isInactive = (bnsId, bnsType) in inactiveBonuses
            result.append(self.__packBonusField(bnsId, _packBonusName(bnsType, bnsId, enabled=False, inactive=isInactive), isDisabled=True))

        return (result, hasSituational)

    def __packBonusField(self, bonusID, name, value='', isDisabled=False, padding=None):
        return formatters.packTitleDescParameterWithIconBlockData(name, value=value, icon=param_formatter.getBonusIcon(bonusID), iconAlpha=self.__iconDisabledAlpha if isDisabled else 1, iconPadding=self.__iconPadding, titlePadding=padding or self.__titlePadding, padding=self.__listPadding)


class VehicleListDescParameterTooltipData(BaseVehicleAdvancedParametersTooltipData):

    def __init__(self, context):
        super(VehicleListDescParameterTooltipData, self).__init__(context)
        self.__paramName = None
        return

    def _packBlocks(self, paramName):
        blocks = super(VehicleListDescParameterTooltipData, self)._packBlocks(paramName)
        self.__paramName = self._extendedData.name
        blocks.append(formatters.packTextBlockData(text_styles.main(TOOLTIPS.TANK_PARAMS_DESC_EFFECTIVEARMORDESC)))
        return blocks


class VehiclePreviewCrewMemberTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehiclePreviewCrewMemberTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(360)
        self._setMargins(13, 13)

    def _packBlocks(self, role):
        blocks = []
        bodyStr = '%s/%s' % (TOOLTIPS.VEHICLEPREVIEW_CREW, role)
        crewParams = {k:text_styles.neutral(v) for k, v in _CREW_TOOLTIP_PARAMS[role].iteritems()}
        blocks.append(formatters.packTitleDescBlock(text_styles.highTitle(ITEM_TYPES.tankman_roles(role)), text_styles.main(_ms(bodyStr, **crewParams))))
        vehicle = self.context.getVehicle()
        for idx, tankman in vehicle.crew:
            if tankman.role == role:
                otherRoles = list(vehicle.descriptor.type.crewRoles[idx])
                otherRoles.remove(tankman.role)
                if otherRoles:
                    rolesStr = ', '.join([ text_styles.stats(_ms(ITEM_TYPES.tankman_roles(r))) for r in otherRoles ])
                    blocks.append(formatters.packTextBlockData(text_styles.main(_ms(TOOLTIPS.VEHICLEPREVIEW_CREW_ADDITIONALROLES, roles=rolesStr))))

        return blocks


class VehicleTradeInTooltipData(ToolTipBaseData):
    tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self, context):
        super(VehicleTradeInTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)

    def getDisplayableData(self, *args, **kwargs):
        vehicle = self.context.buildItem(*args, **kwargs)
        tradeInInfo = self.tradeIn.getTradeInInfo(vehicle)
        if tradeInInfo is None:
            discount = i18n.makeString(TOOLTIPS.TRADE_NODISCOUNT)
        else:
            discountValue = moneyWithIcon(tradeInInfo.maxDiscountPrice, currType=Currency.GOLD)
            if tradeInInfo.hasMultipleTradeOffs:
                discountValue = i18n.makeString(TOOLTIPS.TRADE_SEVERALDISCOUNTS, discountValue=discountValue)
            discount = i18n.makeString(TOOLTIPS.TRADE_DISCOUNT, discountValue=discountValue)
        return {'header': i18n.makeString(TOOLTIPS.TRADE_HEADER),
         'body': i18n.makeString(TOOLTIPS.TRADE_BODY, discount=discount)}


class VehicleTradeInPriceTooltipData(ToolTipBaseData):
    tradeIn = dependency.descriptor(ITradeInController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(VehicleTradeInPriceTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)

    def getDisplayableData(self, tradeInVehicleCD, tradeOffVehicleCD):
        if tradeInVehicleCD < 0:
            return {}
        tradeInVehicle = self.context.buildItem(tradeInVehicleCD)
        itemPrice = tradeInVehicle.buyPrices.itemPrice
        statsMoney = self.itemsCache.items.stats.money
        bodyParts = []
        if tradeInVehicle.buyPrices.itemPrice.isActionPrice():
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_OLDPRICE, gold=moneyWithIcon(itemPrice.defPrice, currType=Currency.GOLD), statsMoney=statsMoney))
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_NEWPRICE, gold=moneyWithIcon(itemPrice.price, currType=Currency.GOLD, statsMoney=statsMoney)))
        else:
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_PRICE, gold=moneyWithIcon(itemPrice.price, currType=Currency.GOLD, statsMoney=statsMoney)))
        if tradeOffVehicleCD < 0:
            tradeOffVehicleName = i18n.makeString(TOOLTIPS.TRADE_VEHICLE_NOVEHICLE)
            resultPrice = itemPrice.price
        else:
            tradeOffVehicle = self.context.buildItem(tradeOffVehicleCD)
            tradeOffVehicleName = tradeOffVehicle.userName
            resultPrice = itemPrice.price - tradeOffVehicle.tradeOffPrice
        bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_TOCHANGE, vehicleName=text_styles.playerOnline(tradeOffVehicleName)))
        return {'header': i18n.makeString(TOOLTIPS.TRADE_VEHICLE_HEADER, vehicleName=tradeInVehicle.userName),
         'body': '\n'.join(bodyParts),
         'result': i18n.makeString(TOOLTIPS.TRADE_VEHICLE_RESULT, gold=moneyWithIcon(resultPrice, currType=Currency.GOLD, statsMoney=statsMoney))}


class VehicleTooltipBlockConstructor(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, configuration, leftPadding=20, rightPadding=20):
        self.vehicle = vehicle
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding

    def construct(self):
        return None


class HeaderBlockConstructor(VehicleTooltipBlockConstructor):

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
        icon = getTypeBigIconPath(self.vehicle.type, self.vehicle.isElite)
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc=text_styles.concatStylesToMultiLine(levelStr + ' ' + typeStr, ''), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-2, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        if self.vehicle.isFavorite:
            headerBlocks.append(formatters.packImageTextBlockData(title=text_styles.neutral(TOOLTIPS.VEHICLE_FAVORITE), img=RES_ICONS.MAPS_ICONS_TOOLTIP_MAIN_TYPE, imgPadding=formatters.packPadding(top=-15), imgAtLeft=False, txtPadding=formatters.packPadding(left=10), txtAlign=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=-28, bottom=-27)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class TelecomBlockConstructor(VehicleTooltipBlockConstructor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehicle, valueWidth, leftPadding, rightPadding):
        super(TelecomBlockConstructor, self).__init__(vehicle, None, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        return

    def construct(self):
        if self.vehicle.isTelecom:
            serverSettings = self.lobbyContext.getServerSettings()
            provider = BigWorld.player().inventory.getProviderForVehInvId(self.vehicle.invID, serverSettings)
            telecomText = _ms(TOOLTIPS.VEHICLE_DEAL_TELECOM_MAIN, tariff=_ms(MENU.internetProviderTariff(provider)), provider=_ms(MENU.internetProviderName(provider)))
            return [formatters.packTextBlockData(text=text_styles.main(telecomText))]
        return []


class PriceBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, params, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._rentExpiryTime = params.get('rentExpiryTime')
        self._rentBattlesLeft = params.get('rentBattlesLeft')
        self._rentWinsLeft = params.get('rentWinsLeft')

    def construct(self):
        xp = self.configuration.xp
        dailyXP = self.configuration.dailyXP
        buyPrice = self.configuration.buyPrice
        sellPrice = self.configuration.sellPrice
        unlockPrice = self.configuration.unlockPrice
        techTreeNode = self.configuration.node
        minRentPrice = self.configuration.minRentPrice
        rentals = self.configuration.rentals
        futureRentals = self.configuration.futureRentals
        paddings = formatters.packPadding(left=-5)
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
                isNextToUnlock = bool(int(techTreeNode.state) & NODE_STATE_FLAGS.NEXT_2_UNLOCK)
                parentCD = techTreeNode.unlockProps.parentID
            if xp:
                xpValue = self.vehicle.xp
                if xpValue:
                    xPText = text_styles.expText(BigWorld.wg_getIntegralFormat(xpValue))
                    icon = ICON_TEXT_FRAMES.ELITE_XP if self.vehicle.isPremium else ICON_TEXT_FRAMES.XP
                    block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_XP), value=xPText, icon=icon, valueWidth=self._valueWidth, padding=paddings))
            if dailyXP:
                attrs = self.itemsCache.items.stats.attributes
                if attrs & constants.ACCOUNT_ATTR.DAILY_MULTIPLIED_XP and self.vehicle.dailyXPFactor > 0:
                    dailyXPText = text_styles.main(text_styles.expText('x' + BigWorld.wg_getIntegralFormat(self.vehicle.dailyXPFactor)))
                    block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_DAILYXPFACTOR), value=dailyXPText, icon=ICON_TEXT_FRAMES.DOUBLE_XP_FACTOR, valueWidth=self._valueWidth, padding=paddings))
            if unlockPrice:
                isAvailable, cost, need = getUnlockPrice(self.vehicle.intCD, parentCD)
                if cost > 0:
                    neededValue = None
                    if isAvailable and not isUnlocked and need > 0 and techTreeNode is not None:
                        neededValue = need
                    block.append(makePriceBlock(cost, CURRENCY_SETTINGS.UNLOCK_PRICE, neededValue, valueWidth=self._valueWidth))
            if buyPrice:
                if self.vehicle.isRestorePossible():
                    price = self.vehicle.restorePrice
                    defaultPrice = price
                    currency = price.getCurrency()
                    buyPriceText = price.get(currency)
                    oldPrice = defaultPrice.get(currency)
                    neededValue = _getNeedValue(price, currency)
                    if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                        neededValue = None
                    block.append(makePriceBlock(buyPriceText, CURRENCY_SETTINGS.RESTORE_PRICE, neededValue, oldPrice, actionPrc, valueWidth=self._valueWidth))
                    if self.vehicle.hasLimitedRestore():
                        timeKey, formattedTime = getTimeLeftInfo(self.vehicle.restoreInfo.getRestoreTimeLeft(), None)
                        block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main('#tooltips:vehicle/restoreLeft/%s' % timeKey), value=text_styles.main(formattedTime), icon=ICON_TEXT_FRAMES.ALERT if timeKey == 'hours' else ICON_TEXT_FRAMES.EMPTY, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5)))
                elif not (self.vehicle.isDisabledForBuy or self.vehicle.isPremiumIGR or self.vehicle.isTelecom):
                    itemPrice = self.vehicle.buyPrices.itemPrice
                    price = itemPrice.price
                    actionPrc = itemPrice.getActionPrc()
                    defaultPrice = itemPrice.defPrice
                    currency = price.getCurrency()
                    buyPriceText = price.get(currency)
                    oldPrice = defaultPrice.get(currency)
                    neededValue = _getNeedValue(price, currency)
                    if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                        neededValue = None
                    block.append(makePriceBlock(buyPriceText, CURRENCY_SETTINGS.getBuySetting(currency), neededValue, oldPrice, actionPrc, valueWidth=self._valueWidth))
            if sellPrice and not self.vehicle.isTelecom:
                sellPrice = self.vehicle.sellPrices.itemPrice.price
                sellCurrency = sellPrice.getCurrency(byWeight=True)
                currencyTextFormatter = getattr(text_styles, sellCurrency, text_styles.credits)
                sellPriceText = currencyTextFormatter(BigWorld.wg_getIntegralFormat(sellPrice.get(sellCurrency, 0)))
                sellPriceIcon = sellCurrency
                block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_SELL_PRICE), value=sellPriceText, icon=sellPriceIcon, valueWidth=self._valueWidth, padding=paddings))
            if minRentPrice and not self.vehicle.isPremiumIGR:
                minRentPricePackage = self.vehicle.getRentPackage()
                if minRentPricePackage:
                    minRentPriceValue = minRentPricePackage['rentPrice']
                    minDefaultRentPriceValue = minRentPricePackage['defaultRentPrice']
                    actionPrc = self.vehicle.getRentPackageActionPrc(minRentPricePackage['days'])
                    currency = minRentPriceValue.getCurrency()
                    price = minRentPriceValue.getSignValue(currency)
                    oldPrice = minDefaultRentPriceValue.getSignValue(currency)
                    neededValue = _getNeedValue(minRentPriceValue, currency)
                    block.append(makePriceBlock(price, CURRENCY_SETTINGS.getRentSetting(currency), neededValue, oldPrice, actionPrc, valueWidth=self._valueWidth))
                    if not self.vehicle.isRented or self.vehicle.rentalIsOver:
                        block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main('#tooltips:vehicle/rentAvailable'), value='', icon=ICON_TEXT_FRAMES.RENTALS, valueWidth=self._valueWidth, padding=paddings))
            if rentals and not self.vehicle.isPremiumIGR:
                if futureRentals:
                    rentLeftKey = '#tooltips:vehicle/rentLeftFuture/%s'
                    rentInfo = RentalInfoProvider(time=self._rentExpiryTime, battles=self._rentBattlesLeft, wins=self._rentWinsLeft, isRented=True)
                else:
                    rentLeftKey = '#tooltips:vehicle/rentLeft/%s'
                    rentInfo = self.vehicle.rentInfo
                rentFormatter = RentLeftFormatter(rentInfo)
                rentLeftInfo = rentFormatter.getRentLeftStr(rentLeftKey, formatter=lambda key, countType, count, _=None: {'left': count,
                 'descr': i18n.makeString(key % countType)})
                if rentLeftInfo:
                    block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(rentLeftInfo['descr']), value=text_styles.main(rentLeftInfo['left']), icon=ICON_TEXT_FRAMES.RENTALS, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5, bottom=-16)))
            if self.vehicle.canTradeIn:
                block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_TRADE), value='', icon=ICON_TEXT_FRAMES.TRADE, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-5, bottom=-10)))
            notEnoughMoney = neededValue > 0
            hasAction = actionPrc > 0
            return (block, notEnoughMoney or hasAction)


class CommonStatsBlockConstructor(VehicleTooltipBlockConstructor):
    PARAMS = {VEHICLE_CLASS_NAME.LIGHT_TANK: ('enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'circularVisionRadius'),
     VEHICLE_CLASS_NAME.MEDIUM_TANK: ('avgDamagePerMinute', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed'),
     VEHICLE_CLASS_NAME.HEAVY_TANK: ('avgDamage', 'avgPiercingPower', 'hullArmor', 'turretArmor'),
     VEHICLE_CLASS_NAME.SPG: ('avgDamage', 'stunMinDuration', 'stunMaxDuration', 'reloadTimeSecs', 'aimingTime', 'explosionRadius'),
     VEHICLE_CLASS_NAME.AT_SPG: ('avgPiercingPower', 'shotDispersionAngle', 'avgDamagePerMinute', 'speedLimits', 'chassisRotationSpeed', 'switchTime'),
     'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        paramsDict = params_helper.getParameters(self.vehicle)
        block = []
        comparator = params_helper.idealCrewComparator(self.vehicle)
        if self.configuration.params and not self.configuration.simplifiedOnly:
            for paramName in self.PARAMS.get(self.vehicle.type, 'default'):
                if paramName in paramsDict:
                    paramInfo = comparator.getExtendedData(paramName)
                    fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.BASE_SCHEME)
                    if fmtValue is not None:
                        block.append(formatters.packTextParameterBlockData(name=param_formatter.formatVehicleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-1)))

        if block:
            title = text_styles.middleTitle(TOOLTIPS.VEHICLEPARAMS_COMMON_TITLE)
            block.insert(0, formatters.packTextBlockData(title, padding=formatters.packPadding(bottom=8)))
        return block


class SimplifiedStatsBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        block = []
        if self.configuration.params:
            comparator = params_helper.idealCrewComparator(self.vehicle)
            stockParams = params_helper.getParameters(self.itemsCache.items.getStockVehicle(self.vehicle.intCD))
            for paramName in RELATIVE_PARAMS:
                paramInfo = comparator.getExtendedData(paramName)
                fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.NO_BONUS_SIMPLIFIED_SCHEME)
                if fmtValue is not None:
                    buffIconSrc = ''
                    if self.vehicle.isInInventory:
                        buffIconSrc = param_formatter.getGroupPenaltyIcon(paramInfo, comparator)
                    block.append(formatters.packStatusDeltaBlockData(title=param_formatter.formatVehicleParamName(paramName), valueStr=fmtValue, statusBarData=SimplifiedBarVO(value=paramInfo.value, markerValue=stockParams[paramName]), buffIconSrc=buffIconSrc, padding=formatters.packPadding(left=74, top=8)))

        if block:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(_ms(TOOLTIPS.VEHICLEPARAMS_SIMPLIFIED_TITLE)), padding=formatters.packPadding(top=-4)))
        return block


class FootnoteBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        if self.configuration.params and not self.configuration.simplifiedOnly:
            currentCrewSize = len([ x for _, x in self.vehicle.crew if x is not None ])
            if currentCrewSize < len(self.vehicle.descriptor.type.crewRoles):
                return [formatters.packImageTextBlockData(title='', desc=text_styles.standard(TOOLTIPS.VEHICLE_STATS_FOOTNOTE), img=RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_OFF, imgPadding=formatters.packPadding(top=4), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=20))]
        return []


class AdditionalStatsBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, params, valueWidth, leftPadding, rightPadding):
        super(AdditionalStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._roleLevel = params.get('tmanRoleLevel')

    def construct(self):
        block = []
        if self.configuration.crew:
            totalCrewSize = len(self.vehicle.descriptor.type.crewRoles)
            if self.configuration.externalCrewParam and self._roleLevel is not None:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_CREW_AWARD, self._roleLevel)), value=text_styles.stats(str(totalCrewSize)), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-2)))
            elif self.vehicle.isInInventory and not self.configuration.externalCrewParam:
                currentCrewSize = len([ x for _, x in self.vehicle.crew if x is not None ])
                currentCrewSizeStr = str(currentCrewSize)
                if currentCrewSize < totalCrewSize:
                    currentCrewSizeStr = text_styles.error(currentCrewSizeStr)
                block.append(self._makeStatBlock(currentCrewSizeStr, totalCrewSize, TOOLTIPS.VEHICLE_CREW))
            else:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_CREW)), value=text_styles.stats(str(totalCrewSize)), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-2)))
        return block

    def _makeStatBlock(self, current, total, text):
        return formatters.packTextParameterBlockData(name=text_styles.main(_ms(text)), value=text_styles.stats(str(current) + '/' + str(total)), valueWidth=self._valueWidth)


class LockAdditionalStatsBlockConstructor(AdditionalStatsBlockConstructor):

    def construct(self):
        block = super(LockAdditionalStatsBlockConstructor, self).construct()
        lockBlock = self._makeLockBlock()
        if lockBlock is not None:
            block.append(lockBlock)
        return block

    def _makeLockBlock(self):
        header = self._makeLockHeader()
        text = self._makeLockText()
        headerPadding = formatters.packPadding(left=77 + self.leftPadding, top=5)
        textPadding = formatters.packPadding(left=77 + self.leftPadding)
        headerBlock = formatters.packTextBlockData(header, padding=headerPadding)
        textBlock = formatters.packTextBlockData(text, padding=textPadding)
        return formatters.packBuildUpBlockData([headerBlock, textBlock], stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LOCK_BG_LINKAGE, padding=formatters.packPadding(left=-17, top=20, bottom=0))

    def _makeLockHeader(self):
        return text_styles.warning(_ms(TOOLTIPS.TANKCARUSEL_LOCK_HEADER))

    def _makeLockText(self):
        pass


class RotationLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockHeader(self):
        return text_styles.warning(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROTATION_HEADER, groupNum=self.vehicle.rotationGroupNum))

    def _makeLockText(self):
        return text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROTATION, battlesToUnlock=text_styles.highlightText(self.vehicle.rotationBattlesLeft), unlockedBy=text_styles.highlightText(', '.join((str(groupNum) for groupNum in self.vehicle.unlockedBy)))))


class RoamingLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockText(self):
        return text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROAMING))


class ClanLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockText(self):
        clanLockTime = self.vehicle.clanLock
        time = time_utils.getDateTimeFormat(clanLockTime)
        timeStr = text_styles.main(text_styles.concatStylesWithSpace(_ms(TOOLTIPS.TANKCARUSEL_LOCK_TO), time))
        return text_styles.concatStylesToMultiLine(timeStr, text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_CLAN)))


class StatusBlockConstructor(VehicleTooltipBlockConstructor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def construct(self):
        block = []
        isClanLock = self.vehicle.clanLock or None
        isDisabledInRoaming = self.vehicle.isDisabledInRoaming
        if isClanLock or isDisabledInRoaming:
            return (block, False)
        else:
            if self.configuration.node is not None:
                result = self.__getTechTreeVehicleStatus(self.configuration, self.vehicle)
            elif self.configuration.isAwardWindow:
                result = None
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
                if text:
                    block.append(formatters.packTextBlockData(text=header))
                    block.append(formatters.packTextBlockData(text=text_styles.standard(text)))
                else:
                    block.append(formatters.packAlignedTextBlockData(header, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
            return (block, result and result.get('operationError') is not None)

    def __getTechTreeVehicleStatus(self, config, vehicle):
        nodeState = int(config.node.state)
        tooltip, level = None, Vehicle.VEHICLE_STATE_LEVEL.WARNING
        parentCD = None
        if config.node is not None:
            parentCD = config.node.unlockProps.parentID
        _, _, need2Unlock = getUnlockPrice(vehicle.intCD, parentCD)
        if not nodeState & NODE_STATE_FLAGS.UNLOCKED:
            if not nodeState & NODE_STATE_FLAGS.NEXT_2_UNLOCK:
                tooltip = TOOLTIPS.RESEARCHPAGE_VEHICLE_STATUS_PARENTMODULEISLOCKED
            elif need2Unlock > 0:
                tooltip = TOOLTIPS.RESEARCHPAGE_MODULE_STATUS_NOTENOUGHXP
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
        else:
            if nodeState & NODE_STATE_FLAGS.IN_INVENTORY:
                return self.__getVehicleStatus(False, vehicle)
            mayObtain, reason = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
            if not mayObtain:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                if GUI_ITEM_ECONOMY_CODE.isMoneyError(reason):
                    tooltip = _makeModuleFitTooltipError(reason)
                else:
                    tooltip = TOOLTIPS.MODULEFITS_OPERATION_ERROR
        header, text = getComplexStatus(tooltip)
        return None if header is None and text is None else {'header': header,
         'text': text,
         'level': level}

    def __getVehicleStatus(self, showCustomStates, vehicle):
        if showCustomStates:
            isInInventory = vehicle.isInInventory
            level = Vehicle.VEHICLE_STATE_LEVEL.WARNING
            if not isInInventory and vehicle.hasRestoreCooldown() and vehicle.isHidden:
                timeKey, formattedTime = getTimeLeftInfo(self.vehicle.restoreInfo.getRestoreCooldownTimeLeft())
                return {'header': _ms('#tooltips:vehicleStatus/restoreCooldown/%s' % timeKey, time=formattedTime),
                 'text': '',
                 'level': level}
            isUnlocked = vehicle.isUnlocked
            mayObtain, reason = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
            msg = None
            operationError = False
            if not isUnlocked:
                msg = 'notUnlocked'
            elif isInInventory:
                msg = 'inHangar'
            elif not mayObtain:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                if reason == GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_GOLD:
                    msg = 'notEnoughGold'
                elif reason == GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CREDITS:
                    msg = 'notEnoughCredits'
                else:
                    msg = 'operationError'
                    operationError = True
            if msg:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % msg)
                return {'header': header,
                 'text': text,
                 'level': level,
                 'operationError': operationError}
            return
        else:
            state, level = vehicle.getState()
            if state == Vehicle.VEHICLE_STATE.SERVER_RESTRICTION:
                return
            if state == Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state, groupNum=vehicle.rotationGroupNum, battlesLeft=getBattlesLeft(vehicle))
            elif state == Vehicle.VEHICLE_STATE.DEAL_IS_OVER:
                serverSettings = self.lobbyContext.getServerSettings()
                provider = BigWorld.player().inventory.getProviderForVehInvId(vehicle.invID, serverSettings)
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state, provider=_ms(MENU.internetProviderName(provider)))
            else:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state)
                if header is None and text is None:
                    return
            return {'header': header,
             'text': text,
             'level': level}


def _getNumNotNullPenaltyTankman(penalties):
    nullPenaltyTypes = []
    actualPenalties = []
    for penalty in penalties:
        if penalty.value != 0:
            actualPenalties.append(penalty)
        nullPenaltyTypes.append(penalty.roleName)

    return (actualPenalties, nullPenaltyTypes)


def _formatValueChange(paramName, value):
    if not param_formatter.isRelativeParameter(paramName):
        if isinstance(value, collections.Sized):
            state = zip([PARAM_STATE.WORSE] * len(value), value)
        else:
            state = (PARAM_STATE.WORSE, value)
        valueStr = param_formatter.formatParameter(paramName, value, state, colorScheme=param_formatter.BASE_SCHEME, formatSettings=param_formatter.DELTA_PARAMS_SETTING, allowSmartRound=False)
        return valueStr or ''
    else:
        return ''


def _getNeedValue(price, currency):
    itemsCache = dependency.instance(IItemsCache)
    money = itemsCache.items.stats.money
    neededValue = price.getSignValue(currency) - money.getSignValue(currency)
    return neededValue if neededValue > 0 else None

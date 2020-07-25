# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/vehicle.py
import collections
import logging
import constants
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import getItemUnlockPricesVO, getItemRestorePricesVO, getItemSellPricesVO, getMoneyVO
from gui.shared.gui_items.gui_item_economics import getMinRentItemPrice
from gui.shared.formatters import text_styles, moneyWithIcon, icons, getItemPricesVO
from gui.shared.formatters.time_formatters import RentLeftFormatter, getTimeLeftInfo
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE, KPI
from gui.shared.gui_items.Tankman import Tankman, getRoleUserName, CrewTypes
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.gui_items.Vehicle import Vehicle, getBattlesLeft, getTypeBigIconPath
from gui.shared.gui_items.fitting_item import RentalInfoProvider
from gui.shared.items_parameters import RELATIVE_PARAMS, params_helper
from gui.shared.items_parameters import formatters as param_formatter
from gui.shared.items_parameters.bonus_helper import isSituationalBonus
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.formatters import isRelativeParameter, SITUATIONAL_SCHEME, EXTRACTED_BONUS_SCHEME
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.money import Currency
from gui.shared.tooltips import formatters, ToolTipBaseData
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makeCompoundPriceBlock, CURRENCY_SETTINGS
from gui.shared.utils import MAX_STEERING_LOCK_ANGLE, WHEELED_SWITCH_TIME, WHEELED_SPEED_MODE_SPEED, DUAL_GUN_CHARGE_TIME, TURBOSHAFT_SPEED_MODE_SPEED
from helpers import i18n, time_utils, int2roman, dependency
from helpers.i18n import makeString as _ms
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ITradeInController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from items import perks
_logger = logging.getLogger(__name__)
_EQUIPMENT = 'equipment'
_OPTION_DEVICE = 'optionalDevice'
_BATTLE_BOOSTER = 'battleBooster'
_IS_SENIORITY = 'isSeniority'
_ARTEFACT_TYPES = (_EQUIPMENT, _OPTION_DEVICE)
_SKILL_BONUS_TYPE = 'skill'
_PERK_BONUS_TYPE = 'perk'
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
_MULTI_KPI_PARAMS = frozenset(['vehicleRepairSpeed',
 'vehicleRamOrExplosionDamageResistance',
 'vehicleGunShotDispersion',
 'crewHitChance',
 'crewRepeatedStunDuration',
 'vehicleChassisStrength',
 'vehicleChassisFallDamage',
 'vehicleChassisRepairSpeed',
 'vehicleAmmoBayEngineFuelStrength',
 'vehicleFireChance',
 'demaskFoliageFactor',
 'demaskMovingFactor'])

def _bonusCmp(x, y):
    return cmp(x[1], y[1]) or cmp(x[0], y[0])


def _makeModuleFitTooltipError(reason):
    return '#tooltips:moduleFits/{}'.format(reason)


_SHORTEN_TOOLTIP_CASES = ('shopVehicle',)

class VehicleInfoTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)
    __bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self, context):
        super(VehicleInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=12, right=20)
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
        bottomPadding = 12
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 75
        textGap = -2
        headerItems = [formatters.packBuildUpBlockData(HeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding, blockWidth=410), formatters.packBuildUpBlockData(self._getCrewIconBlock(), gap=2, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=34, right=0), blockWidth=20)]
        headerBlockItems = [formatters.packBuildUpBlockData(headerItems, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-16))]
        telecomBlock = TelecomBlockConstructor(vehicle, valueWidth, leftPadding, rightPadding).construct()
        if telecomBlock:
            headerBlockItems.append(formatters.packBuildUpBlockData(telecomBlock, padding=leftRightPadding))
        self.__createStatusBlock(vehicle, headerBlockItems, statsConfig, paramsConfig, valueWidth)
        items.append(formatters.packBuildUpBlockData(headerBlockItems, gap=-4, padding=formatters.packPadding(bottom=-8)))
        if vehicle.isEarnCrystals:
            crystalBlock, linkage = CrystalBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct()
            if crystalBlock:
                items.append(formatters.packBuildUpBlockData(crystalBlock, linkage=linkage, padding=leftRightPadding))
        simplifiedStatsBlock = SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if simplifiedStatsBlock:
            items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        if not vehicle.isRotationGroupLocked:
            commonStatsBlock = CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct()
            if commonStatsBlock:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=textGap, padding=blockPadding))
        statsBlockConstructor = None
        if vehicle.isRotationGroupLocked:
            statsBlockConstructor = RotationLockAdditionalStatsBlockConstructor
        elif vehicle.isDisabledInRoaming:
            statsBlockConstructor = RoamingLockAdditionalStatsBlockConstructor
        elif vehicle.clanLock and vehicle.clanLock > time_utils.getCurrentTimestamp():
            statsBlockConstructor = ClanLockAdditionalStatsBlockConstructor
        if statsBlockConstructor is not None:
            items.append(formatters.packBuildUpBlockData(statsBlockConstructor(vehicle, paramsConfig, self.context.getParams(), valueWidth, leftPadding, rightPadding).construct(), gap=textGap, padding=blockPadding))
        priceBlock, invalidWidth = PriceBlockConstructor(vehicle, statsConfig, self.context.getParams(), valueWidth, leftPadding, rightPadding).construct()
        shouldBeCut = self.calledBy and self.calledBy in _SHORTEN_TOOLTIP_CASES or vehicle.isOnlyForEpicBattles
        if priceBlock and not shouldBeCut:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, gap=5, padding=formatters.packPadding(left=98), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL))
        if not vehicle.isRotationGroupLocked:
            statusBlock, operationError = StatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not (operationError and shouldBeCut):
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding, blockWidth=440))
            else:
                self._setContentMargin(bottom=bottomPadding)
        if self.context.getParams().get(_IS_SENIORITY, False):
            awardCrewAndHangarBlock = AwardCrewAndHangar(vehicle, paramsConfig, leftPadding, rightPadding).construct()
            if awardCrewAndHangarBlock:
                items.append(formatters.packBuildUpBlockData(awardCrewAndHangarBlock))
        return items

    def _getCrewIconBlock(self):
        block = []
        vehicle = self.item
        crewSorted = sorted(vehicle.crew, key=lambda tankman: tankman[1], reverse=True)
        for _, tankman in crewSorted:
            tImg = RES_ICONS.MAPS_ICONS_MESSENGER_ICONCONTACTS
            tAlpha = 0.5 if tankman is not None else 0.25
            block.append(formatters.packImageBlockData(img=tImg, alpha=tAlpha))

        return block

    def __createStatusBlock(self, vehicle, items, statsConfig, paramsConfig, valueWidth):
        ctxParams = self.context.getParams()
        frontlineBlock = FrontlineRentBlockConstructor(vehicle, statsConfig, ctxParams, valueWidth, leftPadding=20, rightPadding=20).construct()
        if frontlineBlock:
            items.append(formatters.packBuildUpBlockData(frontlineBlock, gap=-4, padding=formatters.packPadding(left=25, right=20, top=0, bottom=-11)))
        if vehicle.canTradeIn and not self.__bootcamp.isInBootcamp():
            items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_TRADE), value='', icon=ICON_TEXT_FRAMES.TRADE, valueWidth=valueWidth, padding=formatters.packPadding(left=-5, top=0, bottom=-10)))
        if not vehicle.isPremiumIGR and not frontlineBlock and vehicle.getRentPackage() and (vehicle.rentalIsOver or not vehicle.isRented):
            items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main('#tooltips:vehicle/rentAvailable'), value='', icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, valueWidth=valueWidth, padding=formatters.packPadding(left=-5, top=0, bottom=-10)))
        if statsConfig.rentals and not vehicle.isPremiumIGR and not frontlineBlock:
            if statsConfig.futureRentals:
                rentLeftKey = '#tooltips:vehicle/rentLeftFuture/%s'
                rentInfo = RentalInfoProvider(time=ctxParams.get('rentExpiryTime'), battles=ctxParams.get('rentBattlesLeft'), wins=ctxParams.get('rentWinsLeft'), seasonRent=ctxParams.get('rentSeason'), isRented=True)
            else:
                rentLeftKey = '#tooltips:vehicle/rentLeft/%s'
                rentInfo = vehicle.rentInfo
            rentFormatter = RentLeftFormatter(rentInfo)
            rentLeftInfo = rentFormatter.getRentLeftStr(rentLeftKey, formatter=lambda key, countType, count, _=None: {'left': count,
             'descr': i18n.makeString(key % countType)})
            if rentLeftInfo:
                items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(rentLeftInfo['descr']), value=text_styles.main(rentLeftInfo['left']), icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, gap=0, valueWidth=valueWidth, padding=formatters.packPadding(left=0, bottom=-10)))
        if statsConfig.showRankedBonusBattle:
            items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(backport.text(R.strings.tooltips.vehicle.rankedBonusBattle())), value='', icon=ICON_TEXT_FRAMES.BONUS_BATTLE, iconYOffset=2, valueWidth=valueWidth, gap=0, padding=formatters.packPadding(left=0, top=-2, bottom=5)))
        if statsConfig.dailyXP:
            attrs = self.__itemsCache.items.stats.attributes
            if attrs & constants.ACCOUNT_ATTR.DAILY_MULTIPLIED_XP and vehicle.dailyXPFactor > 0:
                dailyXPText = text_styles.main(text_styles.expText(''.join(('x', backport.getIntegralFormat(vehicle.dailyXPFactor)))))
                items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_DAILYXPFACTOR), value=dailyXPText, icon=ICON_TEXT_FRAMES.DOUBLE_XP_FACTOR, iconYOffset=2, valueWidth=valueWidth, gap=0, padding=formatters.packPadding(left=2, top=-2, bottom=5)))
        if statsConfig.restorePrice:
            if vehicle.isRestorePossible() and vehicle.hasLimitedRestore():
                timeKey, formattedTime = getTimeLeftInfo(vehicle.restoreInfo.getRestoreTimeLeft(), None)
                items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(''.join(('#tooltips:vehicle/restoreLeft/', timeKey))), value=text_styles.stats(formattedTime), icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, gap=0, valueWidth=valueWidth, padding=formatters.packPadding(left=0, bottom=-10)))
        return


class BaseVehicleParametersTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BaseVehicleParametersTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setMargins(11, 14)
        self._setWidth(520)
        self._paramName = None
        self.__iconPadding = formatters.packPadding(left=6, top=-2)
        self.__titlePadding = formatters.packPadding(left=8)
        self.__listPadding = formatters.packPadding(bottom=6)
        return

    def _packData(self, paramName):
        comparator = self.context.getComparator()
        self._hasPerksBonuses = comparator.hasBonusOfType(constants.BonusTypes.PERK)
        self._extendedData = comparator.getExtendedData(paramName)
        self._paramName = self._extendedData.name

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
                valueStr = _formatValueChange(self._paramName, penalty.value)
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
        isExtraParam = KPI.Name.hasValue(paramName)
        if isExtraParam:
            title = text_styles.highTitle(backport.text(R.strings.menu.extraParams.header(), paramName=backport.text(R.strings.tank_setup.kpi.bonus.dyn(paramName)())))
            desc = text_styles.main(backport.text(R.strings.menu.extraParams.name.dyn(paramName, R.strings.menu.extraParams.desc)()))
        else:
            title = text_styles.highTitle(MENU.tank_params(paramName))
            title += '&nbsp;'
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
        self._packData(paramName)
        rangeParamName = self._AVG_TO_RANGE_PARAMETER_NAME[paramName]
        value = self.context.getComparator().getExtendedData(rangeParamName).value
        fmtValue = param_formatter.formatParameter(rangeParamName, value)
        blocks.append(formatters.packBuildUpBlockData([formatters.packTextParameterBlockData(text_styles.main(_ms(TOOLTIPS.getAvgParameterCommentKey(rangeParamName), units=_ms(param_formatter.MEASURE_UNITS.get(rangeParamName)))), text_styles.stats(fmtValue), valueWidth=80)]))
        return blocks


def _getBonusID(bnsType, bnsId):
    return bnsId.split('_tier')[0] if bnsType == _OPTION_DEVICE else bnsId


def _packBonusName(bnsType, bnsId, enabled=True, inactive=False):
    itemStr = None
    textStyle = text_styles.main if enabled else text_styles.standard
    if bnsType in (_EQUIPMENT, _OPTION_DEVICE):
        itemStr = textStyle(_ms('#artefacts:%s/name' % bnsId))
    elif bnsType == _SKILL_BONUS_TYPE:
        itemStr = textStyle(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_SKILL_TEMPLATE, name=_ms(ITEM_TYPES.tankman_skills(bnsId)), type=text_styles.standard(_ms(TOOLTIPS.VEHICLEPARAMS_SKILL_NAME))))
    elif bnsType == _PERK_BONUS_TYPE:
        cache = perks.g_cache.perks()
        perkItem = cache.perks[int(bnsId)]
        itemStr = textStyle(_ms(TOOLTIPS.VEHICLEPARAMS_BONUS_PERK_TEMPLATE, name=perkItem.name, type=text_styles.standard(_ms(TOOLTIPS.VEHICLEPARAMS_SKILL_NAME))))
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
    elif not enabled and not bnsType == _PERK_BONUS_TYPE:
        itemStr += _ms(TOOLTIPS.VEHICLEPARAMS_BONUS_POSSIBLE_NOTINSTALLED)
    return textStyle(itemStr)


class VehicleAdvancedParametersTooltipData(BaseVehicleAdvancedParametersTooltipData):

    def __init__(self, context):
        super(VehicleAdvancedParametersTooltipData, self).__init__(context)
        self.__iconPadding = formatters.packPadding(left=6, top=-2)
        self.__titlePadding = formatters.packPadding(left=8)
        self.__listPadding = formatters.packPadding(bottom=6)
        self.__iconDisabledAlpha = 0.5

    def _packBlocks(self, paramName):
        blocks = super(VehicleAdvancedParametersTooltipData, self)._packBlocks(paramName)
        self._packData(paramName)
        bonuses, hasSituational = self._getBonuses()
        self._packListBlock(blocks, bonuses, text_styles.warning(_ms(TOOLTIPS.VEHICLEPARAMS_BONUSES_TITLE)))
        notFullCrew, penalties = self._getPenalties()
        if notFullCrew:
            blocks.append(formatters.packImageTextBlockData(title='', desc=text_styles.standard(TOOLTIPS.VEHICLE_STATS_FOOTNOTE), img=RES_ICONS.MAPS_ICONS_LIBRARY_STORE_CONDITION_OFF, imgPadding=formatters.packPadding(top=4), txtGap=-4, txtOffset=20, padding=formatters.packPadding(left=59, right=20)))
        self._packListBlock(blocks, penalties, text_styles.critical(_ms(TOOLTIPS.VEHICLEPARAMS_PENALTIES_TITLE)))
        if len(self._extendedData.bonuses) > 1 and paramName in _MULTI_KPI_PARAMS:
            blocks.append(formatters.packTextBlockData(text_styles.standard(backport.text(R.strings.menu.extraParams.multiDesc()))))
        if self._extendedData.inactiveBonuses:
            blocks.append(formatters.packBuildUpBlockData(self._getFootNoteBlock('inactive'), padding=0))
        if hasSituational:
            blocks.append(formatters.packBuildUpBlockData(self._getFootNoteBlock('optional'), padding=0))
        return blocks

    def _packListBlock(self, blocks, listBlock, title):
        if listBlock:
            titlePadding = formatters.packPadding(bottom=15)
            listPadding = formatters.packPadding(left=90)
            blockPadding = formatters.packPadding(left=5, bottom=-15)
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
        item = self.context.buildItem()
        if item is None:
            return (result, False)
        else:
            bonuses = sorted(self._extendedData.bonuses, cmp=_bonusCmp)
            bonusExtractor = self.context.getBonusExtractor(item, bonuses, self._paramName)
            hasSituational = False
            for bnsType, bnsId, pInfo in bonusExtractor.getBonusInfo():
                bnsId = _getBonusID(bnsType, bnsId)
                isSituational = isSituationalBonus(bnsId, bnsType)
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

            perksController = item.getPerksController()
            if perksController:
                perksController.restore()
            possibleBonuses = sorted(self._extendedData.possibleBonuses, cmp=_bonusCmp)
            inactiveBonuses = self._extendedData.inactiveBonuses
            for bnsId, bnsType in possibleBonuses:
                if bnsType == constants.BonusTypes.PERK and not self._hasPerksBonuses:
                    continue
                tirelessBnsId = _getBonusID(bnsType, bnsId)
                isInactive = (bnsId, bnsType) in inactiveBonuses
                result.append(self.__packBonusField(tirelessBnsId, _packBonusName(bnsType, tirelessBnsId, enabled=False, inactive=isInactive), isDisabled=True))

            return (result, hasSituational)

    def __packBonusField(self, bonusID, name, value='', isDisabled=False, padding=None):
        return formatters.packTitleDescParameterWithIconBlockData(name, value=value, icon=param_formatter.getBonusIcon(bonusID), iconAlpha=self.__iconDisabledAlpha if isDisabled else 1, iconPadding=self.__iconPadding, titlePadding=padding or self.__titlePadding, padding=self.__listPadding)


class VehicleListDescParameterTooltipData(BaseVehicleAdvancedParametersTooltipData):

    def _packBlocks(self, paramName):
        blocks = super(VehicleListDescParameterTooltipData, self)._packBlocks(paramName)
        blocks.append(formatters.packTextBlockData(text_styles.main(TOOLTIPS.TANK_PARAMS_DESC_EFFECTIVEARMORDESC)))
        return blocks


class DefaultCrewMemberTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(DefaultCrewMemberTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(360)
        self._setMargins(13, 13)

    def _packBlocks(self, role):
        blocks = []
        bodyStr = '{}/{}'.format(TOOLTIPS.VEHICLEPREVIEW_CREW, role)
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


class VehiclePreviewCrewMemberTooltipData(DefaultCrewMemberTooltipData):

    def __init__(self, context):
        super(VehiclePreviewCrewMemberTooltipData, self).__init__(context)
        self._setWidth(295)

    def _packBlocks(self, role, name, vehicleName, icon, description, skillsItems, *args, **kwargs):
        blocks = []
        defaultBlocks = super(VehiclePreviewCrewMemberTooltipData, self)._packBlocks(role)
        roleStr = getRoleUserName(role)
        if name and icon:
            bodyStr = '{}, {}'.format(roleStr, vehicleName)
            blocks.append(formatters.packImageTextBlockData(title=text_styles.highTitle(name), desc=text_styles.main(bodyStr)))
            blocks.append(formatters.packImageBlockData(img=icon, padding=formatters.packPadding(left=63)))
            blocks.append(formatters.packSeparatorBlockData())
            if description:
                blocks.append(formatters.packTextBlockData(text_styles.main(description), useHtml=True, padding=formatters.packPadding(top=20, bottom=7)))
        else:
            blocks.extend(defaultBlocks)
        if skillsItems:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.VEHICLEPREVIEW_TANKMAN_SKILLSTITLE), padding=formatters.packPadding(top=10, bottom=10)))
            for skillItem in skillsItems:
                blocks.append(formatters.packImageTextBlockData(img=skillItem[0], title=text_styles.main(skillItem[1]), txtPadding=formatters.packPadding(left=10), titleAtMiddle=True))

        return [formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=10))]


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
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(VehicleTradeInPriceTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)

    def getDisplayableData(self, tradeInVehicleCD, tradeOffVehicleCD):
        if tradeInVehicleCD < 0:
            return {}
        tradeInVehicle = self.context.buildItem(tradeInVehicleCD)
        itemPrice = tradeInVehicle.buyPrices.itemPrice
        bodyParts = []
        if tradeInVehicle.buyPrices.itemPrice.isActionPrice():
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_OLDPRICE, gold=moneyWithIcon(itemPrice.defPrice, currType=Currency.GOLD)))
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_NEWPRICE, gold=moneyWithIcon(itemPrice.price, currType=Currency.GOLD)))
        else:
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_PRICE, gold=moneyWithIcon(itemPrice.price, currType=Currency.GOLD)))
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
         'result': i18n.makeString(TOOLTIPS.TRADE_VEHICLE_RESULT, gold=moneyWithIcon(resultPrice, currType=Currency.GOLD))}


class VehicleStatusTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleStatusTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        vehicle = self.context.buildItem(*args, **kwargs)
        items = super(VehicleStatusTooltipData, self)._packBlocks()
        statusConfig = self.context.getStatusConfiguration(vehicle)
        if not vehicle.isRotationGroupLocked:
            statusBlock, operationError = StatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not operationError:
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=formatters.packPadding(bottom=-16)))
        return items


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
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc=text_styles.concatStylesToMultiLine(levelStr + ' ' + typeStr, ''), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-9, txtOffset=99, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class CrystalBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        block = []
        current, limit = self.vehicle.getCrystalsEarnedInfo()
        icon = backport.image(R.images.gui.maps.icons.library.crystal_23x22())
        linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_VIOLET_LINKAGE
        imgPaddingLeft = -4
        imgPaddingTop = 0
        if current == 0:
            title = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.common.title())
            limitStatus = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.common.description(), max=text_styles.stats(limit))
        elif current >= limit:
            daysLeft = time_utils.getServerRegionalDaysLeftInGameWeek() * time_utils.ONE_DAY
            timeLeft = daysLeft + time_utils.getDayTimeLeft()
            timeLeftStr = time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUESHORT, isRoundUp=True, removeLeadingZeros=True)
            title = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.limitReached.title())
            limitStatus = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.limitReached.description(), timeLeft=text_styles.neutral(timeLeftStr))
            icon = backport.image(R.images.gui.maps.icons.library.time_icon())
            linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_GRAY_LINKAGE
            imgPaddingLeft = 4
            imgPaddingTop = 4
        else:
            title = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.progress.title())
            limitStatus = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.progress.description(), current=text_styles.stats(current), max=limit)
        block.append(formatters.packTextBlockData(text_styles.middleTitle(title), padding=formatters.packPadding(top=-4)))
        block.append(formatters.packImageTextBlockData(img=icon, desc=text_styles.main(limitStatus), imgPadding=formatters.packPadding(left=imgPaddingLeft, top=imgPaddingTop, right=6), padding=formatters.packPadding(left=54, top=3, bottom=4), titleAtMiddle=True))
        if 0 < current < limit:
            block.append(formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_EPIC_PROGRESS_BLOCK_LINKAGE, data={'value': current,
             'maxValue': limit}, padding=formatters.packPadding(top=-5, left=82, bottom=8), blockWidth=304))
        return (block, linkage)


class TelecomBlockConstructor(VehicleTooltipBlockConstructor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehicle, valueWidth, leftPadding, rightPadding):
        super(TelecomBlockConstructor, self).__init__(vehicle, None, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        return

    def construct(self):
        if self.vehicle.isTelecom:
            telecomConfig = self.lobbyContext.getServerSettings().telecomConfig
            provider = telecomConfig.getInternetProvider(self.vehicle.intCD)
            providerLocRes = R.strings.menu.internet_provider.dyn(provider)
            telecomTextRes = R.strings.tooltips.vehicle.deal.telecom.main.dyn(provider, R.strings.tooltips.vehicle.deal.telecom.main.default)
            return [formatters.packTextBlockData(text=text_styles.main(backport.text(telecomTextRes(), tariff=backport.text(providerLocRes.tariff()) if providerLocRes else '', provider=backport.text(providerLocRes.name()) if providerLocRes else '')))]
        return []


class PriceBlockConstructor(VehicleTooltipBlockConstructor):
    bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self, vehicle, configuration, params, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._rentExpiryTime = params.get('rentExpiryTime')
        self._rentBattlesLeft = params.get('rentBattlesLeft')
        self._rentWinsLeft = params.get('rentWinsLeft')
        self._rentSeason = params.get('rentSeason')

    def construct(self):
        xp = self.configuration.xp
        buyPrice = self.configuration.buyPrice
        sellPrice = self.configuration.sellPrice
        unlockPrice = self.configuration.unlockPrice
        techTreeNode = self.configuration.node
        minRentPrice = self.configuration.minRentPrice
        neededValue = 0
        actionPrc = 0
        block = []
        vehicle = self.vehicle
        isUnlocked = vehicle.isUnlocked
        isInInventory = vehicle.isInInventory
        isNextToUnlock = False
        parentCD = None
        if techTreeNode is not None:
            isNextToUnlock = bool(int(techTreeNode.state) & NODE_STATE_FLAGS.NEXT_2_UNLOCK)
            parentCD = int(techTreeNode.unlockProps.parentID) or None
        if xp:
            xpValue = vehicle.xp
            if isUnlocked and not vehicle.getRentPackage() or vehicle.isRestorePossible() or vehicle.isInInventory:
                xPText = text_styles.expTextBig(backport.getIntegralFormat(xpValue))
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_ELITEXPICONBIG if vehicle.isElite or vehicle.isPremium else RES_ICONS.MAPS_ICONS_LIBRARY_XPICONBIG_2
                xpBlock = [formatters.packTextBlockData(text_styles.main(TOOLTIPS.VEHICLE_XP)), formatters.packImageTextBlockData(title=xPText, img=icon, imgPadding=formatters.packPadding(left=0, top=4), imgAtLeft=False, snapImage=True, txtGap=-2, txtOffset=0, padding=formatters.packPadding(top=-4, bottom=0))]
                block.append(formatters.packBuildUpBlockData(xpBlock, blockWidth=150, padding=formatters.packPadding(bottom=-8)))
        if unlockPrice:
            isAvailable, cost, need, defCost, discount = getUnlockPrice(vehicle.intCD, parentCD, vehicle.level)
            if not isUnlocked and cost >= 0:
                neededValue = None
                if isAvailable and not isUnlocked and need > 0 and techTreeNode is not None:
                    neededValue = need
                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.UNLOCK_PRICE, getItemUnlockPricesVO(UnlockProps(parentID=-1, unlockIdx=0, xpCost=cost, discount=discount, xpFullCost=defCost, required=set()))))
        if minRentPrice and vehicle.isRentAvailable:
            if not (vehicle.isRented or vehicle.isRestorePossible() or vehicle.isPremiumIGR):
                minRentItemPrice = getMinRentItemPrice(vehicle)
                if minRentItemPrice is not None:
                    actionPrc = minRentItemPrice.getActionPrc()
                    currency = minRentItemPrice.getCurrency()
                    neededValue = _getNeedValue(minRentItemPrice.price, currency)
                    block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.getRentSetting(currency), getItemPricesVO(minRentItemPrice)))
        if sellPrice:
            if isInInventory and not (vehicle.isRentable or vehicle.isRented or vehicle.isTelecom):
                sellPrice = vehicle.sellPrices.itemPrice.price
                sellCurrency = sellPrice.getCurrency(byWeight=True)
                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.SELL_PRICE, getItemSellPricesVO(sellCurrency, sellPrice)))
        if buyPrice:
            if vehicle.isRestorePossible():
                price = vehicle.restorePrice
                currency = price.getCurrency()
                neededValue = _getNeedValue(price, currency)
                if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                    neededValue = None
                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.RESTORE_PRICE, getItemRestorePricesVO(price)))
            elif not isInInventory or vehicle.isRentable or vehicle.isRented and not (vehicle.isDisabledForBuy or vehicle.isPremiumIGR or vehicle.isTelecom):
                itemPrice = vehicle.buyPrices.itemPrice
                price = itemPrice.price
                currency = price.getCurrency()
                neededValue = _getNeedValue(price, currency)
                if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                    neededValue = None
                if self.bootcamp.isInBootcamp():
                    itemPricesVO = [{'price': getMoneyVO(itemPrice.price)}]
                    actionPrc = 0
                else:
                    itemPricesVO = getItemPricesVO(itemPrice)
                    actionPrc = itemPrice.getActionPrc()
                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.getBuySetting(currency), itemPricesVO))
        notEnoughMoney = neededValue > 0
        hasAction = actionPrc > 0
        return (block, notEnoughMoney or hasAction)


class FrontlineRentBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, params, valueWidth, leftPadding, rightPadding):
        super(FrontlineRentBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._rentExpiryTime = params.get('rentExpiryTime')
        self._rentBattlesLeft = params.get('rentBattlesLeft')
        self._rentWinsLeft = params.get('rentWinsLeft')
        self._rentSeason = params.get('rentSeason')

    def construct(self):
        block = []
        rentals = self.configuration.rentals
        futureRentals = self.configuration.futureRentals
        paddings = formatters.packPadding(left=-5, bottom=4)
        if rentals and not self.vehicle.isPremiumIGR:
            if futureRentals:
                rentLeftKey = '#tooltips:vehicle/rentLeftFuture/%s'
                rentInfo = RentalInfoProvider(time=self._rentExpiryTime, battles=self._rentBattlesLeft, wins=self._rentWinsLeft, seasonRent=self._rentSeason, isRented=True)
            else:
                rentLeftKey = '#tooltips:vehicle/rentLeft/%s'
                rentInfo = self.vehicle.rentInfo
            if self.vehicle.isOnlyForEpicBattles:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_DEAL_EPIC_MAIN), value='', valueWidth=self._valueWidth, padding=paddings))
                if rentInfo.getActiveSeasonRent() is not None:
                    rentFormatter = RentLeftFormatter(rentInfo)
                    rentLeftInfo = rentFormatter.getRentLeftStr(rentLeftKey)
                    if rentLeftInfo:
                        block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.neutral(rentLeftInfo), value='', icon=ICON_TEXT_FRAMES.RENTALS, valueWidth=self._valueWidth, padding=paddings))
                return block
        return


class CommonStatsBlockConstructor(VehicleTooltipBlockConstructor):
    PARAMS = {VEHICLE_CLASS_NAME.LIGHT_TANK: ('enginePowerPerTon',
                                     'speedLimits',
                                     WHEELED_SPEED_MODE_SPEED,
                                     'chassisRotationSpeed',
                                     MAX_STEERING_LOCK_ANGLE,
                                     WHEELED_SWITCH_TIME,
                                     'circularVisionRadius'),
     VEHICLE_CLASS_NAME.MEDIUM_TANK: ('avgDamagePerMinute',
                                      'enginePowerPerTon',
                                      'speedLimits',
                                      TURBOSHAFT_SPEED_MODE_SPEED,
                                      'chassisRotationSpeed'),
     VEHICLE_CLASS_NAME.HEAVY_TANK: ('avgDamage',
                                     'avgPiercingPower',
                                     'hullArmor',
                                     'turretArmor',
                                     DUAL_GUN_CHARGE_TIME),
     VEHICLE_CLASS_NAME.SPG: ('avgDamage', 'stunMinDuration', 'stunMaxDuration', 'reloadTimeSecs', 'aimingTime', 'explosionRadius'),
     VEHICLE_CLASS_NAME.AT_SPG: ('avgPiercingPower', 'shotDispersionAngle', 'avgDamagePerMinute', 'speedLimits', 'chassisRotationSpeed', 'switchTime'),
     'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        paramsDict = params_helper.getParameters(self.vehicle)
        block = []
        highlightPossible = False
        if self.vehicle.descriptor.hasTurboshaftEngine:
            serverSettings = dependency.instance(ISettingsCore).serverSettings
            highlightPossible = serverSettings.checkTurboshaftHighlights(increase=True)
        comparator = params_helper.idealCrewComparator(self.vehicle)
        if self.configuration.params and not self.configuration.simplifiedOnly:
            for paramName in self.PARAMS.get(self.vehicle.type, 'default'):
                if paramName in paramsDict:
                    paramInfo = comparator.getExtendedData(paramName)
                    fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.BASE_SCHEME)
                    if fmtValue is not None:
                        block.append(formatters.packTextParameterBlockData(name=param_formatter.formatVehicleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-1), highlight=highlightPossible and paramName in (TURBOSHAFT_SPEED_MODE_SPEED,)))

        if block:
            title = text_styles.middleTitle(TOOLTIPS.VEHICLEPARAMS_COMMON_TITLE)
            block.insert(0, formatters.packTextBlockData(title, padding=formatters.packPadding(bottom=8)))
        return block


class AwardCrewAndHangar(VehicleTooltipBlockConstructor):

    def construct(self):
        block = []
        if self.configuration.params:
            leftPaddingImg = 30
            leftPaddingTxtCrew = 2
            leftPaddingTxtSlot = leftPaddingTxtCrew + 30
            block.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.SENIORITYAWARDS_ADDITIONAL_TOOLTIP_HEADER), padding=formatters.packPadding(left=20)))
            block.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(_ms(TOOLTIPS.CUSTOMCREW_REFERRAL_BODY, value=CrewTypes.SKILL_100)), img=RES_ICONS.MAPS_ICONS_CREWBUNDLES_BONUSES_BASICROLEBOOST_100, imgPadding=formatters.packPadding(left=leftPaddingImg, top=10), txtPadding=formatters.packPadding(left=leftPaddingTxtCrew, top=20)))
            block.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(TOOLTIPS.SENIORITYAWARDS_HANGARSLOT_TOOLTIP_HEADER), img=RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_SLOTS, imgPadding=formatters.packPadding(left=leftPaddingImg, top=10), txtPadding=formatters.packPadding(left=leftPaddingTxtSlot, top=20)))
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
                    delta = 0
                    state, diff = paramInfo.state
                    if state == PARAM_STATE.WORSE:
                        delta = -abs(diff)
                    block.append(formatters.packStatusDeltaBlockData(title=param_formatter.formatVehicleParamName(paramName), valueStr=fmtValue, statusBarData=SimplifiedBarVO(value=paramInfo.value, delta=delta, markerValue=stockParams[paramName]), buffIconSrc=buffIconSrc, padding=formatters.packPadding(left=74, top=8)))

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
        return text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROTATION, battlesToUnlock=text_styles.stats(self.vehicle.rotationBattlesLeft), unlockedBy=text_styles.stats(', '.join((str(groupNum) for groupNum in self.vehicle.unlockedBy)))))


class RoamingLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockText(self):
        return text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROAMING))


class ClanLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockText(self):
        clanLockTime = self.vehicle.clanLock
        time = backport.getDateTimeFormat(clanLockTime)
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
                elif statusLevel in (Vehicle.VEHICLE_STATE_LEVEL.RENTED, Vehicle.VEHICLE_STATE_LEVEL.RENTABLE):
                    headerFormatter = text_styles.warning
                else:
                    _logger.error('Unknown status type "%s"!', statusLevel)
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
            parentCD = int(config.node.unlockProps.parentID) or None
        _, _, need2Unlock, _, _ = getUnlockPrice(vehicle.intCD, parentCD, vehicle.level)
        if not nodeState & NODE_STATE_FLAGS.UNLOCKED and not nodeState & NODE_STATE_FLAGS.COLLECTIBLE:
            level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
            if not nodeState & NODE_STATE_FLAGS.NEXT_2_UNLOCK:
                tooltip = TOOLTIPS.RESEARCHPAGE_VEHICLE_STATUS_PARENTMODULEISLOCKED
            elif need2Unlock > 0:
                tooltip = TOOLTIPS.RESEARCHPAGE_MODULE_STATUS_NOTENOUGHXP
        else:
            if nodeState & NODE_STATE_FLAGS.IN_INVENTORY:
                return self.__getVehicleStatus(False, vehicle)
            mayObtain, reason = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
            if not mayObtain:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                if GUI_ITEM_ECONOMY_CODE.isCurrencyError(reason):
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
                telecomConfig = self.lobbyContext.getServerSettings().telecomConfig
                provider = telecomConfig.getInternetProvider(vehicle.intCD)
                providerLocRes = R.strings.menu.internet_provider.dyn(provider)
                keyString = '#tooltips:vehicleStatus/{}'.format(state)
                if provider != '':
                    keyString = keyString + '/{}'.format(provider)
                header, text = getComplexStatus(keyString, provider=backport.text(providerLocRes.name()) if providerLocRes else '')
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

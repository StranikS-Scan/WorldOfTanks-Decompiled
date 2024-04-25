# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/tooltips/vehicle.py
from itertools import chain
import constants
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.items_parameters import RELATIVE_PARAMS, params_helper
from gui.shared.items_parameters import formatters as param_formatter
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.tooltips import formatters
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.utils import MAX_STEERING_LOCK_ANGLE, WHEELED_SWITCH_TIME, WHEELED_SPEED_MODE_SPEED, SHOT_DISPERSION_ANGLE, DUAL_GUN_CHARGE_TIME, TURBOSHAFT_SPEED_MODE_SPEED, ROCKET_ACCELERATION_SPEED_LIMITS, DUAL_ACCURACY_COOLING_DELAY
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
_TOOLTIP_MIN_WIDTH = 420

class HBVehicleInfoTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)
    _LEFT_PADDING = 20
    _RIGHT_PADDING = 20

    def __init__(self, context):
        super(HBVehicleInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=12, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(args[0], **kwargs)
        items = super(HBVehicleInfoTooltipData, self)._packBlocks()
        vehicle = self.item
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        leftPadding = self._LEFT_PADDING
        rightPadding = self._RIGHT_PADDING
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        valueWidth = 77
        textGap = -2
        headerItems = [formatters.packBuildUpBlockData(HeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding, blockWidth=410), formatters.packBuildUpBlockData(self._getCrewIconBlock(), gap=2, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=34, right=0), blockWidth=20)]
        headerBlockItems = [formatters.packBuildUpBlockData(headerItems, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-16))]
        items.append(formatters.packBuildUpBlockData(headerBlockItems, gap=-4, padding=formatters.packPadding(bottom=-12)))
        simplifiedStatsBlock = SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if simplifiedStatsBlock:
            items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        if not vehicle.isRotationGroupLocked:
            commonStatsBlock = CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct()
            if commonStatsBlock:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=textGap, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=-3)))
        isLocked = args[1]
        if vehicle.level > 1 and isLocked:
            items.append(formatters.packBuildUpBlockData([formatters.packTitleDescParameterWithIconBlockData(title=text_styles.statusAttention(backport.text(R.strings.hb_tooltips.vehicleInfoTooltip.locked.title())), icon=backport.image(R.images.historical_battles.gui.maps.icons.library.lock()), iconPadding=formatters.packPadding(top=-2, left=20)), formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.hb_tooltips.vehicleInfoTooltip.locked.descr())), padding=formatters.packPadding(left=18, top=4))]))
        return items

    def _getCrewIconBlock(self):
        block = []
        vehicle = self.item
        crewSorted = sorted(vehicle.crew, key=lambda tankman: tankman[1], reverse=True)
        for _, __ in crewSorted:
            tImg = RES_ICONS.MAPS_ICONS_MESSENGER_ICONCONTACTS
            block.append(formatters.packImageBlockData(img=tImg, alpha=0.5))

        return block


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
        vehicleType = self.vehicle.type.replace('-', '_')
        if self.vehicle.isElite and self.vehicle.level > 1:
            vehicleType = backport.text(R.strings.hb_tooltips.vehicleInfoTooltip.elite.dyn(vehicleType)())
        else:
            vehicleType = backport.text(R.strings.hb_tooltips.vehicleInfoTooltip.normal.dyn(vehicleType)())
        vehicleType = backport.text(R.strings.menu.roleExp.roleLabel()) + ' ' + vehicleType
        icon = getTypeBigIconPath(self.vehicle.type, self.vehicle.isElite and self.vehicle.level > 1)
        bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_ELITE_VEHICLE_BG_LINKAGE
        headerBlocks.append(formatters.packImageTextBlockData(title=text_styles.highTitle(self.vehicle.userName), desc=text_styles.main(vehicleType), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-1, txtOffset=101, padding=formatters.packPadding(top=15, bottom=-15)))
        if self.vehicle.isElite and self.vehicle.level > 1:
            headerBlocks.append(formatters.packTitleDescParameterWithIconBlockData(title=text_styles.main(backport.text(R.strings.hb_tooltips.vehicleInfoTooltip.elite.descr())), value=text_styles.stats(backport.text(R.strings.hb_tooltips.vehicleInfoTooltip.elite.modifier())), icon=backport.image(R.images.historical_battles.gui.maps.icons.library.offence()), padding=formatters.packPadding(left=80), titlePadding=formatters.packPadding(left=5), iconPadding=formatters.packPadding(top=3, left=1)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
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
                    block.append(formatters.packStatusDeltaBlockData(title=param_formatter.formatVehicleParamName(paramName), valueStr=fmtValue, statusBarData=SimplifiedBarVO(value=paramInfo.value, delta=delta, markerValue=stockParams[paramName]), buffIconSrc=buffIconSrc, padding=formatters.packPadding(left=76, top=8)))

        if block:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.vehicleParams.simplified.title())), padding=formatters.packPadding(top=-4)))
        return block


class CommonStatsBlockConstructor(VehicleTooltipBlockConstructor):
    PARAMS = {VEHICLE_CLASS_NAME.LIGHT_TANK: ('enginePowerPerTon',
                                     'speedLimits',
                                     TURBOSHAFT_SPEED_MODE_SPEED,
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
     VEHICLE_CLASS_NAME.SPG: ('avgDamage', 'stunMaxDuration', 'reloadTimeSecs', 'aimingTime', 'explosionRadius'),
     VEHICLE_CLASS_NAME.AT_SPG: ('avgPiercingPower', 'shotDispersionAngle', 'avgDamagePerMinute', 'speedLimits', 'chassisRotationSpeed', 'switchTime'),
     'roles': {constants.ROLE_TYPE.SPG_FLAME: ('avgDamage', 'flameMaxDistance', 'stunMaxDuration', 'enginePowerPerTon', 'speedLimits'),
               constants.ROLE_TYPE.SPG_ASSAULT: ('avgDamagePerMinute', 'avgPiercingPower', 'aimingTime', 'speedLimits', 'hullArmor')},
     'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}
    __CONDITIONAL_PARAMS = ((ROCKET_ACCELERATION_SPEED_LIMITS, ('speedLimits', ROCKET_ACCELERATION_SPEED_LIMITS)),)

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        paramsDict = params_helper.getParameters(self.vehicle)
        block = []
        highlightedParams = self.__getHighlightedParams()
        comparator = params_helper.idealCrewComparator(self.vehicle)
        if self.configuration.params and not self.configuration.simplifiedOnly:
            for paramName in self.__getShownParameters(paramsDict):
                paramInfo = comparator.getExtendedData(paramName)
                fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.BASE_SCHEME)
                if fmtValue is not None:
                    block.append(formatters.packTextParameterBlockData(name=param_formatter.formatVehicleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-1), highlight=paramName in highlightedParams))

        if block:
            title = text_styles.middleTitle(backport.text(R.strings.tooltips.vehicleParams.common.title()))
            block.insert(0, formatters.packTextBlockData(title, padding=formatters.packPadding(bottom=8)))
        return block

    def __getHighlightedParams(self):
        serverSettings = dependency.instance(ISettingsCore).serverSettings
        descr = self.vehicle.descriptor
        params = []
        if descr.hasTurboshaftEngine and serverSettings.checkTurboshaftHighlights(increase=True):
            params.append(TURBOSHAFT_SPEED_MODE_SPEED)
        if descr.hasRocketAcceleration and serverSettings.checkRocketAccelerationHighlights(increase=True):
            params.append(ROCKET_ACCELERATION_SPEED_LIMITS)
        if descr.hasDualAccuracy and serverSettings.checkDualAccuracyHighlights(increase=True):
            params.append(DUAL_ACCURACY_COOLING_DELAY)
            params.append(SHOT_DISPERSION_ANGLE)
        return params

    def __getShownParameters(self, paramsDict):
        if self.vehicle.role in self.PARAMS['roles']:
            paramsToDisplay = self.PARAMS['roles'][self.vehicle.role]
        else:
            paramsToDisplay = self.PARAMS.get(self.vehicle.type, 'default')
        return chain([ p for p in paramsToDisplay if p in paramsDict ], [ p for group in self.__CONDITIONAL_PARAMS if group[0] in paramsDict for p in group[1] ])

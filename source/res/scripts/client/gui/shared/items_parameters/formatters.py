# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/formatters.py
import typing
from collections import namedtuple
from itertools import chain
from constants import BonusTypes, DAMAGE_INTERPOLATION_DIST_LAST
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items import KPI, kpiFormatValue, kpiFormatNoSignValue
from gui.shared.items_parameters import RELATIVE_PARAMS
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.params_helper import hasGroupPenalties, getCommonParam, isValidEmptyValue, PARAMS_GROUPS
from gui.shared.utils import AUTO_RELOAD_PROP_NAME, MAX_STEERING_LOCK_ANGLE, WHEELED_SWITCH_ON_TIME, WHEELED_SWITCH_OFF_TIME, WHEELED_SWITCH_TIME, WHEELED_SPEED_MODE_SPEED, DUAL_GUN_CHARGE_TIME, DUAL_GUN_RATE_TIME, TURBOSHAFT_SPEED_MODE_SPEED, TURBOSHAFT_ENGINE_POWER, TURBOSHAFT_INVISIBILITY_STILL_FACTOR, TURBOSHAFT_INVISIBILITY_MOVING_FACTOR, TURBOSHAFT_SWITCH_TIME, CHASSIS_REPAIR_TIME, CHASSIS_REPAIR_TIME_YOH, ROCKET_ACCELERATION_ENGINE_POWER, ROCKET_ACCELERATION_SPEED_LIMITS, ROCKET_ACCELERATION_REUSE_AND_DURATION, DUAL_ACCURACY_COOLING_DELAY, SHOT_DISPERSION_ANGLE, DISPERSION_RADIUS, BURST_FIRE_RATE, BURST_TIME_INTERVAL, BURST_SIZE, BURST_COUNT
from helpers.i18n import makeString
from items import vehicles, artefacts, getTypeOfCompactDescr, ITEM_TYPES
from web_stubs import i18n
ChangeCondition = namedtuple('ChangeCondition', ('predicate', 'alternativeParameter'))
MEASURE_UNITS = {'aimingTime': MENU.TANK_PARAMS_S,
 'areaRadius': MENU.TANK_PARAMS_M,
 'areaSquare': MENU.TANK_PARAMS_SQM,
 'armor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
 'artDelayRange': MENU.TANK_PARAMS_S,
 'avgDamageList': MENU.TANK_PARAMS_VAL,
 'maxAvgMutableDamageList': MENU.TANK_PARAMS_VAL,
 'minAvgMutableDamageList': MENU.TANK_PARAMS_VAL,
 'gunModuleAvgDamageList': MENU.TANK_PARAMS_VAL,
 'avgPiercingPower': MENU.TANK_PARAMS_MM,
 'bombDamage': MENU.TANK_PARAMS_VAL,
 'bombsNumberRange': MENU.TANK_PARAMS_CNT,
 'chassisRotationSpeed': MENU.TANK_PARAMS_GPS,
 'circularVisionRadius': MENU.TANK_PARAMS_M,
 'clipFireRate': MENU.TANK_PARAMS_CLIPSEC,
 BURST_FIRE_RATE: MENU.TANK_PARAMS_BURSTSEC,
 'turboshaftBurstFireRate': MENU.TANK_PARAMS_BURSTSEC,
 BURST_TIME_INTERVAL: MENU.TANK_PARAMS_S,
 BURST_COUNT: MENU.TANK_PARAMS_CNT,
 BURST_SIZE: MENU.TANK_PARAMS_CNT,
 'avgDamage': MENU.TANK_PARAMS_VAL,
 'avgMutableDamage': MENU.TANK_PARAMS_VAL,
 'avgDamagePerMinute': MENU.TANK_PARAMS_VPM,
 'fireStartingChance': MENU.TANK_PARAMS_PERCENT,
 'maxHealth': MENU.TANK_PARAMS_VAL,
 'flyDelayRange': MENU.TANK_PARAMS_S,
 'enginePower': MENU.TANK_PARAMS_P,
 TURBOSHAFT_ENGINE_POWER: MENU.TANK_PARAMS_P,
 ROCKET_ACCELERATION_ENGINE_POWER: MENU.TANK_PARAMS_P,
 ROCKET_ACCELERATION_REUSE_AND_DURATION: MENU.TANK_PARAMS_QPT,
 ROCKET_ACCELERATION_SPEED_LIMITS: MENU.TANK_PARAMS_MPH,
 'enginePowerPerTon': MENU.TANK_PARAMS_PT,
 'explosionRadius': MENU.TANK_PARAMS_M,
 'gunYawLimits': MENU.TANK_PARAMS_GRADS,
 'hullArmor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
 'maxLoad': MENU.TANK_PARAMS_T,
 'piercingPower': MENU.TANK_PARAMS_MM,
 'maxPiercingPower': MENU.TANK_PARAMS_MM,
 'minPiercingPower': MENU.TANK_PARAMS_MM,
 'pitchLimits': MENU.TANK_PARAMS_GRADS,
 'radioDistance': MENU.TANK_PARAMS_M,
 'radarRadius': MENU.TANK_PARAMS_M,
 'radarCooldown': MENU.TANK_PARAMS_S,
 'maxHullHealth': MENU.TANK_PARAMS_VAL,
 'forwardMaxSpeed': MENU.TANK_PARAMS_MPH,
 'reloadMagazineTime': MENU.TANK_PARAMS_S,
 'reloadTime': MENU.TANK_PARAMS_SPM,
 'reloadTimeSecs': MENU.TANK_PARAMS_S,
 'rotationSpeed': MENU.TANK_PARAMS_GPS,
 'chassisModuleRotationSpeed': MENU.TANK_PARAMS_GPS,
 'turretModuleRotationSpeed': MENU.TANK_PARAMS_GPS,
 'shellReloadingTime': MENU.TANK_PARAMS_S,
 SHOT_DISPERSION_ANGLE: MENU.TANK_PARAMS_M,
 'shotsNumberRange': MENU.TANK_PARAMS_CNT,
 'shellsCount': MENU.TANK_PARAMS_CNT,
 'speedLimits': MENU.TANK_PARAMS_MPH,
 'turretArmor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
 'turretYawLimits': MENU.TANK_PARAMS_GRADS,
 'vehicleWeight': MENU.TANK_PARAMS_T,
 'weight': MENU.TANK_PARAMS_KG,
 'hullWeight': MENU.TANK_PARAMS_KG,
 'hullAndChassisWeight': MENU.TANK_PARAMS_KG,
 'caliber': MENU.TANK_PARAMS_MM,
 'damage': MENU.TANK_PARAMS_VAL,
 'maxMutableDamage': MENU.TANK_PARAMS_VAL,
 'minMutableDamage': MENU.TANK_PARAMS_VAL,
 'turretRotationSpeed': MENU.TANK_PARAMS_GPS,
 'invisibilityStillFactor': MENU.TANK_PARAMS_PERCENT,
 'invisibilityMovingFactor': MENU.TANK_PARAMS_PERCENT,
 TURBOSHAFT_INVISIBILITY_STILL_FACTOR: MENU.TANK_PARAMS_PERCENT,
 TURBOSHAFT_INVISIBILITY_MOVING_FACTOR: MENU.TANK_PARAMS_PERCENT,
 'maxShotDistance': MENU.TANK_PARAMS_M,
 'switchOnTime': MENU.TANK_PARAMS_S,
 'switchOffTime': MENU.TANK_PARAMS_S,
 'switchTime': MENU.TANK_PARAMS_S,
 TURBOSHAFT_SWITCH_TIME: MENU.TANK_PARAMS_S,
 'stunMaxDuration': MENU.TANK_PARAMS_S,
 'stunMinDuration': MENU.TANK_PARAMS_S,
 'stunDurationList': MENU.TANK_PARAMS_S,
 'stunMaxDurationList': MENU.TANK_PARAMS_S,
 'stunMinDurationList': MENU.TANK_PARAMS_S,
 'cooldownSeconds': MENU.TANK_PARAMS_S,
 AUTO_RELOAD_PROP_NAME: MENU.TANK_PARAMS_S,
 MAX_STEERING_LOCK_ANGLE: MENU.TANK_PARAMS_GRADS,
 WHEELED_SWITCH_ON_TIME: MENU.TANK_PARAMS_S,
 WHEELED_SWITCH_OFF_TIME: MENU.TANK_PARAMS_S,
 WHEELED_SWITCH_TIME: MENU.TANK_PARAMS_S,
 WHEELED_SPEED_MODE_SPEED: MENU.TANK_PARAMS_MPH,
 TURBOSHAFT_SPEED_MODE_SPEED: MENU.TANK_PARAMS_MPH,
 DUAL_GUN_CHARGE_TIME: MENU.TANK_PARAMS_S,
 DUAL_GUN_RATE_TIME: MENU.TANK_PARAMS_S,
 DUAL_ACCURACY_COOLING_DELAY: MENU.TANK_PARAMS_S,
 'shotSpeed': MENU.TANK_PARAMS_MPS,
 CHASSIS_REPAIR_TIME: MENU.TANK_PARAMS_S,
 CHASSIS_REPAIR_TIME_YOH: MENU.TANK_PARAMS_YOH_S_S,
 'commonDelay': MENU.TANK_PARAMS_S,
 'duration': MENU.TANK_PARAMS_S,
 'inactivationDelay': MENU.TANK_PARAMS_S,
 'commonAreaRadius': MENU.TANK_PARAMS_M,
 'crewRolesFactor': MENU.TANK_PARAMS_PERCENT,
 'maxDamage': MENU.TANK_PARAMS_VAL,
 'increaseHealth': MENU.TANK_PARAMS_VAL,
 'artNotificationDelayFactor': MENU.TANK_PARAMS_S,
 'vehicleOwnSpottingTime': MENU.TANK_PARAMS_S,
 'damagedModulesDetectionTime': MENU.TANK_PARAMS_S}
MEASURE_UNITS_NO_BRACKETS = {'weight': MENU.TANK_PARAMS_NO_BRACKETS_KG,
 'cooldownSeconds': MENU.TANK_PARAMS_NO_BRACKETS_S,
 'reloadCooldownSeconds': MENU.TANK_PARAMS_NO_BRACKETS_S,
 'caliber': MENU.TANK_PARAMS_NO_BRACKETS_MM}
KPI_FORMATTERS = {KPI.Name.DAMAGED_MODULES_DETECTION_TIME: kpiFormatNoSignValue,
 KPI.Name.ART_NOTIFICATION_DELAY_FACTOR: kpiFormatNoSignValue}
COLORLESS_SCHEME = (text_styles.stats, text_styles.stats, text_styles.stats)
NO_BONUS_SIMPLIFIED_SCHEME = (text_styles.warning, text_styles.warning, text_styles.warning)
NO_BONUS_BASE_SCHEME = (text_styles.error, text_styles.stats, text_styles.stats)
SIMPLIFIED_SCHEME = (text_styles.critical, text_styles.warning, text_styles.statInfo)
BASE_SCHEME = (text_styles.error, text_styles.stats, text_styles.bonusAppliedText)
EXTRACTED_BONUS_SCHEME = (text_styles.error, text_styles.bonusAppliedText, text_styles.bonusAppliedText)
SITUATIONAL_SCHEME = (text_styles.critical, text_styles.warning, text_styles.bonusPreviewText)
VEHICLE_PARAMS = tuple(chain(*[ PARAMS_GROUPS[param] for param in RELATIVE_PARAMS ]))
ITEMS_PARAMS_LIST = {ITEM_TYPES.vehicleRadio: ('radioDistance', 'weight'),
 ITEM_TYPES.vehicleChassis: ('maxLoad',
                             'rotationSpeed',
                             'weight',
                             MAX_STEERING_LOCK_ANGLE,
                             CHASSIS_REPAIR_TIME),
 ITEM_TYPES.vehicleEngine: ('enginePower',
                            TURBOSHAFT_ENGINE_POWER,
                            ROCKET_ACCELERATION_ENGINE_POWER,
                            'fireStartingChance',
                            'weight'),
 ITEM_TYPES.vehicleTurret: ('armor', 'rotationSpeed', 'circularVisionRadius', 'weight'),
 ITEM_TYPES.vehicle: VEHICLE_PARAMS,
 ITEM_TYPES.equipment: {artefacts.RageArtillery: ('damage', 'piercingPower', 'caliber', 'shotsNumberRange', 'areaRadius', 'artDelayRange'),
                        artefacts.RageBomber: ('bombDamage', 'piercingPower', 'bombsNumberRange', 'areaSquare', 'flyDelayRange'),
                        artefacts.AttackArtilleryFortEquipment: ('maxDamage', 'areaRadius', 'duration', 'commonDelay'),
                        artefacts.FortConsumableInspire: ('crewRolesFactor', 'commonAreaRadius', 'inactivationDelay', 'duration'),
                        artefacts.ConsumableInspire: ('crewRolesFactor', 'commonAreaRadius', 'inactivationDelay', 'duration')},
 ITEM_TYPES.shell: ('caliber', 'avgDamage', 'avgMutableDamage', 'avgPiercingPower', 'shotSpeed', 'explosionRadius', 'stunDurationList'),
 ITEM_TYPES.optionalDevice: ('weight',),
 ITEM_TYPES.vehicleGun: ('caliber',
                         'shellsCount',
                         'reloadTimeSecs',
                         'shellReloadingTime',
                         'reloadMagazineTime',
                         AUTO_RELOAD_PROP_NAME,
                         'reloadTime',
                         'rateTime',
                         'chargeTime',
                         'avgPiercingPower',
                         'avgDamageList',
                         'maxAvgDamageList',
                         'minAvgDamageList',
                         'stunMinDurationList',
                         'stunMaxDurationList',
                         DISPERSION_RADIUS,
                         DUAL_ACCURACY_COOLING_DELAY,
                         'aimingTime',
                         'maxShotDistance',
                         'weight')}
FORMAT_NAME_C_S_VALUE_S_UNITS = '{paramName} {paramValue} {paramUnits}'
_COUNT_OF_AUTO_RELOAD_SLOTS_TIMES_TO_SHOW_IN_INFO = 5
_EQUAL_TO_ZERO_LITERAL = '~0'

def needUseYohChassisRepairTime(vehicleDescr):
    return vehicleDescr and vehicleDescr.isTrackWithinTrack


MULTIPLE_MEASURE_UNITS_PARAMS = {CHASSIS_REPAIR_TIME: ChangeCondition(needUseYohChassisRepairTime, CHASSIS_REPAIR_TIME_YOH)}

def getMeasureParamName(vehicleDescr, paramName):
    if paramName in MULTIPLE_MEASURE_UNITS_PARAMS:
        measureCondition = MULTIPLE_MEASURE_UNITS_PARAMS[paramName]
        if measureCondition.predicate(vehicleDescr):
            return measureCondition.alternativeParameter
    return paramName


MULTIPLE_TITLES_PARAMS = {CHASSIS_REPAIR_TIME: ChangeCondition(needUseYohChassisRepairTime, CHASSIS_REPAIR_TIME_YOH)}

def getTitleParamName(vehicleDescr, paramName):
    if paramName in MULTIPLE_TITLES_PARAMS:
        changeCondition = MULTIPLE_TITLES_PARAMS[paramName]
        if changeCondition.predicate(vehicleDescr):
            return changeCondition.alternativeParameter
    return paramName


def measureUnitsForParameter(paramName):
    return i18n.makeString(MEASURE_UNITS[paramName])


def isRelativeParameter(paramName):
    return paramName in RELATIVE_PARAMS


def isRelativeParameterVisible(parameter):
    return isRelativeParameter(parameter.name) and isDiffEnoughToDisplay(parameter.state[1])


def isDiffEnoughToDisplay(value):
    return abs(int(value)) > 0


def getParameterSmallIconPath(parameter):
    return RES_ICONS.MAPS_ICONS_VEHPARAMS_SMALL + '/%s.png' % parameter


def getParameterBigIconPath(parameter):
    return RES_ICONS.MAPS_ICONS_VEHPARAMS_BIG + '/%s.png' % parameter


def formatModuleParamName(paramName, vDescr=None):
    builder = text_styles.builder(delimiter=_NBSP)
    hasBoost = vDescr and vDescr.gun.autoreloadHasBoost
    titleName = getTitleParamName(vDescr, paramName)
    if paramName == 'minAvgMutableDamageList':
        dist = DAMAGE_INTERPOLATION_DIST_LAST
        if vDescr is not None:
            dist = int(min(vDescr.shot.maxDistance, DAMAGE_INTERPOLATION_DIST_LAST))
        textOrMsgId = backport.text(R.strings.menu.moduleInfo.params.dyn(titleName)(), dist=dist)
    else:
        resource = R.strings.menu.moduleInfo.params.dyn(titleName)
        textOrMsgId = backport.msgid(resource.dyn('boost')() if hasBoost and resource.dyn('boost') else resource())
    builder.addStyledText(text_styles.main, textOrMsgId)
    measureName = getMeasureParamName(vDescr, paramName)
    builder.addStyledText(text_styles.standard, MEASURE_UNITS.get(measureName, ''))
    return builder.render()


def formatNameColonValue(nameStr, valueStr):
    builder = text_styles.builder(delimiter=_NBSP)
    builder.addStyledText(text_styles.main, '{}{}'.format(makeString(nameStr), _COLON))
    builder.addStyledText(text_styles.expText, makeString(valueStr))
    return builder.render()


def formatParamNameColonValueUnits(paramName, paramValue):
    builder = text_styles.builder(delimiter=_NBSP)
    resource = R.strings.menu.moduleInfo.params
    paramMsgId = backport.msgid(resource.dyn(paramName)()) if resource.dyn(paramName) else None
    builder.addStyledText(text_styles.main, '{}{}'.format(makeString(paramMsgId), _COLON))
    builder.addStyledText(text_styles.expText, paramValue)
    builder.addStyledText(text_styles.standard, MEASURE_UNITS_NO_BRACKETS.get(paramName, ''))
    return builder.render()


def formatVehicleParamName(paramName, showMeasureUnit=True):
    if isRelativeParameter(paramName):
        return text_styles.middleTitle(MENU.tank_params(paramName))
    else:
        builder = text_styles.builder(delimiter=_NBSP)
        builder.addStyledText(text_styles.main, MENU.tank_params(paramName))
        if showMeasureUnit:
            builder.addStyledText(text_styles.standard, MEASURE_UNITS.get(paramName, ''))
        return builder.render()


def getRelativeDiffParams(comparator):
    relativeParams = [ p for p in comparator.getAllDifferentParams() if isRelativeParameterVisible(p) ]
    return sorted(relativeParams, cmp=lambda a, b: cmp(RELATIVE_PARAMS.index(a.name), RELATIVE_PARAMS.index(b.name)))


_NBSP = backport.text(R.strings.common.common.nbsp())
_DASH = '-'
_SLASH = '/'
_COLON = ':'
_niceFormat = {'rounder': backport.getNiceNumberFormat}
_niceRangeFormat = {'rounder': backport.getNiceNumberFormat,
 'separator': _DASH}
_listFormat = {'rounder': lambda v: backport.getIntegralFormat(int(v)),
 'separator': _SLASH}
_niceListFormat = {'rounder': backport.getNiceNumberFormat,
 'separator': _SLASH}
_niceListFormatWithoutNone = {'rounder': backport.getNiceNumberFormat,
 'separator': _SLASH,
 'skipNone': True}
_integralFormat = {'rounder': backport.getIntegralFormat}
_percentFormat = {'rounder': lambda v: '%d%%' % v}
_plusPercentFormat = {'rounder': lambda v: '+%d%%' % v}

def _autoReloadPreprocessor(reloadTimes, rowStates):
    times = []
    states = []
    if not hasattr(reloadTimes, '__iter__'):
        return (times, _SLASH, states if states else None)
    else:
        for idx, slotTime in enumerate(reloadTimes):
            if isinstance(slotTime, (float, int)) or slotTime is None:
                times.append(slotTime)
                if rowStates:
                    states.append(rowStates[idx])
                continue
            if isinstance(slotTime, tuple):
                minSlotTime, maxSlotTime = slotTime
                if minSlotTime == maxSlotTime:
                    times.append(minSlotTime)
                    if rowStates:
                        states.append(rowStates[idx][0])
                else:
                    LOG_ERROR('Different auto-reload times for same gun and slot')
                    return

        if len(times) > _COUNT_OF_AUTO_RELOAD_SLOTS_TIMES_TO_SHOW_IN_INFO:
            if states:
                minTime, maxTime = min(times), max(times)
                minState, maxState = (None, None)
                for idx, time in enumerate(times):
                    if time == minTime:
                        minState = states[idx]
                    if time == maxTime:
                        maxState = states[idx]

                return ((min(times), max(times)), _DASH, (minState, maxState))
            return ((min(times), max(times)), _DASH, None)
        return (times, _SLASH, states if states else None)


def shotDispersionAnglePreprocessor(values, states):
    _, dualAccuracyParamDiff = states[0]
    states = [(PARAM_STATE.WORSE, dualAccuracyParamDiff)] + [states[1]] if len(states) > 1 else states
    return (values, _SLASH, states)


def _getRoundReload(value):
    return backport.getNiceNumberFormat(round(value, 1))


FORMAT_SETTINGS = {'relativePower': _integralFormat,
 'damage': _niceRangeFormat,
 'maxMutableDamage': _niceRangeFormat,
 'minMutableDamage': _niceRangeFormat,
 'piercingPower': _niceRangeFormat,
 'maxPiercingPower': _niceRangeFormat,
 'minPiercingPower': _niceRangeFormat,
 'reloadTime': _niceRangeFormat,
 'reloadTimeSecs': _niceListFormat,
 'turretRotationSpeed': _niceListFormat,
 'turretYawLimits': _niceListFormat,
 'gunYawLimits': _niceListFormat,
 'pitchLimits': _niceListFormat,
 'clipFireRate': _niceListFormat,
 BURST_FIRE_RATE: _niceListFormat,
 BURST_TIME_INTERVAL: _niceFormat,
 BURST_COUNT: _integralFormat,
 BURST_SIZE: _integralFormat,
 'turboshaftBurstFireRate': _niceListFormat,
 'aimingTime': _niceListFormat,
 'avgDamagePerMinute': _niceFormat,
 'relativeArmor': _integralFormat,
 'avgDamage': _niceFormat,
 'avgMutableDamage': _niceRangeFormat,
 'maxHealth': _integralFormat,
 'hullArmor': _listFormat,
 'turretArmor': _listFormat,
 'relativeMobility': _integralFormat,
 'vehicleWeight': _niceListFormat,
 'weight': _niceRangeFormat,
 'enginePower': _integralFormat,
 TURBOSHAFT_ENGINE_POWER: _integralFormat,
 ROCKET_ACCELERATION_ENGINE_POWER: _integralFormat,
 'enginePowerPerTon': _niceListFormat,
 'speedLimits': _niceListFormat,
 'chassisRotationSpeed': _niceFormat,
 'relativeVisibility': _integralFormat,
 'relativeCamouflage': _integralFormat,
 'circularVisionRadius': _niceListFormat,
 'radioDistance': _niceFormat,
 'maxLoad': _niceFormat,
 'rotationSpeed': _niceFormat,
 'fireStartingChance': _percentFormat,
 'armor': _listFormat,
 'caliber': _niceFormat,
 'shotsNumberRange': _niceFormat,
 'areaRadius': _niceFormat,
 'artDelayRange': _niceFormat,
 'bombDamage': _niceRangeFormat,
 'bombsNumberRange': _niceFormat,
 'areaSquare': _niceFormat,
 'flyDelayRange': _niceFormat,
 'explosionRadius': _niceFormat,
 'shellsCount': _niceRangeFormat,
 'shellReloadingTime': _niceRangeFormat,
 'reloadMagazineTime': _niceRangeFormat,
 'avgPiercingPower': _listFormat,
 'avgDamageList': _listFormat,
 'maxAvgMutableDamageList': _listFormat,
 'minAvgMutableDamageList': _listFormat,
 SHOT_DISPERSION_ANGLE: _niceListFormatWithoutNone,
 DISPERSION_RADIUS: _niceListFormatWithoutNone,
 'invisibilityStillFactor': _niceListFormat,
 'invisibilityMovingFactor': _niceListFormat,
 TURBOSHAFT_INVISIBILITY_STILL_FACTOR: _niceListFormat,
 TURBOSHAFT_INVISIBILITY_MOVING_FACTOR: _niceListFormat,
 'switchOnTime': _niceFormat,
 'switchOffTime': _niceFormat,
 'switchTime': _niceListFormat,
 TURBOSHAFT_SWITCH_TIME: _niceListFormat,
 'stunMaxDuration': _niceFormat,
 'stunMinDuration': _niceFormat,
 'stunMaxDurationList': _niceListFormat,
 'stunMinDurationList': _niceListFormat,
 'stunDurationList': _niceRangeFormat,
 'cooldownSeconds': _niceFormat,
 AUTO_RELOAD_PROP_NAME: {'preprocessor': _autoReloadPreprocessor,
                         'rounder': _getRoundReload},
 MAX_STEERING_LOCK_ANGLE: _niceFormat,
 WHEELED_SWITCH_ON_TIME: _niceFormat,
 WHEELED_SWITCH_OFF_TIME: _niceFormat,
 WHEELED_SWITCH_TIME: _niceListFormat,
 WHEELED_SPEED_MODE_SPEED: _niceListFormat,
 DUAL_GUN_CHARGE_TIME: _niceListFormat,
 DUAL_GUN_RATE_TIME: _niceListFormat,
 DUAL_ACCURACY_COOLING_DELAY: _niceFormat,
 'shotSpeed': _integralFormat,
 'extraRepairSpeed': _percentFormat,
 TURBOSHAFT_SPEED_MODE_SPEED: _niceListFormat,
 ROCKET_ACCELERATION_SPEED_LIMITS: _niceListFormat,
 ROCKET_ACCELERATION_REUSE_AND_DURATION: _niceListFormat,
 CHASSIS_REPAIR_TIME: _niceListFormat,
 'commonDelay': _niceFormat,
 'duration': _niceFormat,
 'inactivationDelay': _niceFormat,
 'commonAreaRadius': _niceFormat,
 'crewRolesFactor': _plusPercentFormat,
 'maxDamage': _niceFormat,
 'artNotificationDelayFactor': _niceFormat,
 'vehicleOwnSpottingTime': _niceFormat,
 'damagedModulesDetectionTime': _niceFormat}

def _deltaWrapper(fn):

    def wrapped(paramValue):
        formattedValue = fn(paramValue)
        if formattedValue == '0':
            return _EQUAL_TO_ZERO_LITERAL
        return '+%s' % formattedValue if isinstance(paramValue, (int, float)) and paramValue > 0 else formattedValue

    return wrapped


def _getDeltaSettings():
    detlaSettings = {}
    for paramName, setting in FORMAT_SETTINGS.iteritems():
        settingCopy = setting.copy()
        rounder = settingCopy['rounder']
        settingCopy['rounder'] = _deltaWrapper(rounder)
        detlaSettings[paramName] = settingCopy

    return detlaSettings


DELTA_PARAMS_SETTING = _getDeltaSettings()
_SMART_ROUND_PARAMS = ('damage',
 'piercingPower',
 'bombDamage',
 'shellsCount',
 'shellReloadingTime',
 'reloadMagazineTime',
 'reloadTime',
 DISPERSION_RADIUS,
 'aimingTime',
 'weight',
 DUAL_GUN_RATE_TIME,
 DUAL_GUN_CHARGE_TIME,
 'crewRolesFactor')
_STATES_INDEX_IN_COLOR_MAP = {PARAM_STATE.WORSE: 0,
 PARAM_STATE.NORMAL: 1,
 PARAM_STATE.BETTER: 2}

def colorize(paramStr, state, colorScheme):
    if isinstance(state, (tuple, list)):
        stateType, _ = state
    else:
        stateType = state
    return paramStr if stateType == PARAM_STATE.NOT_APPLICABLE else colorScheme[_STATES_INDEX_IN_COLOR_MAP[stateType]](paramStr)


def colorizedFormatParameter(parameter, colorScheme):
    return formatParameter(parameter.name, parameter.value, parameter.state, colorScheme)


def colorizedFullFormatParameter(parameter, colorScheme):
    return formatParameter(parameter.name, parameter.value, parameter.state, colorScheme, allowSmartRound=False)


def simplifiedDeltaParameter(parameter, isSituational=False, isApproximately=False):
    mainFormatter = SIMPLIFIED_SCHEME[1]
    delta = int(parameter.state[1])
    paramStr = formatParameter(parameter.name, parameter.value)
    if delta:
        sign = '-' if delta < 0 else '+'
        approximatelySymbol = '*' if isApproximately else ''
        scheme = SITUATIONAL_SCHEME if isSituational else SIMPLIFIED_SCHEME
        deltaStr = colorize('%s%s%s' % (sign, abs(delta), approximatelySymbol), parameter.state, scheme)
        return '(%s) %s' % (deltaStr, mainFormatter(paramStr))
    return mainFormatter(paramStr)


def _applyFormat(value, state, settings, doSmartRound, colorScheme):
    if doSmartRound:
        value = _cutDigits(value)
    if isinstance(value, (str, unicode)):
        paramStr = value
    elif value is None or value == 0 and state is not None and state[0] == PARAM_STATE.NOT_APPLICABLE:
        paramStr = '--'
    else:
        paramStr = settings['rounder'](value)
    if state is not None and colorScheme is not None:
        if paramStr == _EQUAL_TO_ZERO_LITERAL and isinstance(state, (tuple, list)):
            stateType, value = state
            if value > 0:
                paramStr = '+&lt;0.01'
            elif value < 0:
                paramStr = '-&lt;0.01'
            if stateType == PARAM_STATE.NORMAL:
                paramStr = '0'
        paramStr = colorize(paramStr, state, colorScheme)
    return paramStr


def formatParameter(parameterName, paramValue, parameterState=None, colorScheme=None, formatSettings=None, allowSmartRound=True, showZeroDiff=False):
    formatSettings = formatSettings or FORMAT_SETTINGS
    settings = formatSettings.get(parameterName, _listFormat)
    doSmartRound = allowSmartRound and parameterName in _SMART_ROUND_PARAMS
    preprocessor = settings.get('preprocessor')
    if KPI.Name.hasValue(parameterName):
        formatter = KPI_FORMATTERS.get(parameterName, kpiFormatValue)
        values, separator = formatter(parameterName, round(paramValue, 3)), None
    elif preprocessor:
        values, separator, parameterState = preprocessor(paramValue, parameterState)
    else:
        values = paramValue
        separator = None
    if values is None:
        return
    elif isinstance(values, (tuple, list)):
        if parameterState is None:
            parameterState = [None] * len(values)
        if doSmartRound and len(set(values)) == 1:
            if values[0] > 0:
                return _applyFormat(values[0], parameterState[0], settings, doSmartRound, colorScheme)
            return
        separator = separator or settings.get('separator', '')
        skipNone = settings.get('skipNone', False)
        if skipNone:
            params = [ (val, state) for val, state in zip(values, parameterState) if val is not None ]
        else:
            params = zip(values, parameterState)
        paramsList = [ _applyFormat(val, state, settings, doSmartRound, colorScheme) for val, state in params ]
        return separator.join(paramsList)
    else:
        return None if not showZeroDiff and values == 0 and not isValidEmptyValue(parameterName, paramValue) else _applyFormat(values, parameterState, settings, doSmartRound, colorScheme)


def formatParameterDelta(pInfo, deltaScheme=None, formatSettings=None):
    diff = pInfo.getParamDiff()
    return formatParameter(pInfo.name, diff, pInfo.state, deltaScheme or BASE_SCHEME, formatSettings or DELTA_PARAMS_SETTING, allowSmartRound=False, showZeroDiff=True) if diff is not None else None


def getFormattedParamsList(descriptor, parameters, excludeRelative=False):
    if vehicles.isVehicleDescr(descriptor):
        compactDescr = descriptor.type.compactDescr
    else:
        compactDescr = descriptor.compactDescr
    itemTypeIdx = getTypeOfCompactDescr(compactDescr)
    if itemTypeIdx == ITEM_TYPES.equipment:
        eqDescr = vehicles.getItemByCompactDescr(compactDescr)
        paramsList = ITEMS_PARAMS_LIST[itemTypeIdx].get(type(eqDescr), [])
    else:
        paramsList = ITEMS_PARAMS_LIST[itemTypeIdx]
    params = []
    for paramName in paramsList:
        if excludeRelative and isRelativeParameter(paramName):
            continue
        paramValue = parameters.get(paramName)
        if paramValue or isValidEmptyValue(paramName, paramValue):
            fmtValue = formatParameter(paramName, paramValue)
            if fmtValue:
                if paramName == 'autoReloadTime' and descriptor.gun.autoreloadHasBoost:
                    paramName = 'autoReloadTimeBoost'
                elif paramName == CHASSIS_REPAIR_TIME and descriptor.isTrackWithinTrack:
                    paramName = CHASSIS_REPAIR_TIME_YOH
                params.append((paramName, fmtValue))

    return params


def getBonusIconRes(bonusId, bonusType, archetype=None):
    if bonusType == BonusTypes.PAIR_MODIFICATION:
        mod = vehicles.g_cache.postProgression().getModificationByName(bonusId)
        if mod is not None:
            iconR = R.images.gui.maps.icons.vehPostProgression.actionItems.pairModifications.c_24x24.dyn(mod.imgName, R.invalid)()
        else:
            iconR = R.invalid()
    elif bonusId.find('Rammer') >= 0 and bonusId != 'deluxRammer' and bonusId.find('trophy') == -1:
        iconR = R.images.gui.maps.icons.vehParams.tooltips.bonuses.rammer()
    elif archetype:
        iconR = R.images.gui.maps.icons.vehParams.tooltips.bonuses.archetypes.dyn(archetype, R.invalid)()
    else:
        iconR = R.images.gui.maps.icons.vehParams.tooltips.bonuses.dyn(bonusId.split('_class')[0], R.invalid)()
    return iconR


def getBonusIcon(bonusId, bonusType, archetype=None):
    return backport.image(getBonusIconRes(bonusId, bonusType, archetype))


def getPenaltyIconRes(penaltyId):
    return R.images.gui.maps.icons.vehParams.tooltips.penalties.dyn(penaltyId, R.invalid)()


def getPenaltyIcon(penaltyId):
    return backport.image(getPenaltyIconRes(penaltyId))


def packSituationalIcon(text, icon):
    return '<nobr>'.join((text, icon))


def getGroupPenaltyIcon(parameter, comparator):
    return RES_ICONS.MAPS_ICONS_VEHPARAMS_ICON_DECREASE if hasGroupPenalties(parameter.name, comparator) else ''


def getAllParametersTitles():
    result = []
    for _, groupName in enumerate(RELATIVE_PARAMS):
        data = getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_SIMPLE_TOP, groupName)
        data['titleText'] = formatVehicleParamName(groupName)
        data['isEnabled'] = True
        data['tooltip'] = TOOLTIPS_CONSTANTS.VEHICLE_ADVANCED_PARAMETERS
        result.append(data)
        for paramName in PARAMS_GROUPS[groupName]:
            data = getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_ADVANCED, paramName, groupName)
            data['iconSource'] = getParameterSmallIconPath(paramName)
            data['titleText'] = formatVehicleParamName(paramName)
            data['isEnabled'] = False
            data['tooltip'] = TOOLTIPS_CONSTANTS.BASE_VEHICLE_PARAMETERS
            result.append(data)

    return result


def _cutDigits(value):
    if abs(value) > 99:
        return round(value)
    return round(value, 1) if abs(value) > 9 else round(value, 2)

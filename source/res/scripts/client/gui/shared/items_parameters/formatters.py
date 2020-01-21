# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/formatters.py
from itertools import chain
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import RELATIVE_PARAMS
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.params_helper import hasGroupPenalties, getCommonParam, PARAMS_GROUPS
from gui.shared.utils import AUTO_RELOAD_PROP_NAME, MAX_STEERING_LOCK_ANGLE, WHEELED_SWITCH_ON_TIME, WHEELED_SWITCH_OFF_TIME, WHEELED_SWITCH_TIME, WHEELED_SPEED_MODE_SPEED, DUAL_GUN_CHARGE_TIME, DUAL_GUN_RATE_TIME
from items import vehicles, artefacts, getTypeOfCompactDescr, ITEM_TYPES
from web_stubs import i18n
MEASURE_UNITS = {'aimingTime': MENU.TANK_PARAMS_S,
 'areaRadius': MENU.TANK_PARAMS_M,
 'areaSquare': MENU.TANK_PARAMS_SQM,
 'armor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
 'artDelayRange': MENU.TANK_PARAMS_S,
 'avgDamageList': MENU.TANK_PARAMS_VAL,
 'avgPiercingPower': MENU.TANK_PARAMS_MM,
 'bombDamage': MENU.TANK_PARAMS_VAL,
 'bombsNumberRange': MENU.TANK_PARAMS_CNT,
 'chassisRotationSpeed': MENU.TANK_PARAMS_GPS,
 'circularVisionRadius': MENU.TANK_PARAMS_M,
 'clipFireRate': MENU.TANK_PARAMS_CLIPSEC,
 'avgDamage': MENU.TANK_PARAMS_VAL,
 'avgDamagePerMinute': MENU.TANK_PARAMS_VPM,
 'fireStartingChance': MENU.TANK_PARAMS_PERCENT,
 'maxHealth': MENU.TANK_PARAMS_VAL,
 'flyDelayRange': MENU.TANK_PARAMS_S,
 'enginePower': MENU.TANK_PARAMS_P,
 'enginePowerPerTon': MENU.TANK_PARAMS_PT,
 'explosionRadius': MENU.TANK_PARAMS_M,
 'gunYawLimits': MENU.TANK_PARAMS_GRADS,
 'hullArmor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
 'maxLoad': MENU.TANK_PARAMS_T,
 'piercingPower': MENU.TANK_PARAMS_MM,
 'pitchLimits': MENU.TANK_PARAMS_GRADS,
 'radioDistance': MENU.TANK_PARAMS_M,
 'reloadMagazineTime': MENU.TANK_PARAMS_S,
 'reloadTime': MENU.TANK_PARAMS_SPM,
 'reloadTimeSecs': MENU.TANK_PARAMS_S,
 'rotationSpeed': MENU.TANK_PARAMS_GPS,
 'shellReloadingTime': MENU.TANK_PARAMS_S,
 'shotDispersionAngle': MENU.TANK_PARAMS_M,
 'shotsNumberRange': MENU.TANK_PARAMS_CNT,
 'shellsCount': MENU.TANK_PARAMS_CNT,
 'speedLimits': MENU.TANK_PARAMS_MPH,
 'turretArmor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
 'turretYawLimits': MENU.TANK_PARAMS_GRADS,
 'vehicleWeight': MENU.TANK_PARAMS_T,
 'weight': MENU.TANK_PARAMS_KG,
 'caliber': MENU.TANK_PARAMS_MM,
 'damage': MENU.TANK_PARAMS_VAL,
 'turretRotationSpeed': MENU.TANK_PARAMS_GPS,
 'invisibilityStillFactor': MENU.TANK_PARAMS_PERCENT,
 'invisibilityMovingFactor': MENU.TANK_PARAMS_PERCENT,
 'maxShotDistance': MENU.TANK_PARAMS_M,
 'switchOnTime': MENU.TANK_PARAMS_S,
 'switchOffTime': MENU.TANK_PARAMS_S,
 'switchTime': MENU.TANK_PARAMS_S,
 'stunMaxDuration': MENU.TANK_PARAMS_S,
 'stunMinDuration': MENU.TANK_PARAMS_S,
 'stunMaxDurationList': MENU.TANK_PARAMS_S,
 'stunMinDurationList': MENU.TANK_PARAMS_S,
 'cooldownSeconds': MENU.TANK_PARAMS_S,
 AUTO_RELOAD_PROP_NAME: MENU.TANK_PARAMS_S,
 MAX_STEERING_LOCK_ANGLE: MENU.TANK_PARAMS_GRADS,
 WHEELED_SWITCH_ON_TIME: MENU.TANK_PARAMS_S,
 WHEELED_SWITCH_OFF_TIME: MENU.TANK_PARAMS_S,
 WHEELED_SWITCH_TIME: MENU.TANK_PARAMS_S,
 WHEELED_SPEED_MODE_SPEED: MENU.TANK_PARAMS_MPH,
 DUAL_GUN_CHARGE_TIME: MENU.TANK_PARAMS_S,
 DUAL_GUN_RATE_TIME: MENU.TANK_PARAMS_S}
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
                             MAX_STEERING_LOCK_ANGLE),
 ITEM_TYPES.vehicleEngine: ('enginePower', 'fireStartingChance', 'weight'),
 ITEM_TYPES.vehicleTurret: ('armor', 'rotationSpeed', 'circularVisionRadius', 'weight'),
 ITEM_TYPES.vehicle: VEHICLE_PARAMS,
 ITEM_TYPES.equipment: {artefacts.RageArtillery: ('damage', 'piercingPower', 'caliber', 'shotsNumberRange', 'areaRadius', 'artDelayRange'),
                        artefacts.RageBomber: ('bombDamage', 'piercingPower', 'bombsNumberRange', 'areaSquare', 'flyDelayRange')},
 ITEM_TYPES.shell: ('caliber', 'avgPiercingPower', 'damage', 'stunMinDuration', 'stunMaxDuration', 'explosionRadius'),
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
                         'stunMinDurationList',
                         'stunMaxDurationList',
                         'dispertionRadius',
                         'aimingTime',
                         'maxShotDistance',
                         'weight')}
_COUNT_OF_AUTO_RELOAD_SLOTS_TIMES_TO_SHOW_IN_INFO = 5

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


def formatModuleParamName(paramName):
    builder = text_styles.builder()
    builder.addStyledText(text_styles.main, MENU.moduleinfo_params(paramName))
    builder.addStyledText(text_styles.standard, MEASURE_UNITS.get(paramName, ''))
    return builder.render()


def formatVehicleParamName(paramName, showMeasureUnit=True):
    if isRelativeParameter(paramName):
        return text_styles.middleTitle(MENU.tank_params(paramName))
    else:
        builder = text_styles.builder(delimiter='&nbsp;')
        builder.addStyledText(text_styles.main, MENU.tank_params(paramName))
        if showMeasureUnit:
            builder.addStyledText(text_styles.standard, MEASURE_UNITS.get(paramName, ''))
        return builder.render()


def getRelativeDiffParams(comparator):
    relativeParams = [ p for p in comparator.getAllDifferentParams() if isRelativeParameterVisible(p) ]
    return sorted(relativeParams, cmp=lambda a, b: cmp(RELATIVE_PARAMS.index(a.name), RELATIVE_PARAMS.index(b.name)))


_niceFormat = {'rounder': backport.getNiceNumberFormat}
_niceRangeFormat = {'rounder': backport.getNiceNumberFormat,
 'separator': '-'}
_listFormat = {'rounder': lambda v: backport.getIntegralFormat(int(v)),
 'separator': '/'}
_niceListFormat = {'rounder': backport.getNiceNumberFormat,
 'separator': '/'}
_integralFormat = {'rounder': backport.getIntegralFormat}
_percentFormat = {'rounder': lambda v: '%d%%' % v}

def _autoReloadPreprocessor(reloadTimes, rowStates):
    times = []
    states = []
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

            return ((min(times), max(times)), '-', (minState, maxState))
        return ((min(times), max(times)), '-', None)
    else:
        return (times, '/', states if states else None)


def _getRoundReload(value):
    return backport.getNiceNumberFormat(round(value, 1))


FORMAT_SETTINGS = {'relativePower': _integralFormat,
 'damage': _niceRangeFormat,
 'piercingPower': _niceRangeFormat,
 'reloadTime': _niceRangeFormat,
 'reloadTimeSecs': _niceListFormat,
 'turretRotationSpeed': _niceFormat,
 'turretYawLimits': _niceListFormat,
 'gunYawLimits': _niceListFormat,
 'pitchLimits': _niceListFormat,
 'clipFireRate': _niceListFormat,
 'aimingTime': _niceRangeFormat,
 'shotDispersionAngle': _niceFormat,
 'avgDamagePerMinute': _niceFormat,
 'relativeArmor': _integralFormat,
 'avgDamage': _niceFormat,
 'maxHealth': _integralFormat,
 'hullArmor': _listFormat,
 'turretArmor': _listFormat,
 'relativeMobility': _integralFormat,
 'vehicleWeight': _niceListFormat,
 'weight': _niceRangeFormat,
 'enginePower': _integralFormat,
 'enginePowerPerTon': _niceFormat,
 'speedLimits': _niceListFormat,
 'chassisRotationSpeed': _niceFormat,
 'relativeVisibility': _integralFormat,
 'relativeCamouflage': _integralFormat,
 'circularVisionRadius': _niceFormat,
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
 'dispertionRadius': _niceRangeFormat,
 'invisibilityStillFactor': _niceListFormat,
 'invisibilityMovingFactor': _niceListFormat,
 'switchOnTime': _niceFormat,
 'switchOffTime': _niceFormat,
 'switchTime': _niceListFormat,
 'stunMaxDuration': _niceFormat,
 'stunMinDuration': _niceFormat,
 'stunMaxDurationList': _niceListFormat,
 'stunMinDurationList': _niceListFormat,
 'cooldownSeconds': _niceFormat,
 AUTO_RELOAD_PROP_NAME: {'preprocessor': _autoReloadPreprocessor,
                         'rounder': _getRoundReload},
 MAX_STEERING_LOCK_ANGLE: _niceFormat,
 WHEELED_SWITCH_ON_TIME: _niceFormat,
 WHEELED_SWITCH_OFF_TIME: _niceFormat,
 WHEELED_SWITCH_TIME: _niceListFormat,
 WHEELED_SPEED_MODE_SPEED: _niceListFormat,
 DUAL_GUN_CHARGE_TIME: _niceListFormat,
 DUAL_GUN_RATE_TIME: _niceListFormat}

def _deltaWrapper(fn):

    def wrapped(paramValue):
        formattedValue = fn(paramValue)
        if formattedValue == '0':
            return '~0'
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
 'dispertionRadius',
 'aimingTime',
 'weight',
 DUAL_GUN_RATE_TIME,
 DUAL_GUN_CHARGE_TIME)
_STATES_INDEX_IN_COLOR_MAP = {PARAM_STATE.WORSE: 0,
 PARAM_STATE.NORMAL: 1,
 PARAM_STATE.BETTER: 2}

def _colorize(paramStr, state, colorScheme):
    stateType, _ = state
    return paramStr if stateType == PARAM_STATE.NOT_APPLICABLE else colorScheme[_STATES_INDEX_IN_COLOR_MAP[stateType]](paramStr)


def colorizedFormatParameter(parameter, colorScheme):
    return formatParameter(parameter.name, parameter.value, parameter.state, colorScheme)


def colorizedFullFormatParameter(parameter, colorScheme):
    return formatParameter(parameter.name, parameter.value, parameter.state, colorScheme, allowSmartRound=False)


def simplifiedDeltaParameter(parameter, isSituational=False):
    mainFormatter = SIMPLIFIED_SCHEME[1]
    delta = int(parameter.state[1])
    paramStr = formatParameter(parameter.name, parameter.value)
    if delta:
        sign = '-' if delta < 0 else '+'
        scheme = SITUATIONAL_SCHEME if isSituational else SIMPLIFIED_SCHEME
        deltaStr = _colorize('%s%s' % (sign, abs(delta)), parameter.state, scheme)
        return '(%s) %s' % (deltaStr, mainFormatter(paramStr))
    return mainFormatter(paramStr)


def _applyFormat(value, state, settings, doSmartRound, colorScheme):
    if doSmartRound:
        value = _cutDigits(value)
    if isinstance(value, str):
        paramStr = value
    elif value is None:
        paramStr = '--'
    else:
        paramStr = settings['rounder'](value)
    if state is not None and colorScheme is not None:
        paramStr = _colorize(paramStr, state, colorScheme)
    return paramStr


def formatParameter(parameterName, paramValue, parameterState=None, colorScheme=None, formatSettings=None, allowSmartRound=True, showZeroDiff=False):
    formatSettings = formatSettings or FORMAT_SETTINGS
    settings = formatSettings.get(parameterName, _listFormat)
    doSmartRound = allowSmartRound and parameterName in _SMART_ROUND_PARAMS
    preprocessor = settings.get('preprocessor')
    if preprocessor:
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
        paramsList = [ _applyFormat(val, state, settings, doSmartRound, colorScheme) for val, state in zip(values, parameterState) ]
        return separator.join(paramsList)
    else:
        return None if not showZeroDiff and values == 0 else _applyFormat(values, parameterState, settings, doSmartRound, colorScheme)


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
        if paramValue:
            fmtValue = formatParameter(paramName, paramValue)
            if fmtValue:
                params.append((paramName, fmtValue))

    return params


def getBonusIcon(bonusId):
    if bonusId.find('Rammer') >= 0 and bonusId != 'deluxRammer':
        iconName = 'rammer'
    elif bonusId.find('enhanced') >= 0 and bonusId not in ('enhancedAimDrives', 'enhancedAimDrivesBattleBooster'):
        iconName = 'enhancedSuspension'
    else:
        iconName = bonusId.split('_class')[0]
    return RES_ICONS.getParamsTooltipIcon('bonuses', iconName)


def getPenaltyIcon(penaltyId):
    return RES_ICONS.getParamsTooltipIcon('penalties', penaltyId)


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
        data['tooltip'] = TOOLTIPS_CONSTANTS.BASE_VEHICLE_PARAMETERS
        result.append(data)
        for paramName in PARAMS_GROUPS[groupName]:
            data = getCommonParam(HANGAR_ALIASES.VEH_PARAM_RENDERER_STATE_ADVANCED, paramName)
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

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/formatters.py
import BigWorld
from itertools import chain
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.items_parameters import RELATIVE_PARAMS
from gui.shared.items_parameters.comparator import PARAM_STATE
from items import vehicles, artefacts, getTypeOfCompactDescr, ITEM_TYPES
from web_stubs import i18n
MEASURE_UNITS = {'aimingTime': MENU.TANK_PARAMS_S,
 'areaRadius': MENU.TANK_PARAMS_M,
 'areaSquare': MENU.TANK_PARAMS_SQM,
 'armor': MENU.TANK_PARAMS_FACEFRONTBOARDINMM,
 'artDelayRange': MENU.TANK_PARAMS_S,
 'avgDamage': MENU.TANK_PARAMS_VAL,
 'avgPiercingPower': MENU.TANK_PARAMS_MM,
 'bombDamage': MENU.TANK_PARAMS_VAL,
 'bombsNumberRange': MENU.TANK_PARAMS_CNT,
 'chassisRotationSpeed': MENU.TANK_PARAMS_GPS,
 'circularVisionRadius': MENU.TANK_PARAMS_M,
 'clipFireRate': MENU.TANK_PARAMS_CLIPSEC,
 'damageAvg': MENU.TANK_PARAMS_VAL,
 'damageAvgPerMinute': MENU.TANK_PARAMS_VPM,
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
 'gunRotationSpeed': MENU.TANK_PARAMS_GPS,
 'turretRotationSpeed': MENU.TANK_PARAMS_GPS,
 'invisibilityStillFactor': MENU.TANK_PARAMS_PERCENT,
 'invisibilityMovingFactor': MENU.TANK_PARAMS_PERCENT,
 'maxShotDistance': MENU.TANK_PARAMS_M,
 'switchOnTime': MENU.TANK_PARAMS_S,
 'switchOffTime': MENU.TANK_PARAMS_S}
NO_COLORIZE_FORMATTERS = (text_styles.stats, text_styles.stats, text_styles.stats)
NO_BONUS_SIMPLIFIED_FORMATTERS = (text_styles.warning, text_styles.warning, text_styles.warning)
NO_BONUS_BASE_FORMATTERS = (text_styles.error, text_styles.stats, text_styles.stats)
SIMPLIFIED_FORMATTERS = (text_styles.critical, text_styles.warning, text_styles.statInfo)
BASE_FORMATTERS = (text_styles.error, text_styles.stats, text_styles.bonusAppliedText)
RELATIVE_POWER_PARAMS = ('damage', 'piercingPower', 'reloadTime', 'reloadTimeSecs', 'gunRotationSpeed', 'turretRotationSpeed', 'turretYawLimits', 'pitchLimits', 'gunYawLimits', 'clipFireRate', 'aimingTime', 'shotDispersionAngle', 'damageAvgPerMinute')
RELATIVE_ARMOR_PARAMS = ('maxHealth', 'hullArmor', 'turretArmor')
RELATIVE_MOBILITY_PARAMS = ('vehicleWeight', 'enginePower', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'switchOnTime', 'switchOffTime')
RELATIVE_CAMOUFLAGE_PARAMS = ('invisibilityStillFactor', 'invisibilityMovingFactor')
RELATIVE_VISIBILITY_PARAMS = ('circularVisionRadius', 'radioDistance')
PARAMS_GROUPS = {'relativePower': RELATIVE_POWER_PARAMS,
 'relativeArmor': RELATIVE_ARMOR_PARAMS,
 'relativeMobility': RELATIVE_MOBILITY_PARAMS,
 'relativeCamouflage': RELATIVE_CAMOUFLAGE_PARAMS,
 'relativeVisibility': RELATIVE_VISIBILITY_PARAMS}
VEHICLE_PARAMS = tuple(chain(*[ PARAMS_GROUPS[param] for param in RELATIVE_PARAMS ]))
ITEMS_PARAMS_LIST = {ITEM_TYPES.vehicleRadio: ('radioDistance', 'weight'),
 ITEM_TYPES.vehicleChassis: ('maxLoad', 'rotationSpeed', 'weight'),
 ITEM_TYPES.vehicleEngine: ('enginePower', 'fireStartingChance', 'weight'),
 ITEM_TYPES.vehicleTurret: ('armor', 'rotationSpeed', 'circularVisionRadius', 'weight'),
 ITEM_TYPES.vehicle: VEHICLE_PARAMS,
 ITEM_TYPES.equipment: {artefacts.Artillery: ('damage', 'piercingPower', 'caliber', 'shotsNumberRange', 'areaRadius', 'artDelayRange'),
                        artefacts.Bomber: ('bombDamage', 'piercingPower', 'bombsNumberRange', 'areaSquare', 'flyDelayRange')},
 ITEM_TYPES.shell: ('caliber', 'piercingPower', 'damage', 'explosionRadius'),
 ITEM_TYPES.optionalDevice: ('weight',),
 ITEM_TYPES.vehicleGun: ('caliber', 'shellsCount', 'shellReloadingTime', 'reloadMagazineTime', 'reloadTime', 'avgPiercingPower', 'avgDamage', 'dispertionRadius', 'aimingTime', 'maxShotDistance', 'weight')}

def measureUnitsForParameter(paramName):
    return i18n.makeString(MEASURE_UNITS[paramName])


def isRelativeParameter(paramName):
    return paramName in RELATIVE_PARAMS


def isRelativeParameterVisible(param):
    return isRelativeParameter(param.name) and isDiffEnoughToDisplay(param.state[1])


def isDiffEnoughToDisplay(value):
    return abs(int(value)) > 0


def getParameterIconPath(parameter):
    return RES_ICONS.MAPS_ICONS_VEHPARAMS + '/%s.png' % parameter


def formatModuleParamName(paramName):
    builder = text_styles.builder()
    builder.addStyledText(text_styles.main, MENU.moduleinfo_params(paramName))
    builder.addStyledText(text_styles.standard, MEASURE_UNITS.get(paramName, ''))
    return builder.render()


def formatVehicleParamName(paramName, showMeasureUnit=True):
    if isRelativeParameter(paramName):
        return text_styles.middleTitle(MENU.tank_params(paramName))
    else:
        builder = text_styles.builder()
        builder.addStyledText(text_styles.main, MENU.tank_params(paramName))
        if showMeasureUnit:
            builder.addStyledText(text_styles.standard, MEASURE_UNITS.get(paramName, ''))
        return builder.render()


def formatCompatibles(name, collection):
    return ', '.join([ (text_styles.neutral(c) if c == name else text_styles.main(c)) for c in collection ])


def getRelativeDiffParams(comparator):
    relativeParams = filter(lambda param: isRelativeParameterVisible(param), comparator.getAllDifferentParams())
    return sorted(relativeParams, cmp=lambda a, b: cmp(RELATIVE_PARAMS.index(a.name), RELATIVE_PARAMS.index(b.name)))


_niceFormat = {'rounder': BigWorld.wg_getNiceNumberFormat}
_niceRangeFormat = {'rounder': BigWorld.wg_getNiceNumberFormat,
 'separator': '-'}
_listFormat = {'rounder': lambda v: BigWorld.wg_getIntegralFormat(int(v)),
 'separator': '/'}
_niceListFormat = {'rounder': BigWorld.wg_getNiceNumberFormat,
 'separator': '/'}
_integralFormat = {'rounder': BigWorld.wg_getIntegralFormat}
_percentFormat = {'rounder': lambda v: '%d%%' % v}
FORMAT_SETTINGS = {'relativePower': _integralFormat,
 'damage': _niceRangeFormat,
 'piercingPower': _niceRangeFormat,
 'reloadTime': _niceRangeFormat,
 'reloadTimeSecs': _niceFormat,
 'gunRotationSpeed': _niceFormat,
 'turretRotationSpeed': _niceFormat,
 'turretYawLimits': _niceListFormat,
 'gunYawLimits': _niceListFormat,
 'pitchLimits': _niceListFormat,
 'clipFireRate': _niceListFormat,
 'aimingTime': _niceRangeFormat,
 'shotDispersionAngle': _niceFormat,
 'damageAvgPerMinute': _niceFormat,
 'avgDamagePerMinute': _niceFormat,
 'relativeArmor': _integralFormat,
 'damageAvg': _niceFormat,
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
 'avgDamage': _listFormat,
 'dispertionRadius': _niceRangeFormat,
 'invisibilityStillFactor': _niceListFormat,
 'invisibilityMovingFactor': _niceListFormat,
 'switchOnTime': _niceFormat,
 'switchOffTime': _niceFormat}
_SMART_ROUND_PARAMS = ('damage', 'piercingPower', 'bombDamage', 'shellsCount', 'shellReloadingTime', 'reloadMagazineTime', 'reloadTime', 'dispertionRadius', 'aimingTime', 'weight', 'vehicleWeight', 'invisibilityStillFactor', 'invisibilityMovingFactor')
_STATES_INDEX_IN_COLOR_MAP = {PARAM_STATE.WORSE: 0,
 PARAM_STATE.NORMAL: 1,
 PARAM_STATE.BETTER: 2}

def _colorize(paramStr, state, colorScheme):
    return colorScheme[_STATES_INDEX_IN_COLOR_MAP[state[0]]](paramStr)


def baseFormatParameter(parameterName, parameterValue):
    return formatParameter(parameterName, parameterValue)


def colorizedFormatParameter(parameter, colorScheme):
    return formatParameter(parameter.name, parameter.value, parameter.state, colorScheme)


def simlifiedDeltaParameter(parameter):
    mainFormatter = SIMPLIFIED_FORMATTERS[1]
    delta = int(parameter.state[1])
    paramStr = formatParameter(parameter.name, parameter.value)
    if delta:
        sign = '-' if delta < 0 else '+'
        deltaStr = _colorize('%s%s' % (sign, abs(delta)), parameter.state, SIMPLIFIED_FORMATTERS)
        return '(%s) %s' % (deltaStr, mainFormatter(paramStr))
    else:
        return mainFormatter(paramStr)


def simplifiedVehicleParameter(parameter):
    paramStr = formatParameter(parameter.name, parameter.value)
    if parameter.state[0] == PARAM_STATE.WORSE:
        return _colorize(paramStr, parameter.state, NO_BONUS_SIMPLIFIED_FORMATTERS)
    else:
        mainFormatter = NO_BONUS_SIMPLIFIED_FORMATTERS[1]
        return mainFormatter(paramStr)


def formatParameter(parameterName, paramValue, parameterState=None, colorScheme=None, formatSettings=None, allowSmartRound=True):
    if parameterState is None and isinstance(paramValue, (tuple, list)):
        parameterState = [None] * len(paramValue)
    formatSettings = formatSettings or FORMAT_SETTINGS
    settings = formatSettings.get(parameterName, _listFormat)
    rounder = settings['rounder']
    doSmartRound = allowSmartRound and parameterName in _SMART_ROUND_PARAMS

    def applyFormat(value, state):
        if doSmartRound:
            value = _cutDigits(value)
        if isinstance(value, str):
            paramStr = value
        else:
            paramStr = rounder(value)
        if state is not None and colorScheme is not None:
            paramStr = _colorize(paramStr, state, colorScheme)
        return paramStr

    if paramValue is None:
        return
    else:
        if isinstance(paramValue, (tuple, list)):
            if doSmartRound and len(set(paramValue)) == 1:
                if paramValue[0] > 0:
                    return applyFormat(paramValue[0], parameterState[0])
                return
            else:
                separator = settings['separator']
                paramsList = [ applyFormat(val, parameterState[idx]) for idx, val in enumerate(paramValue) ]
                return separator.join(paramsList)
        else:
            if paramValue != 0:
                return applyFormat(paramValue, parameterState)
            return
        return


def getFormattedParamsList(descriptor, parameters, excludeRelative=False):
    if vehicles.isVehicleDescr(descriptor):
        compactDescr = descriptor.type.compactDescr
    else:
        compactDescr = descriptor['compactDescr']
    itemTypeIdx = getTypeOfCompactDescr(compactDescr)
    if itemTypeIdx == ITEM_TYPES.equipment:
        eqDescr = vehicles.getDictDescr(compactDescr)
        paramsList = ITEMS_PARAMS_LIST[itemTypeIdx].get(type(eqDescr), [])
    else:
        paramsList = ITEMS_PARAMS_LIST[itemTypeIdx]
    params = []
    for paramName in paramsList:
        if excludeRelative and isRelativeParameter(paramName):
            continue
        paramValue = parameters.get(paramName)
        if paramValue:
            fmtValue = baseFormatParameter(paramName, paramValue)
            if fmtValue:
                params.append((paramName, baseFormatParameter(paramName, paramValue)))

    return params


def _cutDigits(value):
    if value > 99:
        return round(value)
    elif value > 9:
        return round(value, 1)
    else:
        return round(value, 2)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/sub_views/veh_param_helpers.py
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_param_group_view_model import BuffIconType
from gui.shared.gui_items import KPI, kpiFormatValue
from gui.shared.items_parameters import MAX_RELATIVE_VALUE
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.formatters import FORMAT_SETTINGS, KPI_FORMATTERS, SMART_ROUND_PARAMS
from gui.shared.items_parameters.params_helper import hasPositiveEffect, hasNegativeEffect, hasGroupPenalties
_EQUAL_TO_ZERO_LITERAL = '~0'
_NUMBER_DIGITS = 2
_STATE_COLOR_MAP = {PARAM_STATE.BETTER: '%(green_open)s{}%(green_close)s',
 PARAM_STATE.WORSE: '%(red_open)s{}%(red_close)s',
 PARAM_STATE.SITUATIONAL: '%(yellow_open)s{}%(yellow_close)s'}

def getGroupIcon(parameter, comparator):
    states = {0: BuffIconType.NONE,
     1: BuffIconType.INCREASE,
     2: BuffIconType.DECREASE,
     3: BuffIconType.MIXED}
    state = 0
    if hasPositiveEffect(parameter.name, comparator):
        state |= 1
    if hasNegativeEffect(parameter.name, comparator):
        state |= 2
    if hasGroupPenalties(parameter.name, comparator):
        state |= 2
    return states[state]


def getMaxValue(value, delta):
    return max(MAX_RELATIVE_VALUE, value + delta)


def _applyFormat(value, state, settings, doSmartRound, isColorize, nDigits=_NUMBER_DIGITS):
    if doSmartRound:
        value = _cutDigits(value, nDigits)
    if isinstance(value, (str, unicode)):
        paramStr = value
    elif value is None:
        paramStr = '--'
    else:
        paramStr = settings['rounder'](value)
    if state is not None:
        if paramStr == _EQUAL_TO_ZERO_LITERAL and isinstance(state, (tuple, list)):
            stateType, value = state
            if value > 0:
                paramStr = '+&lt;0.01'
            elif value < 0:
                paramStr = '-&lt;0.01'
            if stateType == PARAM_STATE.NORMAL:
                paramStr = '0'
        if isColorize:
            paramStr = colorize(paramStr, state)
    return paramStr


def colorize(paramStr, state):
    if isinstance(state, (tuple, list)):
        stateType, _ = state
    else:
        stateType = state
    color = _STATE_COLOR_MAP.get(stateType, '')
    return color.format(paramStr) if color else paramStr


def _cutDigits(value, nDigits=_NUMBER_DIGITS):
    if abs(value) > 99:
        return round(value)
    return round(value, 1) if abs(value) > 9 else round(value, nDigits)


def formatParameterValue(parameterName, paramValue, parameterState=None, formatSettings=None, allowSmartRound=True, showZeroDiff=False, isColorize=True, nDigits=_NUMBER_DIGITS):
    _listFormat = {'rounder': lambda v: backport.getIntegralFormat(int(v)),
     'separator': '/'}
    formatSettings = formatSettings or FORMAT_SETTINGS
    settings = formatSettings.get(parameterName, _listFormat)
    doSmartRound = allowSmartRound and parameterName in SMART_ROUND_PARAMS
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
                return _applyFormat(values[0], parameterState[0], settings, doSmartRound, isColorize, nDigits)
            return
        separator = separator or settings.get('separator', '')
        paramsList = [ _applyFormat(val, state, settings, doSmartRound, isColorize, nDigits) for val, state in zip(values, parameterState) ]
        return separator.join(paramsList)
    else:
        return None if not showZeroDiff and values == 0 else _applyFormat(values, parameterState, settings, doSmartRound, isColorize, nDigits)


def formatAdditionalParameter(parameter, isApproximately=False):
    delta = int(parameter.state[1])
    if delta:
        sign = '-' if delta < 0 else '+'
        approximatelySymbol = '*' if isApproximately else ''
        deltaStr = colorize('%s%s%s' % (sign, abs(delta), approximatelySymbol), parameter.state)
        return '(%s)' % deltaStr

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_ability_tooltip_params.py
import logging
from functools import partial
from collections import namedtuple
import ResMgr
from gui.Scaleform.locale.COMMON import COMMON
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.items_parameters import formatters as params_formatters
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from helpers import i18n
from items import vehicles
from soft_exception import SoftException
from constants import IS_DEVELOPMENT
from items import _xml
COLOR_SCHEME = (text_styles.critical, text_styles.warning, text_styles.statInfo)
INVERSE_COLOR_SCHEME = COLOR_SCHEME[::-1]
NEUTRAL_STYLE = COLOR_SCHEME[1]
TOOLTIPS_PATH = 'gui/ability_tooltips.xml'

def _getColorScheme(higherIsBetter=True):
    return COLOR_SCHEME if higherIsBetter else INVERSE_COLOR_SCHEME


def _getTextStyleForDelta(delta, higherIsBetter=True):
    return _getColorScheme(higherIsBetter)[0 if delta < 0 else (1 if delta == 0 else 2)]


def _getSignForDelta(value):
    if value < 0:
        return '-'
    return '+' if value > 0 else ''


def _getSignForValue(value):
    return '-' if value < 0 else ''


def _getAttrName(param):
    return param.split('-')[0]


class DisplayValuesMixin(object):

    @classmethod
    def _getDisplayParams(cls, curEq, compareEq, eqsRange, param):
        raise NotImplementedError


class DirectValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, compareEq, eqsRange, param):
        param = _getAttrName(param)
        curValue = getattr(curEq, param)
        compValue = getattr(compareEq, param)
        return (curValue, compValue - curValue, max((getattr(eq, param) for eq in eqsRange)))


class MultipliedValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getMultiplier(cls):
        raise NotImplementedError

    @classmethod
    def _getDisplayParams(cls, curEq, compareEq, eqsRange, param):
        param = _getAttrName(param)
        curValue = getattr(curEq, param)
        compValue = getattr(compareEq, param)
        multiplier = cls._getMultiplier()
        return (curValue * multiplier, (compValue - curValue) * multiplier, max((getattr(eq, param) * multiplier for eq in eqsRange)))


class ReciprocalValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, compareEq, eqsRange, param):
        param = _getAttrName(param)
        curValue = getattr(curEq, param)
        compValue = getattr(compareEq, param)
        curValue = 1 / curValue if curValue != 0 else float('inf')
        compValue = 1 / compValue if compValue != 0 else float('inf')
        return (curValue, compValue - curValue, max(((1 / val if val != 0 else float('inf')) for val in (getattr(eq, param) for eq in eqsRange))))


class ShellStunValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, compareEq, eqsRange, param):
        param = _getAttrName(param)
        curShell = vehicles.getItemByCompactDescr(getattr(curEq, param))
        compShell = vehicles.getItemByCompactDescr(getattr(compareEq, param))
        shellsRange = (vehicles.getItemByCompactDescr(getattr(eq, param)) for eq in eqsRange)
        curValue = curShell.stun.stunDuration if curShell.hasStun else 0
        compValue = compShell.stun.stunDuration if compShell.hasStun else 0
        return (curValue, compValue - curValue, max(((shell.stun.stunDuration if shell.hasStun else 0) for shell in shellsRange)))


class MultiValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, compareEq, eqsRange, param):
        param = _getAttrName(param)
        eqsRange = list(eqsRange)
        params = param.split('_')
        length = len(params)
        curValues = [None] * length
        deltaValues = [None] * length
        maxValues = [None] * length
        for idx, singleParam in enumerate(params):
            curValues[idx] = curValue = getattr(curEq, singleParam)
            deltaValues[idx] = getattr(compareEq, singleParam) - curValue
            maxValues[idx] = max((getattr(eq, singleParam) for eq in eqsRange))

        return (curValues, deltaValues, maxValues)


class DisplayLabelMixin(object):

    @classmethod
    def _formatDeltaString(cls, delta, value, higherIsBetter=True):
        raise NotImplementedError


class NumericLabelMixin(DisplayLabelMixin):

    @classmethod
    def _formatDeltaStringInternal(cls, delta, value, higherIsBetter=True, unitLocalization=None, signForValue=_getSignForValue, signForDelta=_getSignForDelta):
        unitLocalization = None if not unitLocalization else i18n.makeString(unitLocalization)
        displayDelta = params_formatters._cutDigits(delta)
        displayValue = params_formatters._cutDigits(value)
        deltaStr = None
        if displayDelta != 0:
            deltaStr = '{}{}'.format(signForDelta(displayDelta), abs(int(displayDelta) if displayDelta.is_integer() else displayDelta))
            if unitLocalization:
                deltaStr = '{}{}'.format(deltaStr, unitLocalization)
            deltaStr = _getTextStyleForDelta(displayDelta, higherIsBetter)(deltaStr)
        valueStr = '{}{}'.format(signForValue(displayValue), abs(int(displayValue) if displayValue.is_integer() else displayValue))
        if unitLocalization:
            valueStr = '{}{}'.format(valueStr, unitLocalization)
        valueStr = NEUTRAL_STYLE(valueStr)
        return valueStr if deltaStr is None else '({}) {}'.format(deltaStr, valueStr)

    @classmethod
    def _formatDeltaString(cls, delta, value, higherIsBetter=True):
        return cls._formatDeltaStringInternal(delta, value, higherIsBetter)


class SecondsLabelMixin(NumericLabelMixin):

    @classmethod
    def _formatDeltaString(cls, delta, value, higherIsBetter=True):
        return cls._formatDeltaStringInternal(delta, value, higherIsBetter, EPIC_BATTLE.ABILITYINFO_UNITS_SECONDS)


class AdditionalSecondsLabelMixin(NumericLabelMixin):

    @classmethod
    def _formatDeltaString(cls, delta, value, higherIsBetter=True):
        return cls._formatDeltaStringInternal(delta, value, higherIsBetter, EPIC_BATTLE.ABILITYINFO_UNITS_SECONDS, signForValue=_getSignForDelta)


class MeterLabelMixin(NumericLabelMixin):

    @classmethod
    def _formatDeltaString(cls, delta, value, higherIsBetter=True):
        return cls._formatDeltaStringInternal(delta, value, higherIsBetter, EPIC_BATTLE.ABILITYINFO_UNITS_METER)


class PercentageLabelMixin(NumericLabelMixin):

    @classmethod
    def _formatDeltaString(cls, delta, value, higherIsBetter=True):
        return cls._formatDeltaStringInternal(delta * 100, value * 100 - 100, higherIsBetter, COMMON.COMMON_PERCENT, signForValue=_getSignForDelta)


class MultiMeterLabelMixin(NumericLabelMixin):

    @classmethod
    def _formatDeltaString(cls, deltas, values, higherIsBetter=True):
        labelParts = []
        for delta, value in zip(deltas, values):
            labelParts.append(cls._formatDeltaStringInternal(delta, value, higherIsBetter, EPIC_BATTLE.ABILITYINFO_UNITS_METER))

        return NEUTRAL_STYLE(' x ').join(labelParts)


class AbilityParam(object):

    @classmethod
    def extendBlocks(cls, blocks, curEq, compareEq, eqsRange, param, title, higherIsBetter=True):
        raise NotImplementedError


class FixedTextParam(AbilityParam):

    @classmethod
    def extendBlocks(cls, blocks, curEq, compareEq, eqsRange, param, title, higherIsBetter=True):
        blocks.append(formatters.packTextParameterBlockData(name=text_styles.middleTitle(title), value=NEUTRAL_STYLE(i18n.makeString(param)), padding=formatters.packPadding(left=0, top=0), valueWidth=85))


class DeltaBarParam(AbilityParam, DisplayValuesMixin, DisplayLabelMixin):

    @classmethod
    def extendBlocks(cls, blocks, curEq, compareEq, eqsRange, param, title, higherIsBetter=True):
        value, delta, maxValue = cls._getDisplayParams(curEq, compareEq, eqsRange, param)
        tmpVal = value + (delta if delta < 0 else 0)
        progressBar = SimplifiedBarVO(value=tmpVal, delta=delta, markerValue=value)
        progressBar['maxValue'] = maxValue
        blocks.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(title), valueStr=cls._formatDeltaString(delta, value + delta, higherIsBetter), statusBarData=progressBar, padding=formatters.packPadding(left=85, top=0)))


class TextParam(AbilityParam, DisplayValuesMixin, DisplayLabelMixin):

    @classmethod
    def extendBlocks(cls, blocks, curEq, compareEq, eqsRange, param, title, higherIsBetter=True):
        value, delta, _ = cls._getDisplayParams(curEq, compareEq, eqsRange, param)
        blocks.append(formatters.packTextParameterBlockData(name=text_styles.middleTitle(title), value=cls._formatDeltaString(delta, value + delta, higherIsBetter), padding=formatters.packPadding(left=0, top=0), valueWidth=85))


class MultiTextParam(AbilityParam, DisplayValuesMixin, DisplayLabelMixin):

    @classmethod
    def extendBlocks(cls, blocks, curEq, compareEq, eqsRange, param, title, higherIsBetter=True):
        values, deltas, _ = cls._getDisplayParams(curEq, compareEq, eqsRange, param)
        blocks.append(formatters.packTextParameterBlockData(name=text_styles.middleTitle(title), value=cls._formatDeltaString(deltas, [ value + delta for value, delta in zip(values, deltas) ], higherIsBetter), padding=formatters.packPadding(left=0, top=0), valueWidth=85))


class DirectNumericTextParam(TextParam, DirectValuesMixin, NumericLabelMixin):
    pass


class DirectSecondsTextParam(TextParam, DirectValuesMixin, SecondsLabelMixin):
    pass


class DirectMetersTextParam(TextParam, DirectValuesMixin, MeterLabelMixin):
    pass


class DirectNumericDeltaBarParam(DeltaBarParam, DirectValuesMixin, NumericLabelMixin):
    pass


class DirectSecondsDeltaBarParam(DeltaBarParam, DirectValuesMixin, SecondsLabelMixin):
    pass


class AdditionalSecondsDeltaBarParam(DeltaBarParam, DirectValuesMixin, AdditionalSecondsLabelMixin):
    pass


class DirectPercentageDeltaBarParam(DeltaBarParam, DirectValuesMixin, PercentageLabelMixin):
    pass


class ReciprocalPercentageDeltaBarParam(DeltaBarParam, ReciprocalValuesMixin, PercentageLabelMixin):
    pass


class ShellStunSecondsDeltaBarParam(DeltaBarParam, ShellStunValuesMixin, SecondsLabelMixin):
    pass


class MultipleMetersTextParam(MultiTextParam, MultiValuesMixin, MultiMeterLabelMixin):
    pass


def makeRenderer(func, higherIsBetter=True):
    return partial(func, higherIsBetter=higherIsBetter)


g_battleAbilityParamsRenderers = {'FixedTextParam': makeRenderer(FixedTextParam.extendBlocks),
 'AscDirectNumericTextParam': makeRenderer(DirectNumericTextParam.extendBlocks),
 'DescDirectNumericTextParam': makeRenderer(DirectNumericTextParam.extendBlocks, higherIsBetter=False),
 'AscDirectSecondsTextParam': makeRenderer(DirectSecondsTextParam.extendBlocks),
 'DescDirectSecondsTextParam': makeRenderer(DirectSecondsTextParam.extendBlocks, higherIsBetter=False),
 'AscDirectMetersTextParam': makeRenderer(DirectMetersTextParam.extendBlocks),
 'DescDirectMetersTextParam': makeRenderer(DirectMetersTextParam.extendBlocks, higherIsBetter=False),
 'AscDirectNumericDeltaBarParam': makeRenderer(DirectNumericDeltaBarParam.extendBlocks),
 'DescDirectNumericDeltaBarParam': makeRenderer(DirectNumericDeltaBarParam.extendBlocks, higherIsBetter=False),
 'AscDirectAdditionalSecondsDeltaBarParam': makeRenderer(AdditionalSecondsDeltaBarParam.extendBlocks),
 'AscDirectSecondsDeltaBarParam': makeRenderer(DirectSecondsDeltaBarParam.extendBlocks),
 'DescDirectSecondsDeltaBarParam': makeRenderer(DirectSecondsDeltaBarParam.extendBlocks, higherIsBetter=False),
 'AscDirectPercentageDeltaBarParam': makeRenderer(DirectPercentageDeltaBarParam.extendBlocks),
 'DescDirectPercentageDeltaBarParam': makeRenderer(DirectPercentageDeltaBarParam.extendBlocks, higherIsBetter=False),
 'AscReciprocalPercentageDeltaBarParam': makeRenderer(ReciprocalPercentageDeltaBarParam.extendBlocks),
 'DescReciprocalPercentageDeltaBarParam': makeRenderer(ReciprocalPercentageDeltaBarParam.extendBlocks, higherIsBetter=False),
 'AscShellStunSecondsDeltaBarParam': makeRenderer(ShellStunSecondsDeltaBarParam.extendBlocks),
 'DescShellStunSecondsDeltaBarParam': makeRenderer(ShellStunSecondsDeltaBarParam.extendBlocks, higherIsBetter=False),
 'AscMultiMetersTextParam': makeRenderer(MultipleMetersTextParam.extendBlocks),
 'DescMultiMetersTextParam': makeRenderer(MultipleMetersTextParam.extendBlocks, higherIsBetter=False)}
ConsumableTooltipEntry = namedtuple('ConsumableTooltipEntry', ('name', 'renderer'))

class BattleAbilityTooltipManager(object):

    def __init__(self):
        self.__tooltipsSettings = {}

    def __del__(self):
        self.__tooltipsSettings = None
        return

    def _validateTooltipsData(self, tooltipsSettings):
        for itemName, data in tooltipsSettings.iteritems():
            name = data.name
            localised = i18n.makeString(name)
            if name.endswith(localised):
                logger = logging.getLogger(__name__)
                logger.error("[ERROR] BattleAbilityTooltipManager: %s: Localization for '%s' not found.", itemName, data.name)
            if g_battleAbilityParamsRenderers.get(data.renderer, None) is None:
                raise SoftException("{}: '{}' No renderer with the name '{}' exists. Allowed are {}.".format(TOOLTIPS_PATH, itemName, data.renderer, g_battleAbilityParamsRenderers.keys()))

        return

    def init(self, xmlPath):
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'cannot open or read')
        xmlCtx = (None, xmlPath)
        readIdentifiers = set()
        for name, subsection in section.items():
            ctx = (xmlCtx, name)
            if name != 'item':
                _xml.raiseWrongXml(ctx, '', "Wrong section: '{}', only 'item' sections expected.".format(name))
            identifier = _xml.readString(ctx, subsection, 'identifier')
            if identifier in readIdentifiers:
                _xml.raiseWrongXml(ctx, identifier, "Identifier '{}' defined multiple times.".format(identifier))
            readIdentifiers.add(identifier)
            self.__tooltipsSettings[identifier] = ConsumableTooltipEntry(_xml.readString(ctx, subsection, 'name'), _xml.readString(ctx, subsection, 'renderer'))

        if IS_DEVELOPMENT:
            self._validateTooltipsData(self.__tooltipsSettings)
        return

    def createBattleAbilityTooltipRenderers(self, skillInfo, currentLevel, specLevel, bodyBlocks):
        equipments = vehicles.g_cache.equipments()
        levels = skillInfo.levels
        curLvlEq = equipments[levels[currentLevel].eqID]
        specLvlEq = equipments[levels[specLevel].eqID]
        for tooltipIdentifier in curLvlEq.tooltipIdentifiers:
            tooltipInfo = self.__tooltipsSettings.get(tooltipIdentifier, None)
            if tooltipInfo is None:
                logger = logging.getLogger(__name__)
                logger.error('[ERROR] createBattleAbilityTooltipRenderers: Failed to find tooltipInfo %(ttid)s for %(us)s (%(name)s).', {'ttid': tooltipIdentifier,
                 'us': specLvlEq.userString,
                 'name': specLvlEq.name})
                continue
            renderer = g_battleAbilityParamsRenderers.get(tooltipInfo.renderer, None)
            if renderer:
                renderer(bodyBlocks, curLvlEq, specLvlEq, (equipments[lvl.eqID] for lvl in levels.itervalues()), tooltipIdentifier, tooltipInfo.name)

        return


g_battleAbilityTooltipMgr = BattleAbilityTooltipManager()
g_battleAbilityTooltipMgr.init(TOOLTIPS_PATH)

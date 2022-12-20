# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/battle_ability_tooltip_params.py
import logging
from functools import partial
from collections import namedtuple
import ResMgr
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import _getFormattedNum, _cutDigits
from gui.Scaleform.locale.COMMON import COMMON
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from helpers import i18n
from items import vehicles
from soft_exception import SoftException
from constants import IS_DEVELOPMENT
from items import _xml
COLOR_SCHEME = (text_styles.stats, text_styles.bonusAppliedText)
NEUTRAL_STYLE = COLOR_SCHEME[0]
TOOLTIPS_PATH = 'gui/ability_tooltips.xml'

def _getTextStyle(idx):
    return COLOR_SCHEME[idx > 0]


def _getAttrName(param):
    return param.split('-')[0]


def _allElementsEq(values):
    return len(set(values)) == 1


class DisplayValuesMixin(object):

    @classmethod
    def _getDisplayParams(cls, curEq, eqsRange, param):
        raise NotImplementedError


class DirectValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, eqsRange, param):
        param = _getAttrName(param)
        values = [ _getFormattedNum(getattr(eq, param)) for eq in eqsRange ]
        if _allElementsEq(values):
            values = [values[0]]
        return values


class ReciprocalValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, eqsRange, param):
        param = _getAttrName(param)
        values = [ _getFormattedNum(1 / val if val != 0 else float('inf')) for val in (getattr(eq, param) for eq in eqsRange) ]
        if _allElementsEq(values):
            values = [values[0]]
        return values


class ShellStunValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, eqsRange, param):
        param = _getAttrName(param)
        shellsRange = (vehicles.getItemByCompactDescr(getattr(eq, param)) for eq in eqsRange)
        values = [ (_getFormattedNum(shell.stun.stunDuration) if shell.hasStun else 0) for shell in shellsRange ]
        if _allElementsEq(values):
            values = [values[0]]
        return values


class MultiValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, eqsRange, param):
        param = _getAttrName(param)
        eqsRange = list(eqsRange)
        params = param.split('_')
        length = len(params)
        allValues = [None] * length
        for idx, singleParam in enumerate(params):
            values = [ _getFormattedNum(getattr(eq, singleParam)) for eq in eqsRange ]
            if _allElementsEq(values):
                values = [values[0]]
            allValues[idx] = values

        return allValues


class NestedValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, eqsRange, param):
        param = _getAttrName(param)
        params = param.split('/')
        values = [ _getFormattedNum(cls._getEqParam(eq, params)) for eq in eqsRange ]
        if _allElementsEq(values):
            values = [values[0]]
        return values

    @classmethod
    def _getEqParam(cls, eq, params):
        data = {}
        if hasattr(eq, params[0]):
            data = getattr(eq, params[0])
        for key in params[1:]:
            if isinstance(data, dict):
                data = data.get(key, {})
            if hasattr(data, key):
                data = getattr(data, key)

        return data


class NestedTupleFirstValuesMixin(NestedValuesMixin):

    @classmethod
    def _getEqParam(cls, eq, params):
        data = super(NestedTupleFirstValuesMixin, cls)._getEqParam(eq, params)
        return data[0]


class NestedShellStunValuesMixin(NestedValuesMixin):

    @classmethod
    def _getDisplayParams(cls, curEq, eqsRange, param):
        shells = super(NestedShellStunValuesMixin, cls)._getDisplayParams(curEq, eqsRange, param)
        shellsRange = (vehicles.getItemByCompactDescr(shell) for shell in shells)
        values = [ (_getFormattedNum(shell.stun.stunDuration) if shell.hasStun else 0) for shell in shellsRange ]
        if _allElementsEq(values):
            values = [values[0]]
        return values


class DisplayLabelMixin(object):

    @classmethod
    def _formatParamStringInternal(cls, values, unitLocalization=None, returnArray=False):
        formatTemplate = '{}{}' if unitLocalization == COMMON.COMMON_PERCENT else '{} {}'
        unitLocalization = None if not unitLocalization else i18n.makeString(unitLocalization)
        formattedValues = []
        if values:
            for idx, dv in enumerate(values):
                dvStr = '{}'.format(abs(dv))
                if unitLocalization:
                    dvStr = formatTemplate.format(dvStr, unitLocalization)
                dvStr = _getTextStyle(idx)(dvStr)
                formattedValues.append(dvStr)

        return ' '.join(formattedValues) if not returnArray else formattedValues

    @classmethod
    def _formatParamString(cls, values, isMultiplier=True, returnArray=False):
        return cls._formatParamStringInternal(values, returnArray=returnArray)


class NumericLabelMixin(DisplayLabelMixin):

    @classmethod
    def _formatParamString(cls, values, isMultiplier=True, returnArray=False):
        return cls._formatParamStringInternal(values, returnArray=returnArray)


class SecondsLabelMixin(DisplayLabelMixin):

    @classmethod
    def _formatParamString(cls, value, isMultiplier=True, returnArray=False):
        return cls._formatParamStringInternal(value, EPIC_BATTLE.ABILITYINFO_UNITS_SECONDS, returnArray=returnArray)


class AdditionalSecondsLabelMixin(DisplayLabelMixin):

    @classmethod
    def _formatParamString(cls, value, isMultiplier=True, returnArray=False):
        return cls._formatParamStringInternal(value, EPIC_BATTLE.ABILITYINFO_UNITS_SECONDS, returnArray=returnArray)


class MeterLabelMixin(DisplayLabelMixin):

    @classmethod
    def _formatParamString(cls, value, isMultiplier=True, returnArray=False):
        return cls._formatParamStringInternal(value, EPIC_BATTLE.ABILITYINFO_UNITS_METER, returnArray=returnArray)


class PercentageLabelMixin(DisplayLabelMixin):

    @classmethod
    def _formatParamString(cls, value, isMultiplier=True, returnArray=False):
        if isMultiplier:
            value = [ _getFormattedNum(v * 100 - 100) for v in value ]
        else:
            value = [ _getFormattedNum(v * 100) for v in value ]
        return cls._formatParamStringInternal(value, COMMON.COMMON_PERCENT, returnArray=returnArray)


class PerksControllerModPercentageMixin(DisplayLabelMixin):

    @classmethod
    def _formatParamString(cls, value, isMultiplier=True, returnArray=False):
        return cls._formatParamStringInternal([ _getFormattedNum(v * 100) for v in value ], COMMON.COMMON_PERCENT, returnArray=returnArray)


class MultiMeterLabelMixin(DisplayLabelMixin):

    @classmethod
    def _formatParamString(cls, values, isMultiplier=True, returnArray=False):
        labelParts = []
        width, length = values
        for area in zip(width, length):
            values = [ int(_cutDigits(value)) for value in area ]
            areaStr = '{} x {}'.format(*values)
            unitLocalization = backport.text(R.strings.epic_battle.abilityInfo.units.meter())
            labelParts.append(NEUTRAL_STYLE('{} {}'.format(areaStr, unitLocalization)))

        return ' '.join(labelParts) if not returnArray else labelParts


class AbilityParam(object):

    @classmethod
    def extendBlocks(cls, staticBlock, dynamicBlock, curEq, eqsRange, param, title, isMultiplier=True):
        raise NotImplementedError


class FixedTextParam(AbilityParam):

    @classmethod
    def extendBlocks(cls, staticBlock, dynamicBlock, curEq, eqsRange, param, title, isMultiplier=True):
        curStr = '{}: {}'.format(text_styles.main(title), NEUTRAL_STYLE(i18n.makeString(param)))
        staticBlock.append(formatters.packTextBlockData(text=curStr, padding=formatters.packPadding(left=0, top=0)))


class TextParam(AbilityParam, DisplayValuesMixin, DisplayLabelMixin):

    @classmethod
    def extendBlocks(cls, staticBlock, dynamicBlock, curEq, eqsRange, param, title, isMultiplier=True):
        values = cls._getDisplayParams(curEq, eqsRange, param)
        if len(values) == 1:
            curStr = '{}: {}'.format(text_styles.main(title), cls._formatParamString(values, isMultiplier))
            staticBlock.append(formatters.packTextBlockData(text=curStr, padding=formatters.packPadding(left=0, top=0)))
        else:
            dynamicBlock.append(formatters.packAbilityBattleRankedItemBlockData(title=title, items=cls._formatParamString(values, isMultiplier, True)))


class MultiTextParam(AbilityParam, DisplayValuesMixin, DisplayLabelMixin):

    @classmethod
    def extendBlocks(cls, staticBlock, dynamicBlock, curEq, eqsRange, param, title, isMultiplier=True):
        values = cls._getDisplayParams(curEq, eqsRange, param)
        if len(values) > 1 and len(values[0]) == 1:
            curStr = '{}: {}'.format(text_styles.main(title), cls._formatParamString(values, isMultiplier))
            staticBlock.append(formatters.packTextBlockData(text=curStr, padding=formatters.packPadding(left=0, top=0)))
        else:
            dynamicBlock.append(formatters.packAbilityBattleRankedItemBlockData(title=title, items=cls._formatParamString(values, isMultiplier, True)))


class NestedTextParam(AbilityParam, DisplayValuesMixin, DisplayLabelMixin):

    @classmethod
    def extendBlocks(cls, staticBlock, dynamicBlock, curEq, eqsRange, param, title, isMultiplier=True):
        values = cls._getDisplayParams(curEq, eqsRange, param)
        if len(values) == 1:
            curStr = '{}: {}'.format(text_styles.main(title), cls._formatParamString(values, isMultiplier))
            staticBlock.append(formatters.packTextBlockData(text=curStr, padding=formatters.packPadding(left=0, top=0)))
        else:
            dynamicBlock.append(formatters.packAbilityBattleRankedItemBlockData(title=title, items=cls._formatParamString(values, isMultiplier, True)))


class DirectNumericTextParam(TextParam, DirectValuesMixin, NumericLabelMixin):
    pass


class DirectSecondsTextParam(TextParam, DirectValuesMixin, SecondsLabelMixin):
    pass


class DirectMetersTextParam(TextParam, DirectValuesMixin, MeterLabelMixin):
    pass


class DirectPercentageTextParam(TextParam, DirectValuesMixin, PercentageLabelMixin):
    pass


class ReciprocalPercentageTextParam(TextParam, ReciprocalValuesMixin, PercentageLabelMixin):
    pass


class ShellStunSecondsTextParam(TextParam, ShellStunValuesMixin, SecondsLabelMixin):
    pass


class MultipleMetersTextParam(MultiTextParam, MultiValuesMixin, MultiMeterLabelMixin):
    pass


class NestedMetersTextParam(NestedTextParam, NestedValuesMixin, MeterLabelMixin):
    pass


class NestedSecondsTextParam(NestedTextParam, NestedValuesMixin, SecondsLabelMixin):
    pass


class NestedPercentageTextParam(NestedTextParam, NestedValuesMixin, PercentageLabelMixin):
    pass


class NestedPercentageTextTupleValueParam(NestedTextParam, NestedTupleFirstValuesMixin, PerksControllerModPercentageMixin):
    pass


class NestedShellStunSecondsTextParam(TextParam, NestedShellStunValuesMixin, SecondsLabelMixin):
    pass


def makeRenderer(func, isMultiplier=True):
    return partial(func, isMultiplier=isMultiplier)


g_battleAbilityParamsRenderers = {'FixedTextParam': makeRenderer(FixedTextParam.extendBlocks),
 'DirectNumericTextParam': makeRenderer(DirectNumericTextParam.extendBlocks),
 'DirectSecondsTextParam': makeRenderer(DirectSecondsTextParam.extendBlocks),
 'DirectMetersTextParam': makeRenderer(DirectMetersTextParam.extendBlocks),
 'MulDirectPercentageTextParam': makeRenderer(DirectPercentageTextParam.extendBlocks),
 'AddDirectPercentageTextParam': makeRenderer(DirectPercentageTextParam.extendBlocks, isMultiplier=False),
 'MulReciprocalPercentageTextParam': makeRenderer(ReciprocalPercentageTextParam.extendBlocks),
 'AddReciprocalPercentageTextParam': makeRenderer(ReciprocalPercentageTextParam.extendBlocks, isMultiplier=False),
 'ShellStunSecondsTextParam': makeRenderer(ShellStunSecondsTextParam.extendBlocks),
 'MultiMetersTextParam': makeRenderer(MultipleMetersTextParam.extendBlocks),
 'NestedMetersTextParam': makeRenderer(NestedMetersTextParam.extendBlocks),
 'NestedSecondsTextParam': makeRenderer(NestedSecondsTextParam.extendBlocks),
 'MulNestedPercentageTextParam': makeRenderer(NestedPercentageTextParam.extendBlocks),
 'AddNestedPercentageTextParam': makeRenderer(NestedPercentageTextParam.extendBlocks, isMultiplier=False),
 'NestedShellStunSecondsTextParam': makeRenderer(NestedShellStunSecondsTextParam.extendBlocks),
 'MulNestedPercentageTextTupleValueParam': makeRenderer(NestedPercentageTextTupleValueParam.extendBlocks)}
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

    def createBattleAbilityTooltipRenderers(self, skillInfo, staticBlock, dynamicBlock, level=1):
        equipments = vehicles.g_cache.equipments()
        levels = skillInfo.levels
        curLvlEq = equipments[levels[level].eqID]
        for tooltipIdentifier in curLvlEq.tooltipIdentifiers:
            tooltipInfo = self.__tooltipsSettings.get(tooltipIdentifier, None)
            if tooltipInfo is None:
                logger = logging.getLogger(__name__)
                logger.error('[ERROR] createBattleAbilityTooltipRenderers: Failed to find tooltipInfo %(ttid)s for %(us)s (%(name)s).', {'ttid': tooltipIdentifier,
                 'us': curLvlEq.userString,
                 'name': curLvlEq.name})
                continue
            renderer = g_battleAbilityParamsRenderers.get(tooltipInfo.renderer, None)
            if renderer:
                renderer(staticBlock, dynamicBlock, curLvlEq, (equipments[lvl.eqID] for lvl in levels.itervalues()), tooltipIdentifier, tooltipInfo.name)

        return

    def getTooltipInfo(self, tooltipIdentifier):
        tooltipInfo = self.__tooltipsSettings.get(tooltipIdentifier, None)
        return (tooltipInfo.name, tooltipInfo.renderer) if tooltipInfo else (None, None)


g_battleAbilityTooltipMgr = BattleAbilityTooltipManager()
g_battleAbilityTooltipMgr.init(TOOLTIPS_PATH)

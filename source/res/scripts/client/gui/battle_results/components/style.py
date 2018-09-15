# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/style.py
from collections import namedtuple
import BigWorld
from constants import IGR_TYPE
from gui import makeHtmlString
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform import settings
from gui.battle_results.components import base
from gui.shared.formatters import text_styles
from helpers import i18n
WIDE_STAT_ROW = 'wideLine'
NORMAL_STAT_ROW = 'normalLine'
SMALL_STAT_LINE = 'smallLineUI'
_LINE_BRAKE_STR = '<br/>'
_TIME_STATS_KEY_FORMAT = '#battle_results:details/time/lbl_{0}'
_RESULT_LINE__FORMAT = '#battle_results:details/calculations/{0}'
_STATS_KEY_FORMAT = '#battle_results:team/stats/labels_{0}'
_VEHICLE_STATE_FORMAT = '#battle_results:common/vehicleState/dead{0}'
_VEHICLE_STATE_PREFIX = '{0} ('
_VEHICLE_STATE_SUFFIX = ')'
_DIFF_FORMAT = '+ {}'
_LINE_FEED = '\n'

def getUnknownPlayerName(isEnemy=False):
    return i18n.makeString(BATTLE_RESULTS.PLAYERS_ENEMY_UNKNOWN) if isEnemy else i18n.makeString(BATTLE_RESULTS.PLAYERS_TEAMMATE_UNKNOWN)


I18nDeathReason = namedtuple('I18nDeathReason', 'i18nString prefix suffix')

def makeI18nDeathReason(deathReason):
    i18nString = i18n.makeString(_VEHICLE_STATE_FORMAT.format(deathReason))
    return I18nDeathReason(i18nString, _VEHICLE_STATE_PREFIX.format(i18nString), _VEHICLE_STATE_SUFFIX)


def markValueAsError(value):
    return makeHtmlString('html_templates:lobby/battle_results', 'negative_value', {'value': value})


def markValueAsEmpty(value):
    return makeHtmlString('html_templates:lobby/battle_results', 'empty_stat_value', {'value': value})


def makeMarksOfMasteryText(marksOfMastery, totalVehicles):
    return makeHtmlString('html_templates:lobby/profileStatistics', 'marksOfMasteryText', {'marksOfMastery': marksOfMastery,
     'totalVehicles': totalVehicles})


def getIntegralFormatIfNoEmpty(value):
    return BigWorld.wg_getIntegralFormat(value) if value else markValueAsEmpty(value)


def getFractionalFormatIfNoEmpty(value):
    return BigWorld.wg_getFractionalFormat(value) if value else markValueAsEmpty(value)


_SPLASH_CHAR_NO_EMPTY_STAT = '/'
_SPLASH_CHAR_EMPTY_STAT = markValueAsEmpty(_SPLASH_CHAR_NO_EMPTY_STAT)

def getTooltipParamsStyle(paramKey=None):
    if paramKey is None:
        paramKey = BATTLE_RESULTS.COMMON_TOOLTIP_PARAMS_VAL
    return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_params_style', {'text': i18n.makeString(paramKey)})


def _makeModuleTooltipLabel(module, suffix):
    return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_crit_label', {'image': '{0}{1}'.format(module, suffix),
     'value': i18n.makeString('#item_types:{0}/name'.format(module))})


def makeCriticalModuleTooltipLabel(module):
    return _makeModuleTooltipLabel(module, 'Critical')


def makeDestroyedModuleTooltipLabel(module):
    return _makeModuleTooltipLabel(module, 'Destroyed')


def makeTankmenTooltipLabel(role):
    return makeHtmlString('html_templates:lobby/battle_results', 'tooltip_crit_label', {'image': '{0}Destroyed'.format(role),
     'value': i18n.makeString('#item_types:tankman/roles/{0}'.format(role))})


class StatRow(base.StatsItem):
    """Base class to make row VO in the tab Details."""
    __slots__ = ('text', 'label', 'lineType', 'column1', 'column2', 'column3', 'column4')

    def __init__(self, text, label, lineType, column1=_LINE_FEED, column2=_LINE_FEED, column3=_LINE_FEED, column4=_LINE_FEED):
        super(StatRow, self).__init__('')
        self.text = text
        self.label = label
        self.lineType = lineType
        self.column1 = column1
        self.column2 = column2
        self.column3 = column3
        self.column4 = column4

    def setRecord(self, record, reusable):
        pass

    def getVO(self):
        return {'label': self.label,
         'labelStripped': self.text,
         'col1': self.column1,
         'col2': self.column2,
         'col3': self.column3,
         'col4': self.column4,
         'lineType': self.lineType}


class EmptyStatRow(StatRow):
    __slots__ = ()

    def __init__(self):
        super(EmptyStatRow, self).__init__(_LINE_FEED, _LINE_FEED, None)
        return


def makeStatRow(label='', column1=None, column2=None, column3=None, column4=None, htmlKey=''):
    """This function is deprecated, use sub-classes of StatRow. It will be removed in task WOTD-50622."""
    if column2 is not None:
        lineType = WIDE_STAT_ROW
    else:
        lineType = NORMAL_STAT_ROW
    if label:
        i18nText = i18n.makeString(_RESULT_LINE__FORMAT.format(label))
        if htmlKey:
            label = makeHtmlString('html_templates:lobby/battle_results', htmlKey, {'value': i18nText})
        else:
            label = i18nText
    else:
        assert htmlKey, 'Can not find label'
        label = makeHtmlString('html_templates:lobby/battle_results', htmlKey)
        import re
        i18nText = re.sub('<[^<]+?>', '', label)
    return {'label': label,
     'labelStripped': i18nText,
     'col1': column1 if column1 is not None else _LINE_FEED,
     'col2': column2 if column2 is not None else _LINE_FEED,
     'col3': column3 if column3 is not None else _LINE_FEED,
     'col4': column4 if column4 is not None else _LINE_FEED,
     'lineType': lineType}


def makeCreditsLabel(value, canBeFaded=False, isDiff=False):
    formatted = BigWorld.wg_getGoldFormat(int(value))
    if value < 0:
        formatted = markValueAsError(formatted)
    if isDiff:
        formatted = _DIFF_FORMAT.format(formatted)
    if canBeFaded and not value:
        template = 'credits_small_inactive_label'
    else:
        template = 'credits_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeGoldLabel(value, canBeFaded=False):
    formatted = BigWorld.wg_getGoldFormat(value)
    if canBeFaded and not value:
        template = 'gold_small_inactive_label'
    else:
        template = 'gold_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeXpLabel(value, canBeFaded=False, isDiff=False):
    formatted = BigWorld.wg_getIntegralFormat(int(value))
    if value < 0:
        formatted = markValueAsError(formatted)
    if isDiff:
        formatted = _DIFF_FORMAT.format(formatted)
    if canBeFaded and not value:
        template = 'xp_small_inactive_label'
    else:
        template = 'xp_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeFreeXpLabel(value, canBeFaded=False):
    if canBeFaded and not value:
        template = 'free_xp_small_inactive_label'
    else:
        template = 'free_xp_small_label'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': BigWorld.wg_getIntegralFormat(int(value))})


def makeCrystalLabel(value):
    return makeHtmlString('html_templates:lobby/battle_results', 'crystal_small_label', {'value': BigWorld.wg_getIntegralFormat(int(value))})


def makePercentLabel(value):
    formatted = BigWorld.wg_getGoldFormat(int(value))
    template = 'percent'
    if value < 0:
        formatted = markValueAsError(formatted)
        template = 'negative_percent'
    return makeHtmlString('html_templates:lobby/battle_results', template, {'value': formatted})


def makeIGRIcon(igrType):
    if igrType == IGR_TYPE.PREMIUM:
        iconName = 'premium'
    else:
        iconName = 'basic'
    return makeHtmlString('html_templates:igr/iconSmall', iconName)


def makeIGRBonusLabel(igrIcon):
    return i18n.makeString(BATTLE_RESULTS.DETAILS_CALCULATIONS_IGRBONUS, igrIcon=igrIcon)


def makeIGRBonusValue(factor):
    return makeHtmlString('html_templates:lobby/battle_results', 'igr_bonus', {'value': BigWorld.wg_getNiceNumberFormat(factor)})


def makeDailyXPFactorValue(value):
    return makeHtmlString('html_templates:lobby/battle_results', 'multy_xp_small_label', {'value': int(value)})


def makeAOGASFactorValue(value):
    formatted = ''.join((i18n.makeString(BATTLE_RESULTS.COMMON_XPMULTIPLIERSIGN), BigWorld.wg_getFractionalFormat(value)))
    formatted = markValueAsError(formatted)
    return formatted


def makeMultiLineHtmlString(seq):
    return _LINE_BRAKE_STR.join(seq)


def makeStatValue(field, value):
    return {'label': i18n.makeString(_STATS_KEY_FORMAT.format(field)),
     'value': value}


def makeTimeStatsVO(field, value):
    return {'label': i18n.makeString(_TIME_STATS_KEY_FORMAT.format(field)),
     'value': value}


def makeRankIcon(rank):
    if not rank:
        return ''
    else:
        icon = RES_ICONS.getRankIcon('24x24', rank)
        return icon if icon is not None else RES_ICONS.getRankIcon('24x24', 0)


def makeBadgeIcon(badge):
    return settings.getBadgeIconPath(settings.BADGES_ICONS.X24, badge)


def makeRankedResultsTitle(title):
    return text_styles.promoTitle(title)


def makeRankedPointValue(pointsValue):
    return makeHtmlString('html_templates:lobby/battle_results', 'xp_small_label', {'value': text_styles.playerOnline(pointsValue)})


def makeRankedPointHugeValue(pointsValue):
    return makeHtmlString('html_templates:lobby/battle_results', 'xp_small_label', {'value': text_styles.hightlight(pointsValue)})


def makeRankedNickNameValue(name):
    return text_styles.playerOnline(name)


def makeRankedNickNameHugeValue(name):
    return text_styles.hightlight(name)


class GroupMiddleLabelBlock(base.DirectStatsItem):

    def __init__(self, label):
        super(GroupMiddleLabelBlock, self).__init__('', {'groupLabel': text_styles.middleTitle(label)})


class _SlashedValueItem(base.StatsItem):

    def _convert(self, value, reusable):
        if value:
            converted = str(value)
            isEmpty = False
        else:
            converted = markValueAsEmpty(value)
            isEmpty = True
        return (isEmpty, converted)


class _RedSlashedValueItem(base.StatsItem):

    def _convert(self, value, reusable):
        isEmpty = False if value > 0 else True
        converted = str(value)
        return (isEmpty, converted)


class _RedSlashedValuesMeta(base.ListMeta):

    def registerComponent(self, component):
        super(_RedSlashedValuesMeta, self).registerComponent(component)
        if not isinstance(component, _RedSlashedValueItem):
            raise base.StatsComponentError('Block can be added _RedSlashedValueItem only')

    def generateVO(self, components):
        if not self._registered:
            return _SPLASH_CHAR_EMPTY_STAT
        result = []
        noStats = True
        for component in components:
            isEmpty, value = component.getVO()
            noStats = noStats and isEmpty
            result.append(value)

        markValue = markValueAsEmpty if noStats else markValueAsError
        return markValue(_SPLASH_CHAR_NO_EMPTY_STAT.join(result))


class _SlashedValuesMeta(base.ListMeta):

    def registerComponent(self, component):
        super(_SlashedValuesMeta, self).registerComponent(component)
        if not isinstance(component, _SlashedValueItem):
            raise base.StatsComponentError('Block can be added SlashedValuesItem only')

    def generateVO(self, components):
        if not self._registered:
            return _SPLASH_CHAR_EMPTY_STAT
        result = []
        noStats = True
        for component in components:
            isEmpty, value = component.getVO()
            noStats = noStats and isEmpty
            result.append(value)

        if noStats:
            slash = _SPLASH_CHAR_EMPTY_STAT
        else:
            slash = _SPLASH_CHAR_NO_EMPTY_STAT
        return slash.join(result)


class TwoItemsWithSlashBlock(base.StatsBlock):

    def __init__(self, itemClass, meta=None, field=''):
        super(TwoItemsWithSlashBlock, self).__init__(meta=meta, field=field)
        self._itemClass = itemClass
        self.addComponent(0, itemClass(''))
        self.addComponent(1, itemClass(''))

    def setRecord(self, result, reusable):
        assert len(result) == 2
        for index, value in enumerate(result):
            self.getComponent(index).setRecord(value, reusable)

    def clone(self, *exclude):
        return TwoItemsWithSlashBlock(self._itemClass, meta=self._meta, field=self._field)


class SlashedValuesBlock(TwoItemsWithSlashBlock):

    def __init__(self, field=''):
        super(SlashedValuesBlock, self).__init__(_SlashedValueItem, meta=_SlashedValuesMeta(), field=field)


class RedSlashedValuesBlock(TwoItemsWithSlashBlock):

    def __init__(self, field=''):
        super(RedSlashedValuesBlock, self).__init__(_RedSlashedValueItem, meta=_RedSlashedValuesMeta(), field=field)


class MetersToKillometersItem(base.StatsItem):

    def _convert(self, value, reusable):
        converted = BigWorld.wg_getFractionalFormat(value / 1000.0)
        if not value:
            converted = markValueAsEmpty(converted)
        return converted

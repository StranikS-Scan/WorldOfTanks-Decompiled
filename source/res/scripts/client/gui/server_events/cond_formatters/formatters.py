# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/formatters.py
import nations
from gui.server_events.formatters import RELATIONS_SCHEME, RELATIONS
from helpers import i18n, int2roman
TOP_RANGE_HIGHEST = 1
TOP_RANGE_LOWEST = 15

def getFiltersLabel(labelKey, condition):
    """
    Gets localized VehicleKill or VehicleDamage condition's description by filters data
    """
    _, fNations, fLevels, fClasses = condition.parseFilters()
    keys, kwargs = [], {}
    if fNations:
        keys.append('nation')
        kwargs['nation'] = ', '.join((i18n.makeString('#menu:nations/%s' % nations.NAMES[idx]) for idx in fNations))
    if fClasses:
        keys.append('type')
        kwargs['type'] = ', '.join([ i18n.makeString('#menu:classes/%s' % name) for name in fClasses ])
    if fLevels:
        keys.append('level')
        kwargs['level'] = ', '.join([ int2roman(lvl) for lvl in fLevels ])
    labelKey = '%s/%s' % (labelKey, '_'.join(keys))
    if condition.relationValue is None and condition.isNegative:
        labelKey = '%s/not' % labelKey
    return i18n.makeString(labelKey, **kwargs)


def getResultsData(condition):
    """
    Gets main values to display BattleResults or UnitResults conditions in GUI
    :return label - localized condition's description
            relation - relation type: (more, less, equal, greaterOrEqual, ...)
            relationI18nType - GUI representation of condition (default or alternative)
            value - condition's value
    """

    def _makeStr(i18nKey, *args, **kwargs):
        if condition.isNegative():
            i18nKey = '%s/not' % i18nKey
        return i18n.makeString(i18nKey, *args, **kwargs)

    key = i18n.makeString('#quests:details/conditions/cumulative/%s' % condition.keyName)
    labelKey = '#quests:details/conditions/results'
    topRangeUpper, topRangeLower = condition.getMaxRange()
    if topRangeLower < TOP_RANGE_LOWEST:
        labelKey = '%s/%s/%s' % (labelKey, condition.localeKey, 'bothTeams' if condition.isTotal() else 'halfTeam')
        if topRangeUpper == TOP_RANGE_HIGHEST:
            label = _makeStr('%s/top' % labelKey, param=key, count=topRangeLower)
        elif topRangeLower == topRangeUpper:
            label = _makeStr('%s/position' % labelKey, param=key, position=topRangeUpper)
        else:
            label = _makeStr('%s/range' % labelKey, param=key, high=topRangeUpper, low=topRangeLower)
    elif condition.isAvg():
        label = i18n.makeString('#quests:details/conditions/results/%s/avg' % condition.localeKey, param=key)
    else:
        label = i18n.makeString('#quests:details/conditions/results/%s/simple' % condition.localeKey, param=key)
    value, relation, relationI18nType = condition.relationValue, condition.relation, RELATIONS_SCHEME.DEFAULT
    if condition.keyName == 'markOfMastery':
        relationI18nType = RELATIONS_SCHEME.ALTERNATIVE
        if condition.relationValue == 0:
            if condition.relation in (RELATIONS.EQ, RELATIONS.LSQ):
                i18nLabelKey = '#quests:details/conditions/cumulative/markOfMastery0'
            else:
                if condition.relation in (RELATIONS.LS,):
                    raise Exception('Mark of mastery 0 can be used with greater or equal relation types')
                i18nLabelKey = '#quests:details/conditions/cumulative/markOfMastery0/not'
            label, value, relation = i18n.makeString(i18nLabelKey), None, None
        else:
            i18nValueKey = '#quests:details/conditions/cumulative/markOfMastery%d' % int(condition.relationValue)
            i18nLabel = i18n.makeString('#quests:details/conditions/cumulative/markOfMastery')
            label, value, relation = i18nLabel, i18n.makeString(i18nValueKey), condition.relation
    return (label,
     relation,
     relationI18nType,
     value)


class ConditionsFormatter(object):
    """
    Formatters container to format defined quests conditions.
    """

    def __init__(self, formatters=None):
        self.__formatters = formatters or {}

    def getConditionFormatter(self, conditionName):
        condFormatter = self.__formatters.get(conditionName)
        return condFormatter if condFormatter else None

    def format(self, conditions, event):
        return []

    def hasFormatter(self, conditionName):
        return conditionName in self.__formatters


class ConditionFormatter(object):
    """
    Formatter to format quest condition.
    """

    def format(self, condition, event):
        """
        Gets list of formatted condition data to display quest condition.
        One quest condition may have several visual representations.
        """
        return self._format(condition, event)

    def _format(self, condition, event):
        return []


class CumulativableFormatter(ConditionFormatter):

    @classmethod
    def getGroupByValue(cls, condition):
        """
        Gets condition group progress key: one of ('nation', 'level', 'types', 'classes') or None
        """
        bonusData = condition.getBonusData()
        return bonusData.getGroupByValue() if condition else condition

    @classmethod
    def formatByGroup(cls, condition, groupByKey, event):
        """
        Gets list of formatted condition data with its progress separated by group.
        """
        return cls._formatByGroup(condition, groupByKey, event)

    @classmethod
    def _formatByGroup(cls, condition, groupByKey, event):
        return []

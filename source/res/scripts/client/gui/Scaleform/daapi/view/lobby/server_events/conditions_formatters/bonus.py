# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/conditions_formatters/bonus.py
from collections import defaultdict
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.server_events.conditions_formatters import _VehicleTableFormatter, QuestsBattleConditionsFormatter
from gui.Scaleform.daapi.view.lobby.server_events.conditions_formatters.postbattle import _VehiclesKillFormatter
from gui.Scaleform.daapi.view.lobby.server_events.conditions_formatters.postbattle import _VehiclesDamageFormatter
from gui.Scaleform.daapi.view.lobby.server_events.conditions_formatters.postbattle import _VehiclesStunFormatter
from gui.server_events import formatters
from gui.server_events.cond_formatters.formatters import CumulativableFormatter
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from helpers import i18n, dependency
from skeletons.gui.shared import IItemsCache

class _VehicleCumulativeFormatter(_VehicleTableFormatter, CumulativableFormatter):

    @classmethod
    def _formatByGroup(cls, condition, groupByKey, event):
        if condition.getBonusData() is not None:
            progress = condition.getProgressPerGroup()
            if groupByKey in progress:
                current, total, _, _ = progress[groupByKey]
                if event.isCompleted():
                    current, total = (None, None)
                if cls.getGroupByValue(condition) is not None:
                    return [formatters.packTextCondition(i18n.makeString(cls._getLabelKey()), relation=condition.relation, value=condition.relationValue, current=current, total=total)]
                fmtData = cls._formatData(condition, event, current, total)
                if fmtData is not None:
                    return [fmtData]
        return []

    def _format(self, condition, event):
        groupByValue = self.getGroupByValue(condition)
        if groupByValue is None:
            return self._formatByGroup(condition, groupByValue, event)
        else:
            return [self._formatData(condition, event)]
            return


class _VehiclesKillsCumulativeFormatter(_VehicleCumulativeFormatter, _VehiclesKillFormatter):
    pass


class _VehicleDamageCumulativeFormatter(_VehicleCumulativeFormatter, _VehiclesDamageFormatter):
    pass


class _VehicleStunCumulativeFormatter(_VehicleCumulativeFormatter, _VehiclesStunFormatter):
    pass


class _CumulativeResultFormatter(CumulativableFormatter):

    def _format(self, condition, event):
        groupByValue = self.getGroupByValue(condition)
        if groupByValue is None:
            return self._formatByGroup(condition, groupByValue, event)
        else:
            result = []
            if not event.isGuiDisabled():
                result.append(formatters.packTextCondition(condition.getUserString(), value=condition.getTotalValue()))
            return result
            return

    @classmethod
    def _formatByGroup(cls, condition, groupByKey, event):
        result = []
        progress = condition.getProgressPerGroup()
        if groupByKey in progress:
            if event is None or not event.isGuiDisabled():
                current, total, _, isGroupCompleted = progress[groupByKey]
                if event is not None and event.isCompleted() or isGroupCompleted:
                    result.append(formatters.packTextCondition(condition.getUserString(), value=condition.getTotalValue()))
                else:
                    isConditionCompleted = False
                    if current is not None and total is not None:
                        isConditionCompleted = current >= total
                    result.append(formatters.packTextCondition(condition.getUserString(), current=current, total=total, isCompleted=isConditionCompleted))
        return result


class QuestsBonusConditionsFormatter(QuestsBattleConditionsFormatter):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(QuestsBonusConditionsFormatter, self).__init__({'vehicleKillsCumulative': _VehiclesKillsCumulativeFormatter(),
         'vehicleDamageCumulative': _VehicleDamageCumulativeFormatter(),
         'vehicleStunCumulative': _VehicleStunCumulativeFormatter(),
         'cumulative': _CumulativeResultFormatter(),
         'unit': _CumulativeResultFormatter()})

    def formatGroupByProgresses(self, conditions, event):
        battlesLeft = {}
        groups = defaultdict(list)
        for c in conditions.getConditions().items:
            condName = c.getName()
            for groupByKey, (current, total, _, _) in c.getProgressPerGroup().iteritems():
                formatter = self.getConditionFormatter(condName)
                if formatter:
                    groups[groupByKey].extend(formatter.formatByGroup(c, groupByKey, event))
                    if condName == 'battles':
                        battlesLeft[groupByKey] = total - current

        result = []
        if not event.isCompleted():
            for groupByKey, groupConds in groups.iteritems():
                isGroupCompleted = conditions.isGroupProgressCompleted(groupByKey)
                groupByItem, packedData = self._packGroupByBlock(conditions.getGroupByValue(), groupByKey, battlesLeft.get(groupByKey), conditions.isInRow(), formatters.indexing(groupConds), isGroupCompleted)
                result.append((groupByItem, packedData, isGroupCompleted))

        def _sortFunc(a, b):
            res = int(a[2]) - int(b[2])
            return res if res else cmp(a, b)

        return map(lambda v: v[1], sorted(result, cmp=_sortFunc))

    @classmethod
    def _packGroupByBlock(cls, groupByValue, groupByKey, battlesLeft, inrow, conds, isGroupCompleted):
        if isGroupCompleted:
            conds = []
        if groupByValue == 'vehicle':
            vehicle = cls.itemsCache.items.getItemByCD(groupByKey)
            return (vehicle, formatters.packGroupByVehicleConditions(cls.itemsCache.items.getItemByCD(groupByKey), battlesLeft, inrow, conds, isCompleted=isGroupCompleted))
        if groupByValue == 'nation':
            return (GUI_NATIONS_ORDER_INDEX[groupByKey], formatters.packGroupByNationConditions(groupByKey, battlesLeft, inrow, conds, isCompleted=isGroupCompleted))
        if groupByValue == 'level':
            levelValue = int(groupByKey.replace('level ', ''))
            return (levelValue, formatters.packGroupByLevelConditions(levelValue, battlesLeft, inrow, conds, isCompleted=isGroupCompleted))
        return (VEHICLE_TYPES_ORDER_INDICES[groupByKey], formatters.packGroupByClassConditions(groupByKey, battlesLeft, inrow, conds, isCompleted=isGroupCompleted)) if groupByValue == 'class' else None

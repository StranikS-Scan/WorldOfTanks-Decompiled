# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/conditions_formatters/__init__.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters import GroupFormatter
from gui.server_events import formatters
from gui.server_events.cond_formatters.formatters import ConditionsFormatter, getFiltersLabel, ConditionFormatter
from helpers import i18n

class _VehicleTableFormatter(ConditionFormatter):

    def _format(self, condition, event):
        fmtData = self._formatData(condition, event)
        return [fmtData] if fmtData is not None else []

    @classmethod
    def _getLabelKey(cls):
        pass

    @classmethod
    def _formatData(cls, condition, event, current=None, total=None):
        if condition.isAnyVehicleAcceptable():
            if not event.isGuiDisabled():
                return formatters.packTextBlock(i18n.makeString('%s/all' % cls._getLabelKey()), value=condition.relationValue, relation=condition.relation)
        elif 'types' not in condition.data:
            if not event.isGuiDisabled():
                if current is not None and total is not None:
                    return formatters.packTextCondition(getFiltersLabel(cls._getLabelKey(), condition), current=current, total=total)
                else:
                    return formatters.packTextBlock(getFiltersLabel(cls._getLabelKey(), condition), value=condition.relationValue, relation=condition.relation)
        else:
            subBlocks = []
            titleKey = cls._getLabelKey()
            if condition.isNegative():
                titleKey = '%s/not' % titleKey
            subBlocks.append(cls._formatVehsTable(condition, event))
            if len(subBlocks):
                if event.isCompleted():
                    current, total = (None, None)
                return formatters.packContainer(i18n.makeString(titleKey), isResizable=True, isOpened=True, subBlocks=subBlocks, value=condition.relationValue, relation=condition.relation, current=current, total=total)
        return

    @classmethod
    def _formatVehsTable(cls, condition, event):
        return formatters.packVehiclesBlock(cls._makeUniqueTableID(condition, event), formatters.VEH_KILLS_HEADER, vehs=condition.getVehiclesData())

    @classmethod
    def _makeUniqueTableID(cls, condition, event):
        return formatters.makeUniqueTableID(event, condition.getUniqueName())


class OrGroupFormatter(GroupFormatter):

    def _format(self, condition, event):
        subBlocks = []
        for cond in condition.getSortedItems():
            formatter = self.getConditionFormatter(cond.getName())
            if formatter:
                subBlocks.extend(formatter.format(cond, event))

        result = []
        for idx, block in enumerate(subBlocks):
            result.append(block)
            if idx < len(subBlocks) - 1:
                result.append(formatters.packSeparator(makeHtmlString('html_templates:lobby/quests', 'or'), needAlign=True))

        return result


class AndGroupFormatter(GroupFormatter):

    def _format(self, condition, event):
        subBlocks = []
        for cond in condition.getSortedItems():
            formatter = self.getConditionFormatter(cond.getName())
            if formatter:
                subBlocks.extend(formatter.format(cond, event))

        return subBlocks


class QuestsBattleConditionsFormatter(ConditionsFormatter):

    def __init__(self, formatters):
        self.__groupConditionsFormatters = {'and': AndGroupFormatter(self),
         'or': OrGroupFormatter(self)}
        super(QuestsBattleConditionsFormatter, self).__init__(formatters)

    def getConditionFormatter(self, conditionName):
        if conditionName in self.__groupConditionsFormatters:
            return self.__groupConditionsFormatters[conditionName]
        else:
            return super(QuestsBattleConditionsFormatter, self).getConditionFormatter(conditionName)

    def format(self, conditions, event):
        result = []
        condition = conditions.getConditions()
        groupFormatter = self.getConditionFormatter(condition.getName())
        if groupFormatter:
            result.extend(groupFormatter.format(condition, event))
        return result

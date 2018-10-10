# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/formatters.py
import weakref
import nations
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.locale.NATIONS import NATIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import formatters as events_fmts
from gui.server_events.cond_formatters import FormattableField, FORMATTER_IDS, VEHICLE_TYPES, MAX_CONDITIONS_IN_OR_SECTION_SUPPORED, packSimpleTitle, packDescriptionField
from personal_missions_constants import CONDITION_ICON
from gui.server_events.conditions import GROUP_TYPE
from gui.shared.formatters import text_styles
from helpers import i18n
from soft_exception import SoftException

class ConditionsFormatter(object):

    def __init__(self, formatters=None):
        self.__formatters = formatters or {}

    def getConditionFormatter(self, conditionName):
        condFormatter = self.__formatters.get(conditionName)
        return condFormatter if condFormatter else None

    def format(self, *args, **kwargs):
        return []

    def hasFormatter(self, conditionName):
        return conditionName in self.__formatters

    def _packCondition(self, *args, **kwargs):
        raise NotImplementedError

    def _getFormattedField(self, *args, **kwargs):
        raise NotImplementedError

    def _packConditions(self, *args, **kwargs):
        raise NotImplementedError


class ConditionFormatter(object):

    def format(self, condition, event):
        return self._format(condition, event)

    def _format(self, condition, event):
        return []

    def _getSortKey(self, condition):
        return condition.getName()


class CumulativableFormatter(ConditionFormatter):

    @classmethod
    def getGroupByValue(cls, condition):
        bonusData = condition.getBonusData()
        return bonusData.getGroupByValue() if condition else condition

    @classmethod
    def formatByGroup(cls, condition, groupByKey, event):
        return cls._formatByGroup(condition, groupByKey, event)

    @classmethod
    def _formatByGroup(cls, condition, groupByKey, event):
        return []


class MissionFormatter(ConditionFormatter):

    def getTitle(self, condition):
        customTitle = condition.getCustomTitle()
        return packSimpleTitle(customTitle) if customTitle is not None else self._getTitle(condition)

    def getDescription(self, condition):
        customDescription = condition.getCustomDescription()
        return packDescriptionField(customDescription) if customDescription is not None else self._getDescription(condition)

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(QUESTS.DETAILS_CONDITIONS_TARGET_TITLE),))

    def _getDescription(self, condition):
        raise NotImplementedError

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.FOLDER

    def _packGui(self, *args, **kwargs):
        raise NotImplementedError


class SimpleMissionsFormatter(MissionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            result.append(self._packGui(condition))
        return result

    def _packGui(self, condition):
        return events_fmts.packMissionIconCondition(self.getTitle(condition), MISSIONS_ALIASES.NONE, self.getDescription(condition), self._getIconKey(condition), sortKey=self._getSortKey(condition), progressID=condition.progressID)


class MissionsVehicleListFormatter(MissionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            result.append(self._formatData(self.getTitle(condition), MISSIONS_ALIASES.NONE, condition))
        return result

    @classmethod
    def _getLabelKey(cls, condition=None):
        return condition.getLabelKey()

    @classmethod
    def _getTitleKey(cls, condition=None):
        return QUESTS.DETAILS_CONDITIONS_TARGET_TITLE

    @classmethod
    def _getTitle(cls, condition):
        return FormattableField(FORMATTER_IDS.RELATION, (condition.relationValue,
         condition.relation,
         events_fmts.RELATIONS_SCHEME.DEFAULT,
         cls._getTitleKey(condition))) if condition.isAnyVehicleAcceptable() else FormattableField(FORMATTER_IDS.COMPLEX_RELATION, (condition.relationValue, condition.relation, cls._getTitleKey(condition)))

    @classmethod
    def _getDescription(cls, condition):
        labelKey = cls._getLabelKey(condition)
        if condition.isAnyVehicleAcceptable():
            labelKey = '%s/all' % labelKey
        if condition.isNegative():
            labelKey = '%s/not' % labelKey
        return packDescriptionField(labelKey)

    def _getConditionData(self, condition):
        data = {'description': i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_HEADER),
         'list': []}
        if condition.isAnyVehicleAcceptable():
            return None
        elif 'types' not in condition.data:
            _, fNations, fLevels, fClasses = condition.parseFilters()
            data['list'].append({'label': text_styles.standard(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_NATIONS)),
             'typeIcon': RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL,
             'list': self._getConditionNationsList(fNations or []),
             'def': text_styles.main(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_NATIONS_ALL))})
            data['list'].append({'label': text_styles.standard(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_TYPE)),
             'typeIcon': RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL,
             'list': self._getConditionClassesList(fClasses or []),
             'def': text_styles.main(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_TYPE_ALL))})
            data['list'].append({'label': text_styles.standard(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_LEVEL)),
             'typeIcon': RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_ALL,
             'list': self._getConditionLevelsList(fLevels or []),
             'def': text_styles.main(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_LEVEL_ALL))})
            data['rendererLinkage'] = MISSIONS_ALIASES.VEHICLE_TYPE_RENDERER
            return {'data': data}
        else:
            conditions = [ self.__makeVehicleVO(vehicle) for vehicle, _ in condition.getVehiclesData() ]
            while len(conditions) < 6:
                conditions.append({'vehicleName': text_styles.main('---')})

            data['list'] = conditions
            data['rendererLinkage'] = MISSIONS_ALIASES.VEHICLE_ITEM_RENDERER
            return {'data': data}

    def _getConditionNationsList(self, nationIds):
        result = []
        for idx in nationIds:
            result.append({'icon': '../maps/icons/filters/nations/%s.png' % nations.NAMES[idx],
             'tooltip': i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_NATIONS_TOOLTIP, nation=i18n.makeString(NATIONS.all(nations.NAMES[idx])))})

        return result

    def _getConditionClassesList(self, classNames):
        result = []
        for name in classNames:
            result.append({'icon': '../maps/icons/filters/tanks/%s.png' % name,
             'tooltip': i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_TYPE_TOOLTIP, type=i18n.makeString(VEHICLE_TYPES[name]))})

        return result

    def _getConditionLevelsList(self, levelNames):
        result = []
        for name in levelNames:
            result.append({'icon': '../maps/icons/filters/levels/level_%s.png' % name})

        return result

    def _formatData(self, title, progressType, condition, current=None, total=None, progressData=None):
        return self._packGui(title, progressType, self.getDescription(condition), current=current, total=total, conditionData=self._getConditionData(condition), progressData=progressData, condition=condition)

    def _packGui(self, title, progressType, label, current=None, total=None, conditionData=None, progressData=None, condition=None):
        return events_fmts.packMissionIconCondition(title, progressType, label, self._getIconKey(condition), current=current, total=total, conditionData=conditionData, progressData=progressData, sortKey=self._getSortKey(condition), progressID=condition.progressID)

    @staticmethod
    def __makeVehicleVO(vehicle):
        return {'nationIcon': '../maps/icons/filters/nations/%s.png' % vehicle.nationName,
         'typeIcon': '../maps/icons/filters/tanks/%s.png' % vehicle.type,
         'levelIcon': '../maps/icons/filters/levels/level_%s.png' % vehicle.level,
         'vehicleIcon': vehicle.iconSmall,
         'vehicleName': text_styles.vehicleName(vehicle.shortUserName)}


class GroupFormatter(ConditionFormatter):

    def __init__(self, proxy):
        super(GroupFormatter, self).__init__()
        self._proxy = weakref.proxy(proxy)

    def getConditionFormatter(self, conditionName):
        return self._proxy.getConditionFormatter(conditionName)


class OrGroupFormatter(GroupFormatter):

    def __init__(self, proxy):
        super(OrGroupFormatter, self).__init__(proxy)
        self._andFormatter = _InnerAndGroupFormatter(proxy)

    def _format(self, condition, event):
        orResults = []
        conditions = condition.getSortedItems()
        if len(conditions) == MAX_CONDITIONS_IN_OR_SECTION_SUPPORED:
            for cond in conditions:
                if not cond.isHidden():
                    formatter = self.getConditionFormatter(cond.getName())
                    if formatter:
                        result = formatter.format(cond, event)
                        orResults.append(result)

        else:
            LOG_ERROR('Unsupported conditions count in quest. SSE Bug. Wrong quest xml')
        return orResults

    def getConditionFormatter(self, conditionName):
        if conditionName == GROUP_TYPE.AND:
            return self._andFormatter
        elif conditionName == GROUP_TYPE.OR:
            LOG_ERROR("Unsupported double depth 'OR' in 'OR' in quest conditions. SSE Bug. Wrong quest xml")
            return None
        else:
            return super(OrGroupFormatter, self).getConditionFormatter(conditionName)


class AndGroupFormatter(GroupFormatter):

    def __init__(self, proxy):
        super(AndGroupFormatter, self).__init__(proxy)
        self._andFormatter = _InnerAndGroupFormatter(proxy)

    def _format(self, condition, event):
        result = []
        andResults = []
        orGroups = []
        conditions = condition.getSortedItems()
        for cond in conditions:
            if not cond.isHidden():
                formatter = self.getConditionFormatter(cond.getName())
                if formatter:
                    if cond.getName() == GROUP_TYPE.OR:
                        orGroups.extend(formatter.format(cond, event))
                    else:
                        andResults.extend(formatter.format(cond, event))

        if len(orGroups) == MAX_CONDITIONS_IN_OR_SECTION_SUPPORED:
            for orList in orGroups:
                orList.extend(andResults)
                result.append(orList)

        else:
            if orGroups:
                LOG_ERROR("Unsupported double depth 'OR' in 'OR' in quest conditions. SSE Bug. Wrong quest xml")
            result.append(andResults)
        return result

    def getConditionFormatter(self, conditionName):
        return self._andFormatter if conditionName == GROUP_TYPE.AND else super(AndGroupFormatter, self).getConditionFormatter(conditionName)


class MissionsBattleConditionsFormatter(ConditionsFormatter):

    def __init__(self, formatters):
        self.__groupConditionsFormatters = {GROUP_TYPE.AND: AndGroupFormatter(self),
         GROUP_TYPE.OR: OrGroupFormatter(self)}
        super(MissionsBattleConditionsFormatter, self).__init__(formatters)

    def getConditionFormatter(self, conditionName):
        return self.__groupConditionsFormatters[conditionName] if conditionName in self.__groupConditionsFormatters else super(MissionsBattleConditionsFormatter, self).getConditionFormatter(conditionName)

    def format(self, conditions, event):
        result = []
        condition = conditions.getConditions()
        groupFormatter = self.getConditionFormatter(condition.getName())
        if groupFormatter:
            result.extend(groupFormatter.format(condition, event))
        return result

    def _packCondition(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')

    def _getFormattedField(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')

    def _packConditions(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')


class _InnerAndGroupFormatter(GroupFormatter):

    def _format(self, condition, event):
        andResults = []
        conditions = condition.getSortedItems()
        for cond in conditions:
            if not cond.isHidden():
                formatter = self.getConditionFormatter(cond.getName())
                andResults.extend(formatter.format(cond, event))

        return andResults

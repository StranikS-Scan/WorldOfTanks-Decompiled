# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/bonus.py
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events import formatters
from gui.server_events.cond_formatters import CONDITION_ICON, POSSIBLE_BATTLE_RESUTLS_KEYS, BATTLE_RESULTS_KEYS, FORMATTER_IDS, FormattableField, packDescriptionField
from gui.server_events.cond_formatters.formatters import CumulativableFormatter, MissionFormatter, MissionsVehicleListFormatter, MissionsBattleConditionsFormatter
from gui.server_events.cond_formatters.postbattle import VehiclesDamageFormatter
from gui.server_events.cond_formatters.postbattle import VehiclesKillFormatter
from gui.server_events.cond_formatters.postbattle import VehiclesStunFormatter
from helpers import i18n, dependency
from skeletons.gui.shared import IItemsCache
ZERO_COUNT = 0
DEFAULT_GROUP_BY_KEY = None

def packMissionVehicleProgress(groupByKey, current, total):
    itemsCache = dependency.instance(IItemsCache)
    vehicle = itemsCache.items.getItemByCD(groupByKey)
    return {'progressLabel': formatters.minimizedTitleCumulativeFormat(current, total),
     'nationIcon': '../maps/icons/filters/nations/%s.png' % vehicle.nationName,
     'vehicleIcon': vehicle.iconSmall,
     'vehicleName': vehicle.shortUserName,
     'vTypeIcon': '../maps/icons/filters/tanks/%s.png' % vehicle.type,
     'level': vehicle.level,
     'progress': {'maxValue': total,
                  'value': current}}


def packMissionNationProgress(groupByKey, current, total):
    return {'progressLabel': formatters.minimizedTitleCumulativeFormat(current, total),
     'nationIcon': '../maps/icons/filters/nations/%s.png' % groupByKey,
     'nationName': i18n.makeString('#menu:nations/%s' % groupByKey),
     'progress': {'maxValue': total,
                  'value': current}}


def packMissionLevelProgress(groupByKey, current, total):
    levelValue = int(groupByKey.replace('level ', ''))
    return {'progressLabel': formatters.minimizedTitleCumulativeFormat(current, total),
     'level': levelValue,
     'levelLabel': i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_LEVEL),
     'progress': {'maxValue': total,
                  'value': current}}


def packMissionClassProgress(groupByKey, current, total):
    return {'progressLabel': formatters.minimizedTitleCumulativeFormat(current, total),
     'vTypeIcon': '../maps/icons/filters/tanks/%s.png' % groupByKey,
     'vTypeLabel': i18n.makeString('#quests:classes/small/%s' % groupByKey),
     'progress': {'maxValue': total,
                  'value': current}}


GROUP_BY_FORMATTERS_DATA = {'vehicle': (packMissionVehicleProgress, MISSIONS_ALIASES.GROUPBY_VEHICLE_RENDERER),
 'nation': (packMissionNationProgress, MISSIONS_ALIASES.GROUPBY_NATION_RENDERER),
 'level': (packMissionLevelProgress, MISSIONS_ALIASES.GROUPBY_LEVEL_RENDERER),
 'class': (packMissionClassProgress, MISSIONS_ALIASES.GROUPBY_VEH_TYPE_RENDERER)}

class MissionsBonusConditionsFormatter(MissionsBattleConditionsFormatter):
    """
    Conditions formatter for 'bonus' conditions section.
    Bonus conditions have cumulative effect.
    Displayed in missions card GUI and detailed card view in the centre of card,
    Visual representation has icon, title, description and progress bar
    """

    def __init__(self):
        super(MissionsBonusConditionsFormatter, self).__init__({'vehicleKillsCumulative': _VehicleKillsCumulativeFormatter(),
         'vehicleDamageCumulative': _VehicleDamageCumulativeFormatter(),
         'vehicleStunCumulative': _VehicleStunCumulativeFormatter(),
         'cumulative': _CumulativeResultFormatter(),
         'unit': _CumulativeResultFormatter()})


class _CumulativableFormatter(MissionFormatter, CumulativableFormatter):
    """
    Base cumulative conditions formatter which accumulate progress between battles.
    """

    def _format(self, condition, event):
        if self.getGroupByValue(condition) is None:
            return self._cumulativeFormat(condition, event)
        else:
            progressData = self._getProgressData(condition, event)
            return self._groupedByFormat(condition, event, progressData)

    def _cumulativeFormat(self, condition, event):
        return []

    def _getProgressData(self, condition, event):
        result = []
        rendererLinkage = None
        if not event.isCompleted():
            groupByValue = self.getGroupByValue(condition)
            formatterData = GROUP_BY_FORMATTERS_DATA.get(groupByValue)
            if formatterData:
                formatter, rendererLinkage = formatterData
                items = sorted(condition.getProgressPerGroup().iteritems(), key=lambda (_, progress): progress[0], reverse=True)
                for groupByKey, (current, total, _, _) in items:
                    result.append(formatter(groupByKey, current, total))

        return formatters.packProgressData(rendererLinkage, result) if result and rendererLinkage is not None else None

    def _groupedByFormat(self, condition, event, progressData):
        return []

    @classmethod
    def _getComplexTitle(cls, current, total):
        return FormattableField(FORMATTER_IDS.COMPLEX, (int(current), int(total)))

    @classmethod
    def _getTitle(cls, current, total):
        return FormattableField(FORMATTER_IDS.CUMULATIVE, (int(current), int(total)))


class _CumulativeResultFormatter(_CumulativableFormatter):
    """
    Formatter for Results and UnitResults conditions. Shows accumulate battle results progress by selected key.
    """

    def _groupedByFormat(self, condition, event, progressData):
        result = []
        if not event.isGuiDisabled():
            progressType = MISSIONS_ALIASES.CUMULATIVE
            if progressData:
                maxProgressItem = progressData.progressList[0]['progress']
                current, total = maxProgressItem['value'], maxProgressItem['maxValue']
            else:
                current = ZERO_COUNT
                total = condition.getTotalValue()
            title = self._getTitle(current, total)
            result.append(self._packGui(title, condition, progressType, current, total, progressData))
        return result

    @classmethod
    def _getIconKey(cls, condition=None):
        if condition.keyName in BATTLE_RESULTS_KEYS:
            return BATTLE_RESULTS_KEYS[condition.keyName]
        elif condition.keyName in POSSIBLE_BATTLE_RESUTLS_KEYS:
            LOG_WARNING("Condition's text description is not supported.", condition.keyName)
            return POSSIBLE_BATTLE_RESUTLS_KEYS[condition.keyName]
        else:
            LOG_ERROR('Condition is not supported.', condition.keyName)
            return None

    def _getDescription(self, condition):
        return packDescriptionField(condition.getUserString())

    def _packGui(self, title, condition, progressType, current, total, progressData=None):
        description = self._getDescription(condition)
        iconKey = self._getIconKey(condition)
        return formatters.packMissionIconCondition(title, progressType, description, iconKey, current=current, total=total, progressData=progressData, sortKey=self._getSortKey(condition))

    def _cumulativeFormat(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            progress = condition.getProgressPerGroup()
            groupByKey = DEFAULT_GROUP_BY_KEY
            progressType = MISSIONS_ALIASES.CUMULATIVE
            if groupByKey in progress:
                current, total, _, isGroupCompleted = progress[groupByKey]
                if event.isCompleted() or isGroupCompleted:
                    current = total = condition.getTotalValue()
            else:
                current = ZERO_COUNT
                total = condition.getTotalValue()
            title = self._getTitle(current, total)
            result.append(self._packGui(title, condition, progressType, current, total))
        return result


class _VehicleCumulativeFormatter(_CumulativableFormatter, MissionsVehicleListFormatter):
    """
    Base cumulative formatter for vehicle kill and vehicle damage conditions
    """

    def _cumulativeFormat(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            progress = condition.getProgressPerGroup()
            groupByKey = DEFAULT_GROUP_BY_KEY
            progressType = MISSIONS_ALIASES.CUMULATIVE
            if groupByKey in progress:
                current, total, _, isGroupCompleted = progress[groupByKey]
                if event.isCompleted() or isGroupCompleted:
                    current = total = condition.getTotalValue()
            else:
                current = ZERO_COUNT
                total = condition.getTotalValue()
            title = self._getConditionTitle(condition, current, total)
            result.append(self._formatData(title, progressType, condition, current, total))
        return result

    def _groupedByFormat(self, condition, event, progressData):
        result = []
        if not event.isGuiDisabled():
            progressType = MISSIONS_ALIASES.CUMULATIVE
            if progressData:
                maxProgressItem = progressData.progressList[0]['progress']
                current, total = maxProgressItem['value'], maxProgressItem['maxValue']
            else:
                current = ZERO_COUNT
                total = condition.getTotalValue()
            title = self._getConditionTitle(condition, current, total)
            result.append(self._formatData(title, progressType, condition, current, total, progressData))
        return result

    @classmethod
    def _getConditionTitle(cls, condition, current, total):
        return cls._getTitle(current, total) if condition.isAnyVehicleAcceptable() else cls._getComplexTitle(current, total)


class _VehicleKillsCumulativeFormatter(_VehicleCumulativeFormatter, VehiclesKillFormatter):
    """
    Cumulative vehicle kill condition formatter. Shows how many vehicles player must kill to complete quest.
    """
    pass


class _VehicleDamageCumulativeFormatter(_VehicleCumulativeFormatter, VehiclesDamageFormatter):
    """
    Cumulative vehicle damage condition formatter. Shows how many damage player must shot to complete quest.
    """
    pass


class _VehicleStunCumulativeFormatter(_VehicleCumulativeFormatter, VehiclesStunFormatter):
    """
    Cumulative vehicle stun condition formatter. Shows how many stun player must shot to complete quest.
    """

    @classmethod
    def _getLabelKey(cls, condition=None):
        if condition.isEventCount():
            key = QUESTS.DETAILS_CONDITIONS_VEHICLESTUNEVENTCOUNT_CUMULATIVE
        else:
            key = QUESTS.DETAILS_CONDITIONS_VEHICLESTUN_CUMULATIVE
        return key


class BattlesCountFormatter(_CumulativeResultFormatter):
    """
    Battles count condition formatter.
    Has specific display logic depends on postbattle conditions, upperLimits and inRow section.
    Shows how many battles player has to complete quest if has 'upperLimits' section.
    Shows battles series in which player must complete all others conditions if quest has 'inRow' section.
    Shows battles count in which player should complete all others conditions if hasPostBattleConditions
    Else shows battles count to complete quest.
    """

    def __init__(self, hasPostBattleConditions):
        self.__hasPostBattleConditions = hasPostBattleConditions

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.BATTLES

    def _getDescription(self, condition):
        bonusData = condition.getBonusData()
        if bonusData is not None and bonusData.isInRow():
            descr = i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_BATTLESINROW, total=condition.getTotalValue())
        elif condition.hasUpperLimit():
            descr = i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_BATTLESUPPERLIMIT, total=condition.getTotalValue())
        elif self.__hasPostBattleConditions:
            descr = i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_BATTLES, total=condition.getTotalValue())
        else:
            descr = i18n.makeString(QUESTS.DETAILS_DOSSIER_BATTLESCOUNT)
        return packDescriptionField(descr)

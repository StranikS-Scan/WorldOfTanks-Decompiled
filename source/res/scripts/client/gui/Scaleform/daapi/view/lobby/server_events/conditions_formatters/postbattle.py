# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/conditions_formatters/postbattle.py
from gui.Scaleform.daapi.view.lobby.server_events.conditions_formatters import _VehicleTableFormatter, QuestsBattleConditionsFormatter
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events import formatters
from gui.server_events.cond_formatters.formatters import ConditionFormatter, getResultsData
from helpers import i18n

class QuestsPostBattleConditionsFormatter(QuestsBattleConditionsFormatter):

    def __init__(self):
        super(QuestsPostBattleConditionsFormatter, self).__init__({'vehicleKills': _VehiclesKillFormatter(),
         'vehicleDamage': _VehiclesDamageFormatter(),
         'win': _WinFormatter(),
         'isAlive': _SurviveFormatter(),
         'achievements': _AchievementsFormatter(),
         'clanKills': _ClanKillsFormatter(),
         'results': _BattleResultsFormatter(),
         'unitResults': _UnitResultsFormatter()})


class _BattleResultsFormatter(ConditionFormatter):

    def _format(self, condition, event):
        if event.isGuiDisabled():
            return []
        label, relation, relationI18nType, value = getResultsData(condition)
        return [formatters.packTextBlock(label, value=value, relation=relation, relationI18nType=relationI18nType)]


class _UnitResultsFormatter(ConditionFormatter):

    def _format(self, condition, event):
        results = []
        if not event.isGuiDisabled():
            isAllAlive = condition.isAllAlive()
            if isAllAlive is not None:
                key = 'alive' if isAllAlive else 'alive/not'
                results.append(formatters.packTextBlock(i18n.makeString('#quests:details/conditions/results/unit/%s' % key)))
            resultsFormatter = _BattleResultsFormatter()
            for c in condition.getResults():
                results.extend(resultsFormatter.format(c, event))

        return results


class _ClanKillsFormatter(ConditionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            camos = []
            for camo in condition.getCamos2ids():
                camoI18key = '#quests:details/conditions/clanKills/camo/%s' % str(camo)
                if i18n.doesTextExist(camoI18key):
                    camos.append(i18n.makeString(camoI18key))

            i18nKey = '#quests:details/conditions/clanKills'
            if condition.isNegative():
                i18nKey = '%s/not' % i18nKey
            if len(camos):
                result = [formatters.packTextBlock(i18n.makeString(i18nKey, camos=', '.join(camos)))]
        return result


class _WinFormatter(ConditionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            key = 'win' if condition.getValue() else 'notWin'
            result.append(formatters.packTextBlock(i18n.makeString('#quests:details/conditions/%s' % key)))
        return result


class _SurviveFormatter(ConditionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            key = 'survive' if condition.getValue() else 'notSurvive'
            result.append(formatters.packTextBlock(i18n.makeString('#quests:details/conditions/%s' % key)))
        return result


class _AchievementsFormatter(ConditionFormatter):

    def _format(self, condition, event):
        if event.isGuiDisabled():
            return []
        key = formatters.getAchievementsConditionKey(condition)
        return [formatters.packIconTextBlock(formatters.formatBright('#quests:details/conditions/%s' % key), iconTexts=[ formatters.packAchieveElement(idx) for idx in condition.getValue() ])]


class _VehiclesKillFormatter(_VehicleTableFormatter):

    @classmethod
    def _getLabelKey(cls):
        return QUESTS.DETAILS_CONDITIONS_VEHICLESKILLS


class _VehiclesDamageFormatter(_VehicleTableFormatter):

    @classmethod
    def _getLabelKey(cls):
        return QUESTS.DETAILS_CONDITIONS_VEHICLEDAMAGE

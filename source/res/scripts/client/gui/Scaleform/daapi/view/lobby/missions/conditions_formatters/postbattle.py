# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/conditions_formatters/postbattle.py
from debug_utils import LOG_WARNING, LOG_ERROR
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.Scaleform.daapi.view.lobby.missions.conditions_formatters import CONDITION_ICON, POSSIBLE_BATTLE_RESUTLS_KEYS, BATTLE_RESULTS_KEYS, SimpleMissionsFormatter, MissionsVehicleListFormatter, MissionsBattleConditionsFormatter, FormattableField, FORMATTER_IDS, packDescriptionField
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import formatters
from gui.server_events.cond_formatters.formatters import getResultsData, TOP_RANGE_LOWEST
from gui.shared.gui_items.dossier import factories
from helpers import i18n

def _packAchieveElement(achieveRecordID):
    _, achieveName = DB_ID_TO_RECORD[achieveRecordID]
    return i18n.makeString('#achievements:%s' % achieveName)


def _packAchievementsList(achivementsIDs):
    result = []
    for id in achivementsIDs:
        block, achieveName = DB_ID_TO_RECORD[id]
        factory = factories.getAchievementFactory((block, achieveName))
        item = factory.create(value=0)
        result.append({'block': block,
         'type': achieveName,
         'tooltip': TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS,
         'icon': item.getSmallIcon(),
         'label': item.getUserName()})

    return result


class MissionsPostBattleConditionsFormatter(MissionsBattleConditionsFormatter):
    """
    Conditions formatter for 'postbattle' conditions section.
    Postbattle conditions must be complete in one battle.
    Displayed in missions card GUI and detailed card view in the centre of card.
    Visual representation has icon, title, description
    """

    def __init__(self):
        super(MissionsPostBattleConditionsFormatter, self).__init__({'vehicleKills': _VehiclesKillFormatter(),
         'vehicleDamage': _VehiclesDamageFormatter(),
         'win': _WinFormatter(),
         'isAlive': _SurviveFormatter(),
         'achievements': _AchievementsFormatter(),
         'clanKills': _ClanKillsFormatter(),
         'results': _BattleResultsFormatter(),
         'unitResults': _UnitResultsFormatter()})


class _ClanKillsFormatter(SimpleMissionsFormatter):
    """
    Formatter for ClanKill condition.
    Shows groups of players which player should kill to complete quest.
    """

    def _getDescription(self, condition):
        camos = []
        for camo in condition.getCamos2ids():
            camoI18key = '#quests:details/conditions/clanKills/camo/%s' % str(camo)
            if i18n.doesTextExist(camoI18key):
                camos.append(i18n.makeString(camoI18key))

        i18nKey = '#quests:details/conditions/clanKills'
        if condition.isNegative():
            i18nKey = '%s/not' % i18nKey
        return packDescriptionField(i18n.makeString(i18nKey, camos=', '.join(camos)))

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.KILL_VEHICLES

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(QUESTS.DETAILS_CONDITIONS_CLANKILLS_TITLE),))


class _WinFormatter(SimpleMissionsFormatter):
    """
    Formatter for Win condition. Shows battles count, where player should win.
    """

    def _getDescription(self, condition):
        key = 'win' if condition.getValue() else 'notWin'
        return packDescriptionField(i18n.makeString('#quests:details/conditions/%s' % key))

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.WIN

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(QUESTS.DETAILS_CONDITIONS_WIN_TITLE),))


class _SurviveFormatter(SimpleMissionsFormatter):
    """
    Formatter for Survive condition. Shows battles count, where player should survive.
    """

    def _getDescription(self, condition):
        key = 'survive' if condition.getValue() else 'notSurvive'
        return packDescriptionField(i18n.makeString('#quests:details/conditions/%s' % key))

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.SURVIVE

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(QUESTS.DETAILS_CONDITIONS_ALIVE_TITLE),))


class _AchievementsFormatter(SimpleMissionsFormatter):
    """
    Formatter for Achievements condition. Shows which achievements player should get to complete quest.
    """

    def _getDescription(self, condition):
        key = formatters.getAchievementsConditionKey(condition)
        iconTexts = [ _packAchieveElement(idx) for idx in condition.getValue() ]
        description = '%s %s' % (i18n.makeString('#quests:details/conditions/%s' % key), ', '.join(iconTexts))
        return packDescriptionField(description)

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.AWARD

    def _packGui(self, condition):
        achievementsList = _packAchievementsList(condition.getValue())
        return formatters.packMissionIconCondition(self._getTitle(condition), MISSIONS_ALIASES.NONE, self._getDescription(condition), self._getIconKey(), conditionData={'data': {'rendererLinkage': MISSIONS_ALIASES.ACHIEVEMENT_RENDERER,
                  'list': achievementsList,
                  'icon': RES_ICONS.get90ConditionIcon(self._getIconKey()),
                  'description': i18n.makeString(QUESTS.DETAILS_CONDITIONS_ACHIEVEMENTS)}})

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(QUESTS.DETAILS_CONDITIONS_ACHIEVEMENTS_TITLE),))


class _VehiclesKillFormatter(MissionsVehicleListFormatter):
    """
    VehicleKill condition formatter. Shows how many vehicles player must kill in one battle to complete quest.
    """

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.KILL_VEHICLES

    @classmethod
    def _getLabelKey(cls):
        return QUESTS.DETAILS_CONDITIONS_VEHICLESKILLS


class _VehiclesDamageFormatter(MissionsVehicleListFormatter):
    """
    VehicleDamage condition formatter. Shows how many damage player must shot in one battle to complete quest.
    """

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.DAMAGE

    @classmethod
    def _getLabelKey(cls):
        return QUESTS.DETAILS_CONDITIONS_VEHICLEDAMAGE


class _BattleResultsFormatter(SimpleMissionsFormatter):
    """
    Formatter for Results and UnitResults conditions.
    Shows battle result parameter value which player must get to complete quest.
    """

    @classmethod
    def _getTitle(cls, condition):
        label, relation, relationI18nType, value = getResultsData(condition)
        topRangeUpper, topRangeLower = condition.getMaxRange()
        if topRangeLower < TOP_RANGE_LOWEST:
            return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(QUESTS.DETAILS_CONDITIONS_TOP_TITLE, value=topRangeLower),))
        elif value is None:
            return super(_BattleResultsFormatter, cls)._getTitle()
        elif condition.keyName == 'markOfMastery':
            return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (value,))
        else:
            return FormattableField(FORMATTER_IDS.RELATION, (value, relation, relationI18nType))
            return

    def _packGui(self, condition):
        label, relation, relationI18nType, value = getResultsData(condition)
        return formatters.packMissionIconCondition(self._getTitle(condition), MISSIONS_ALIASES.NONE, packDescriptionField(label), self._getIconKey(condition))

    @classmethod
    def _getIconKey(cls, condition=None):
        topRangeUpper, topRangeLower = condition.getMaxRange()
        if topRangeLower < TOP_RANGE_LOWEST:
            return CONDITION_ICON.TOP
        elif condition.keyName in BATTLE_RESULTS_KEYS:
            return BATTLE_RESULTS_KEYS[condition.keyName]
        elif condition.keyName in POSSIBLE_BATTLE_RESUTLS_KEYS:
            LOG_WARNING("Condition's text description is not supported.", condition.keyName)
            return POSSIBLE_BATTLE_RESUTLS_KEYS[condition.keyName]
        else:
            LOG_ERROR('Condition is not supported.', condition.keyName)
            return None


class _UnitResultsFormatter(SimpleMissionsFormatter):
    """
    Formatter for UnitResults conditions.
    Shows battle results parameters values which unit must get to complete quest.
    UnitResults condition may contain several conditions inside.
    """

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            isAllAlive = condition.isAllAlive()
            if isAllAlive is not None:
                result.append(self._packGui(condition))
            resultsFormatter = _BattleResultsFormatter()
            for c in condition.getResults():
                result.extend(resultsFormatter.format(c, event))

        return result

    def _getDescription(self, condition):
        isAllAlive = condition.isAllAlive()
        key = 'alive' if isAllAlive else 'alive/not'
        description = i18n.makeString('#quests:details/conditions/results/%s/%s' % (condition.getUnitKey(), key))
        return packDescriptionField(description)

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.SURVIVE

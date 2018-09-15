# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/postbattle.py
from collections import namedtuple
from constants import ATTACK_REASON
from debug_utils import LOG_WARNING, LOG_ERROR
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import formatters
from gui.server_events.cond_formatters import CONDITION_ICON, POSSIBLE_BATTLE_RESUTLS_KEYS, BATTLE_RESULTS_KEYS, BATTLE_RESULTS_AGGREGATED_KEYS, FORMATTER_IDS, FormattableField, packDescriptionField, packSimpleTitle, TOP_RANGE_LOWEST, getResultsData
from gui.server_events.cond_formatters.formatters import ConditionFormatter, ConditionsFormatter, SimpleMissionsFormatter, MissionsVehicleListFormatter, GroupFormatter, MissionsBattleConditionsFormatter
from gui.server_events.conditions import GROUP_TYPE
from gui.server_events.formatters import RELATIONS_SCHEME
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


def _makeKeyNegativeIf(key, cond):
    if cond:
        key = '%s/not' % key
    return key


class MissionsPostBattleConditionsFormatter(MissionsBattleConditionsFormatter):
    """
    Conditions formatter for 'postbattle' conditions section.
    Postbattle conditions must be complete in one battle.
    Displayed in missions card GUI and detailed card view in the centre of card.
    Visual representation has icon, title, description
    """

    def __init__(self):
        super(MissionsPostBattleConditionsFormatter, self).__init__({'vehicleKills': VehiclesKillFormatter(),
         'vehicleDamage': VehiclesDamageFormatter(),
         'vehicleStun': VehiclesStunFormatter(),
         'win': _WinFormatter(),
         'isAlive': _SurviveFormatter(),
         'achievements': _AchievementsFormatter(),
         'clanKills': _ClanKillsFormatter(),
         'results': _BattleResultsFormatter(),
         'unitResults': _UnitResultsFormatter(),
         'crits': _CritsFormatter(),
         'multiStunEvent': _MultiStunEventFormatter()})


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
    def _getTitle(cls, condition):
        return packSimpleTitle(QUESTS.DETAILS_CONDITIONS_CLANKILLS_TITLE)


class _WinFormatter(SimpleMissionsFormatter):
    """
    Formatter for Win condition. Shows battles count, where player should win.
    """

    def _getDescription(self, condition):
        return packDescriptionField('')

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.WIN

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return packSimpleTitle(QUESTS.DETAILS_CONDITIONS_WIN_TITLE)


class _SurviveFormatter(SimpleMissionsFormatter):
    """
    Formatter for Survive condition. Shows battles count, where player should survive.
    """

    def _getDescription(self, condition):
        return packDescriptionField('')

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.SURVIVE

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return packSimpleTitle(QUESTS.DETAILS_CONDITIONS_ALIVE_TITLE)


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
        return formatters.packMissionIconCondition(self._getTitle(condition), MISSIONS_ALIASES.NONE, self._getDescription(condition), self._getIconKey(condition), conditionData={'data': {'rendererLinkage': MISSIONS_ALIASES.ACHIEVEMENT_RENDERER,
                  'list': achievementsList,
                  'icon': RES_ICONS.get90ConditionIcon(self._getIconKey()),
                  'description': i18n.makeString(QUESTS.DETAILS_CONDITIONS_ACHIEVEMENTS)}}, sortKey=self._getSortKey(condition))

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return packSimpleTitle(QUESTS.DETAILS_CONDITIONS_ACHIEVEMENTS_TITLE)


class VehiclesKillFormatter(MissionsVehicleListFormatter):
    """
    VehicleKill condition formatter. Shows how many vehicles player must kill in one battle to complete quest.
    """

    @classmethod
    def _getIconKey(cls, condition=None):
        if condition.getFireStarted() or condition.getAttackReason() == ATTACK_REASON.FIRE:
            return CONDITION_ICON.FIRE
        return CONDITION_ICON.RAM if condition.getAttackReason() == ATTACK_REASON.RAM else CONDITION_ICON.KILL_VEHICLES

    @classmethod
    def _getTitleKey(cls, condition=None):
        return _makeKeyNegativeIf(QUESTS.DETAILS_CONDITIONS_VEHICLESKILLS_TITLE, condition.isNegative())


class VehiclesDamageFormatter(MissionsVehicleListFormatter):
    """
    VehicleDamage condition formatter. Shows how many damage player must shot in one battle to complete quest.
    """

    @classmethod
    def _getIconKey(cls, condition=None):
        if condition.getFireStarted() or condition.getAttackReason() == ATTACK_REASON.FIRE:
            return CONDITION_ICON.FIRE
        if condition.getAttackReason() == ATTACK_REASON.RAM:
            return CONDITION_ICON.RAM
        return CONDITION_ICON.HURT_VEHICLES if 'classes' in condition.data or 'classesDiversity' in condition.data else CONDITION_ICON.DAMAGE

    @classmethod
    def _getTitleKey(cls, condition=None):
        if condition.getFireStarted() or condition.getAttackReason() == ATTACK_REASON.FIRE:
            titleKey = QUESTS.DETAILS_CONDITIONS_FIREDAMAGE_TITLE
        elif condition.getAttackReason() == ATTACK_REASON.RAM:
            titleKey = QUESTS.DETAILS_CONDITIONS_RAMDAMAGE_TITLE
        else:
            titleKey = QUESTS.DETAILS_CONDITIONS_VEHICLEDAMAGE_TITLE
        return _makeKeyNegativeIf(titleKey, condition.isNegative())


class VehiclesStunFormatter(MissionsVehicleListFormatter):
    """
    VehicleStun condition formatter. Shows how many stuns player must do in one battle to complete quest.
    """

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.ASSIST_STUN if condition.isEventCount() else CONDITION_ICON.ASSIST_STUN_DURATION

    @classmethod
    def _getTitleKey(cls, condition=None):
        return _makeKeyNegativeIf(QUESTS.DETAILS_CONDITIONS_VEHICLESTUN_TITLE, condition.isNegative())


class _MultiStunEventFormatter(SimpleMissionsFormatter):
    """
    Formatter for MultiStunEvent condition.
    Shows how many enemies player simultaneously must stun in one battle to complete quest.
    """

    @classmethod
    def _getDescription(cls, condition):
        key = _makeKeyNegativeIf(QUESTS.DETAILS_CONDITIONS_MULTISTUNEVENT, condition.isNegative())
        return packDescriptionField(i18n.makeString(key, count=condition.stunnedByShot))

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.ASSIST_STUN_MULTY

    @classmethod
    def _getTitle(cls, condition):
        return FormattableField(FORMATTER_IDS.RELATION, (condition.relationValue,
         condition.relation,
         RELATIONS_SCHEME.DEFAULT,
         cls._getTitleKey(condition)))

    @classmethod
    def _getTitleKey(cls, condition=None):
        return _makeKeyNegativeIf(QUESTS.DETAILS_CONDITIONS_MULTISTUNEVENT_TITLE, condition.isNegative())


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
            return packSimpleTitle(i18n.makeString(QUESTS.DETAILS_CONDITIONS_TOP_TITLE, value=topRangeLower))
        elif value is None:
            return super(_BattleResultsFormatter, cls)._getTitle()
        else:
            return packSimpleTitle(value) if condition.keyName == 'markOfMastery' else FormattableField(FORMATTER_IDS.RELATION, (value, relation, relationI18nType))

    def _getDescription(self, condition):
        label, _, _, _ = getResultsData(condition)
        return packDescriptionField(i18n.makeString(label))

    @classmethod
    def _getIconKey(cls, condition=None):
        topRangeUpper, topRangeLower = condition.getMaxRange()
        aggregatedKeys = condition.getAggregatedKeys()
        if topRangeLower < TOP_RANGE_LOWEST:
            return CONDITION_ICON.TOP
        elif condition.keyName is None and aggregatedKeys:
            return BATTLE_RESULTS_AGGREGATED_KEYS.get(aggregatedKeys, CONDITION_ICON.FOLDER)
        elif condition.keyName in BATTLE_RESULTS_KEYS:
            return BATTLE_RESULTS_KEYS[condition.keyName]
        elif condition.keyName in POSSIBLE_BATTLE_RESUTLS_KEYS:
            LOG_WARNING("Condition's text description is not supported.", condition.keyName)
            return POSSIBLE_BATTLE_RESUTLS_KEYS[condition.keyName]
        else:
            LOG_ERROR('Condition is not supported.', condition.keyName)
            return super(_BattleResultsFormatter, cls)._getIconKey()

    def _getSortKey(self, condition):
        _, topRangeLower = condition.getMaxRange()
        return 'top' if topRangeLower < TOP_RANGE_LOWEST else condition.keyName or condition.getName()


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
                if not c.isHidden():
                    result.extend(resultsFormatter.format(c, event))

            unitVehDamageCond = condition.getUnitVehDamage()
            if unitVehDamageCond and not unitVehDamageCond.isHidden():
                formatter = VehiclesDamageFormatter()
                result.extend(formatter.format(unitVehDamageCond, event))
            unitVehKillCond = condition.getUnitVehKills()
            if unitVehKillCond and not unitVehKillCond.isHidden():
                formatter = VehiclesKillFormatter()
                result.extend(formatter.format(unitVehKillCond, event))
        return result

    def _getDescription(self, condition):
        isAllAlive = condition.isAllAlive()
        key = 'alive' if isAllAlive else 'alive/not'
        description = i18n.makeString('#quests:details/conditions/results/%s/%s' % (condition.getUnitKey(), key))
        return packDescriptionField(description)

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.SURVIVE


class _CritFormatter(SimpleMissionsFormatter):
    """
    Formatter for single crit section in crits condition
    Shows critical hit which player must do in battle
    """

    @classmethod
    def _getTitle(cls, condition):
        return FormattableField(FORMATTER_IDS.RELATION, (condition.relationValue, condition.relation))

    def _getDescription(self, condition):
        key = '#quests:details/conditions/crits/%s/%s' % (condition.getCritType(), condition.getCritName())
        if condition.isNegative():
            key = '%s/not' % key
        return packDescriptionField(i18n.makeString(key))

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.MODULE_CRIT


class _CritsFormatter(ConditionFormatter):
    """
    Formatter for CritsGroup condition
    Shows critical hits which player must do in battle
    Condition is compound and may contain several crits
    """

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            critFormatter = _CritFormatter()
            for c in condition.getCrits():
                if not c.isHidden():
                    result.extend(critFormatter.format(c, event))

        return result


class PersonalMissionsConditionsFormatter(ConditionsFormatter):
    """
    Base conditions formatter for personal missions with custom group formatters
    """

    def __init__(self, formatters):
        super(PersonalMissionsConditionsFormatter, self).__init__(formatters)
        self.__groupConditionsFormatters = {GROUP_TYPE.AND: PersonalAndGroupFormatter(self),
         GROUP_TYPE.OR: PersonalOrGroupFormatter(self)}

    def getConditionFormatter(self, conditionName):
        return self.__groupConditionsFormatters[conditionName] if conditionName in self.__groupConditionsFormatters else super(PersonalMissionsConditionsFormatter, self).getConditionFormatter(conditionName)

    def format(self, conditions, event):
        result = []
        condition = conditions.getConditions()
        groupFormatter = self.getConditionFormatter(condition.getName())
        if groupFormatter:
            result.extend(groupFormatter.format(condition, event))
        return result


class PersonalMissionsPostBattleConditionsFormatter(PersonalMissionsConditionsFormatter):
    """
    Conditions formatter for 'postbattle' conditions section in personal missions.
    Postbattle conditions must be complete in one battle.
    Displayed in detailed personal mission view in the centre of card.
    Visual representation has icon, title, description
    """

    def __init__(self):
        super(PersonalMissionsPostBattleConditionsFormatter, self).__init__({'vehicleKills': VehiclesKillFormatter(),
         'vehicleDamage': VehiclesDamageFormatter(),
         'vehicleStun': VehiclesStunFormatter(),
         'win': _WinFormatter(),
         'isAlive': _SurviveFormatter(),
         'achievements': _AchievementsFormatter(),
         'clanKills': _ClanKillsFormatter(),
         'results': _BattleResultsFormatter(),
         'unitResults': _UnitResultsFormatter(),
         'crits': _CritsFormatter(),
         'multiStunEvent': _MultiStunEventFormatter()})


GroupResult = namedtuple('GroupResult', 'isOrGroup, results')

class PersonalOrGroupFormatter(GroupFormatter):
    """
    Formatter for quests condition's groups 'OR' for personal missions.
    Collect and format conditions from group recursive.
    Some conditions are marked as hidden and not displayed in GUI
    in that case we simplify groups which contains only one condition
    OR group with only one visible condition transforms into single condition without group
    """

    def _format(self, condition, event):
        totalResult = []
        conditions = condition.getSortedItems()
        orLists = []
        for cond in conditions:
            if not cond.isHidden():
                formatter = self.getConditionFormatter(cond.getName())
                if formatter:
                    orLists.append(formatter.format(cond, event))

        hasAlternativeConditions = len(orLists) > 1
        if orLists:
            for results in orLists:
                totalResult.extend(results)

        return [GroupResult(hasAlternativeConditions, totalResult)] if len(totalResult) > 1 else totalResult


class PersonalAndGroupFormatter(GroupFormatter):
    """
    Formatter for quests condition's groups 'AND' for personal missions.
    Collect and format conditions from group recursive.
    Some conditions are marked as hidden and not displayed in GUI
    in that case we simplify groups which contains only one condition
    AND group with only one visible condition transforms into single condition without group
    """

    def _format(self, condition, event):
        result = []
        conditions = condition.getSortedItems()
        for cond in conditions:
            if not cond.isHidden():
                formatter = self.getConditionFormatter(cond.getName())
                if formatter:
                    result.extend(formatter.format(cond, event))

        return [GroupResult(False, result)] if len(result) > 1 else result

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/challenges/postbattle.py
from __future__ import absolute_import, division
import typing
import logging
from constants import ATTACK_REASON
from dossiers2.custom.records import DB_ID_TO_RECORD
from gui.impl import backport
from gui.server_events.cond_formatters import TOP_RANGE_LOWEST
from gui.server_events.cond_formatters.challenges.constants import CHALLENGES_BATTLE_RESULT_ICONS, CONDITION_TEXT_RES, DEFAULT_CONDITION_TITLE_TEXT_RES, DEFAULT_CONDITION_TEXT_RES, ACHIEVEMENT_TEXT_RES, ConditionIcon, TextResKey, TemplateParam
from gui.server_events.cond_formatters.challenges.helpers import packDescriptionField, packTitleField, getRelationValue
from gui.server_events.cond_formatters.formatters import SimpleMissionsFormatter, MissionsBattleConditionsFormatter
from shared_utils import first
from helpers import time_utils
if typing.TYPE_CHECKING:
    from gui.server_events.conditions import _Condition, _VehsListCondition, BattleResults, Achievements
    from gui.server_events.cond_formatters import FormattableField
    from gui.impl.gen_utils import DynAccessor
_logger = logging.getLogger(__name__)

class ChallengePostBattleConditionsFormatter(MissionsBattleConditionsFormatter):

    def __init__(self):
        super(ChallengePostBattleConditionsFormatter, self).__init__({'vehicleKills': ChallengeVehicleKillsFormatter(),
         'vehicleDamage': ChallengeVehicleDamageFormatter(),
         'achievements': ChallengeAchievementsFormatter(),
         'results': ChallengeBattleResultsFormatter(),
         'vehicleStun': ChallengeDefaultFormatter(),
         'win': ChallengeDefaultFormatter(),
         'isAlive': ChallengeDefaultFormatter(),
         'clanKills': ChallengeDefaultFormatter(),
         'unitResults': ChallengeDefaultFormatter(),
         'crits': ChallengeDefaultFormatter(),
         'multiStunEvent': ChallengeDefaultFormatter(),
         'firstBlood': ChallengeDefaultFormatter(),
         'vehicleBlockedByArmor': ChallengeDefaultFormatter()})


class ChallengeDefaultFormatter(SimpleMissionsFormatter):

    @classmethod
    def _getTitle(cls, condition):
        return packTitleField(DEFAULT_CONDITION_TITLE_TEXT_RES)

    def _getDescription(self, condition):
        return packDescriptionField(DEFAULT_CONDITION_TEXT_RES)

    @classmethod
    def _getIconKey(cls, condition=None):
        return ConditionIcon.DEFAULT


class ChallengeVehicleListFormatter(ChallengeDefaultFormatter):

    @classmethod
    def _getLabelRes(cls, condition):
        raise NotImplementedError

    def _getDescription(self, condition):
        attackReason = condition.getAttackReason()
        distance = condition.getDistance()
        timeLimit = condition.getTimeLimit()
        vehClasses = condition.parseClasses(condition.data)
        classesDiversity = condition.getClassesDiversity()
        textRes = self._getLabelRes(condition)
        textParams = {TemplateParam.GOAL: getRelationValue(condition)}
        if attackReason == ATTACK_REASON.RAM:
            textRes = textRes.dyn(attackReason)
        if distance is not None:
            if distance == 0:
                textRes = textRes.dyn(TextResKey.WITHIN_VIEW_RANGE)
            elif distance > 0:
                textRes = textRes.dyn(TextResKey.MIN_DISTANCE)
                textParams[TemplateParam.DISTANCE] = backport.getIntegralFormat(distance)
            else:
                textRes = textRes.dyn(TextResKey.MAX_DISTANCE)
                textParams[TemplateParam.DISTANCE] = backport.getIntegralFormat(-distance)
        if timeLimit is not None:
            textRes = textRes.dyn(TextResKey.LIMITED_TIME)
            textParams[TemplateParam.TIME_LIMIT] = backport.getNiceNumberFormat(timeLimit / time_utils.ONE_MINUTE)
        if condition.getwhileEnemyInvisible():
            textRes = textRes.dyn(TextResKey.WHILE_ENEMY_INVISIBLE)
        if condition.getWhileInvisible():
            textRes = textRes.dyn(TextResKey.WHILE_INVISIBLE)
        if condition.getWhileFullHealth():
            textRes = textRes.dyn(TextResKey.WHILE_FULL_HEALTH)
        if vehClasses:
            if len(vehClasses) > 1:
                _logger.error('More than 1 class in condition: %s', condition.data)
            vehClass = first(vehClasses)
            textRes = textRes.dyn(TextResKey.CLASSES)
            textParams[TemplateParam.VEHICLE_CLASS] = backport.text(CONDITION_TEXT_RES.classes.dyn(vehClass)())
        if classesDiversity is not None:
            textRes = textRes.dyn(TextResKey.CLASSES_DIVERSITY)
            textParams[TemplateParam.CLASS_COUNT] = backport.getIntegralFormat(classesDiversity)
        return packDescriptionField(textRes, **textParams)


class ChallengeVehicleDamageFormatter(ChallengeVehicleListFormatter):

    @classmethod
    def _getLabelRes(cls, condition):
        textRes = CONDITION_TEXT_RES.damageDealt
        if condition.isEventCount():
            textRes = textRes.dyn(TextResKey.EVENT_COUNT)
        return textRes

    @classmethod
    def _getIconKey(cls, condition=None):
        return ConditionIcon.RAM if condition.getAttackReason() == ATTACK_REASON.RAM else ConditionIcon.HURT_VEHICLES

    @classmethod
    def _getTitle(cls, condition):
        textRes = CONDITION_TEXT_RES.damageDealt
        if condition.getAttackReason() == ATTACK_REASON.RAM:
            textRes = textRes.dyn(TextResKey.RAMMING)
        return packTitleField(textRes.dyn(TextResKey.TITLE))


class ChallengeVehicleKillsFormatter(ChallengeVehicleListFormatter):

    @classmethod
    def _getLabelRes(cls, condition):
        return CONDITION_TEXT_RES.kills

    @classmethod
    def _getIconKey(cls, condition=None):
        return ConditionIcon.KILL_VEHICLES

    @classmethod
    def _getTitle(cls, condition):
        return packTitleField(CONDITION_TEXT_RES.kills.title)


class ChallengeBattleResultsFormatter(ChallengeDefaultFormatter):

    @classmethod
    def _getTitle(cls, condition):
        keyName = condition.keyName
        _, topRangeLower = condition.getMaxRange()
        if topRangeLower < TOP_RANGE_LOWEST:
            return packTitleField(CONDITION_TEXT_RES.top.title)
        elif keyName is not None:
            return packTitleField(CONDITION_TEXT_RES.dyn(keyName).dyn(TextResKey.TITLE))
        else:
            return packTitleField(CONDITION_TEXT_RES.aggregated.title) if condition.getAggregatedKeys() else super(ChallengeBattleResultsFormatter, cls)._getTitle(condition)

    def _getDescription(self, condition):
        keyName = condition.keyName
        aggregatedKeys = condition.getAggregatedKeys()
        _, topRangeLower = condition.getMaxRange()
        if keyName is not None:
            if topRangeLower < TOP_RANGE_LOWEST:
                textRes = CONDITION_TEXT_RES.top.dyn(keyName)
                if condition.isTotal():
                    textRes = textRes.dyn(TextResKey.TOTAL)
                return packDescriptionField(textRes, rank=topRangeLower)
            else:
                textRes = CONDITION_TEXT_RES.dyn(keyName)
                if condition.compareWithMaxHealth:
                    textRes = textRes.dyn(TextResKey.COMPARE_WITH_MAX_HEALTH)
                return packDescriptionField(textRes, goal=getRelationValue(condition))
        elif aggregatedKeys:
            textRes = CONDITION_TEXT_RES.aggregated
            for key in self._processAggregatedKeys(aggregatedKeys):
                textRes = textRes.dyn(key)

            return packDescriptionField(textRes, goal=getRelationValue(condition))
        return super(ChallengeBattleResultsFormatter, self)._getDescription(condition)

    @classmethod
    def _getIconKey(cls, condition=None):
        keyName = condition.keyName
        _, topRangeLower = condition.getMaxRange()
        if topRangeLower < TOP_RANGE_LOWEST:
            return ConditionIcon.TOP
        elif condition.getAggregatedKeys():
            return ConditionIcon.COMPLEX
        else:
            if keyName is not None:
                iconKey = CHALLENGES_BATTLE_RESULT_ICONS.get(keyName)
                if iconKey is not None:
                    return iconKey
            return super(ChallengeBattleResultsFormatter, cls)._getIconKey(condition)

    @staticmethod
    def _processAggregatedKeys(keys):
        damageAssistedPrefix = 'damageAssisted'
        damageAssistedPrefixLen = len(damageAssistedPrefix)
        damageAssistedKey = damageAssistedPrefix
        result = []
        for key in keys:
            if key.startswith(damageAssistedPrefix):
                damageAssistedKey = damageAssistedKey + key[damageAssistedPrefixLen:]
            result.append(key)

        if damageAssistedKey != damageAssistedPrefix:
            result.append(damageAssistedKey)
        return sorted(result)


class ChallengeAchievementsFormatter(SimpleMissionsFormatter):

    @classmethod
    def _getTitle(cls, condition):
        return packTitleField(CONDITION_TEXT_RES.achievement.title)

    def _getDescription(self, condition):
        achievements = condition.getValue()
        if len(achievements) > 1:
            _logger.error('More than 1 achievement in condition: %s', achievements)
        achievementRecordID = first(achievements)
        _, achievementName = DB_ID_TO_RECORD[achievementRecordID]
        nameRes = ACHIEVEMENT_TEXT_RES.dyn(achievementName)
        if nameRes.exists():
            return packDescriptionField(CONDITION_TEXT_RES.achievement, achievement=backport.text(nameRes()))
        _logger.error('Missing localization for achievement: %s', achievementName)
        return super(ChallengeAchievementsFormatter, self)._getDescription(condition)

    @classmethod
    def _getIconKey(cls, condition=None):
        return ConditionIcon.ACHIEVEMENT

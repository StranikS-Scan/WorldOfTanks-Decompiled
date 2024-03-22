# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/data_wrapper/clan_supply.py
import logging
from typing import NamedTuple, Dict, Union, TYPE_CHECKING, List
from shared_utils import makeTupleByDict, CONST_CONTAINER
if TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

class DataNames(CONST_CONTAINER):
    PROGRESSION_SETTINGS = 'PROGRESSION_SETTINGS'
    PROGRESSION_PROGRESS = 'PROGRESSION_PROGRESS'
    QUESTS_INFO = 'QUESTS_INFO'
    QUESTS_INFO_POST = 'QUESTS_INFO_POST'


class PointStatus(CONST_CONTAINER):
    PURCHASED = 'PURCHASED'
    AVAILABLE = 'AVAILABLE'


class ConditionRuleType(CONST_CONTAINER):
    FULL_DAMAGE = 'FULL_DAMAGE'
    FRAGS = 'FRAGS'
    WIN = 'WIN'
    EXP = 'EXP'


class ConditionSquadState(CONST_CONTAINER):
    SOLO = 'solo'
    PLATOON = 'platoon'
    DETACHMENT = 'detachment'


class QuestStatus(CONST_CONTAINER):
    INCOMPLETE = 'INCOMPLETE'
    REWARD_AVAILABLE = 'REWARD_AVAILABLE'
    REWARD_PENDING = 'REWARD_PENDING'
    COMPLETE = 'COMPLETE'


PointSettings = NamedTuple('PointSettings', [('is_elite', bool), ('price', int), ('rewards', Dict[str, Union[int, str, Dict, List[Dict]]])])
ProgressionSettings = NamedTuple('ProgressionSettings', [('enabled', bool), ('points', Dict[str, PointSettings])])
PointProgress = NamedTuple('PointSettings', [('status', str)])
ProgressionProgress = NamedTuple('ProgressionProgress', [('last_purchased', str), ('points', Dict[str, PointProgress])])
FragsCondition = NamedTuple('FragsCondition', [('type', str), ('frags_count', str)])
FullDamageCondition = NamedTuple('FullDamageCondition', [('type', str), ('full_damage', str)])
ExpCondition = NamedTuple('ExpCondition', [('type', str), ('exp_earned', str)])
WinCondition = NamedTuple('WinCondition', [('type', str)])
CONDITIONS_TYPE = Union[FragsCondition, FullDamageCondition, ExpCondition, WinCondition]
SimpleCondition = NamedTuple('SimpleCondition', [('rule', CONDITIONS_TYPE), ('squad_states', List[str])])
_RULE_TYPE_TO_CLAZZ = {ConditionRuleType.FRAGS: FragsCondition,
 ConditionRuleType.WIN: WinCondition,
 ConditionRuleType.EXP: ExpCondition,
 ConditionRuleType.FULL_DAMAGE: FullDamageCondition}

def _makeSimpleCondition(conditionData):
    ruleData = conditionData.get('rule', {})
    ruleType = ruleData.get('type')
    if ruleType not in _RULE_TYPE_TO_CLAZZ:
        _logger.warning('Does not type class for the condition: %s', conditionData)
        return None
    else:
        conditionData.update({'rule': makeTupleByDict(_RULE_TYPE_TO_CLAZZ[ruleType], ruleData)})
        return makeTupleByDict(SimpleCondition, conditionData)


CommonCondition = NamedTuple('CommonCondition', [('level_from', int), ('level_to', int)])
ConditionsInfo = NamedTuple('ConditionsInfo', [('main', SimpleCondition), ('alternative', SimpleCondition), ('common', CommonCondition)])
Quest = NamedTuple('Quest', [('name', str),
 ('level', int),
 ('current_progress', int),
 ('required_progress', int),
 ('status', str),
 ('conditions', ConditionsInfo),
 ('rewards', Dict[str, Union[int, str]])])
QuestsInfo = NamedTuple('QuestsInfo', [('enabled', bool),
 ('cycle_end', int),
 ('cycle_duration', int),
 ('previous_rewards', Dict[str, Union[int, str]]),
 ('quests', List[Quest])])

def makeQuestInfo(incomeData):
    incomeData = incomeData or {}
    questInfo = []
    incomeQuestInfoData = incomeData.get('quest_info', [])
    for rawQuest in sorted(incomeQuestInfoData, key=lambda q: q.get('level')):
        rawConditionsInfo = rawQuest.get('conditions', {})
        conditionsInfo = {'main': _makeSimpleCondition(rawConditionsInfo.get('main', {})),
         'alternative': _makeSimpleCondition(rawConditionsInfo.get('alternative', {})),
         'common': makeTupleByDict(CommonCondition, rawConditionsInfo.get('common', {}))}
        rawQuest.update({'conditions': makeTupleByDict(ConditionsInfo, conditionsInfo)})
        questInfo.append(makeTupleByDict(Quest, rawQuest))

    incomeData.update({'quests': questInfo})
    incomeData.update({'enabled': True})
    return makeTupleByDict(QuestsInfo, incomeData)

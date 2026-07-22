# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/score_system/rules/__init__.py
import typing
from events_core_common.score_system.rules.base_score_rule import BaseScoreRule
from events_core_common.score_system.rules.cumulative_score_rule import CumulativeScoreRule
from events_core_common.score_system.rules.regular_score_rule import RegularScoreRule
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict, Type, Optional

class ScoreRuleClasses(object):

    def __init__(self, mapping=None):
        if mapping is None:
            mapping = self.__getDefaultMapping()
        self._mapping = mapping
        return

    def __getitem__(self, ruleID):
        return self._mapping[ruleID]

    def getScoreRule(self, ruleID):
        return self._mapping.get(ruleID)

    def addScoreRule(self, ruleCls):
        if not issubclass(ruleCls, BaseScoreRule):
            raise SoftException('ScoreRule class must be a subclass of BaseScoreRule')
        self._mapping[ruleCls.RULE_ID] = ruleCls

    @staticmethod
    def __getDefaultMapping():
        return {RegularScoreRule.RULE_ID: RegularScoreRule,
         CumulativeScoreRule.RULE_ID: CumulativeScoreRule}

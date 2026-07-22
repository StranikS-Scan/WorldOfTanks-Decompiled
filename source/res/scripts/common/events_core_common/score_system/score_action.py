# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/score_system/score_action.py
import typing
from debug_utils import LOG_NOTE
if typing.TYPE_CHECKING:
    from events_core_common.score_system.rules import ScoreRuleClasses
    from typing import Dict

class ScoreAction(object):

    def __init__(self, actionID, rulesConfig, scoreRules):
        self.actionID = actionID
        self.rules = {}
        self.__scoreRules = scoreRules
        self.__initRules(rulesConfig)

    def __initRules(self, rulesConfig):
        for ruleName, ruleConfig in rulesConfig.iteritems():
            LOG_NOTE('Registering rule:', ruleName, self.actionID)
            self.rules[ruleName] = self.__scoreRules[ruleName](ruleConfig)

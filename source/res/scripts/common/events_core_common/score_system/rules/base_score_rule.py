# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/score_system/rules/base_score_rule.py
import typing
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Dict

class BaseScoreRule(object):
    RULE_ID = None

    def __init__(self, config):
        self.score = 0
        self.weight = 0
        self._initFromConfig(config)

    def _initFromConfig(self, config):
        score = config.get('score')
        weight = config.get('weight')
        if score is None or weight is None:
            raise SoftException('[base_score_rule] sections <score> and <weight> are missing')
        self.score = score
        self.weight = weight
        return

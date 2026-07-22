# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/score_system/config_readers/__init__.py
from soft_exception import SoftException

def readRuleSection(ruleSection):
    ruleConfig = {}
    for paramSection in ruleSection.values():
        ruleConfig[paramSection.name] = paramSection.asInt

    return ruleConfig


def readScoreSystemSection(scoreSystemSection):
    if 'actions' not in scoreSystemSection.keys():
        raise SoftException('Score system section missing actions')
    actionsDict = {}
    for actionSection in scoreSystemSection['actions'].values():
        actionID = actionSection.name
        rulesDict = {}
        for ruleSection in actionSection.values():
            rulesDict[ruleSection.name] = readRuleSection(ruleSection)

        actionsDict[actionID] = rulesDict

    return actionsDict

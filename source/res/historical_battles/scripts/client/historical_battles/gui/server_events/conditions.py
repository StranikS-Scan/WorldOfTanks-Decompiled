# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/conditions.py
from gui.server_events.conditions import _ConditionsGroup as ConditionsGroup

def getTokenNeededCountInCondition(quest, tokenName, default=None):
    return default if quest is None else _getTokenNeededCountInCondition(quest.accountReqs.getConditions().items, tokenName, default)


def _getTokenNeededCountInCondition(items, tokenName, default=None):
    item = _getTokenItemInCondition(items, tokenName)
    return default if item is None else item.getNeededCount()


def getTokenReceivedCountInCondition(quest, tokenName, default=None):
    return default if quest is None else _getTokenReceivedCountInCondition(quest.accountReqs.getConditions().items, tokenName, default)


def _getTokenReceivedCountInCondition(items, tokenName, default=None):
    item = _getTokenItemInCondition(items, tokenName)
    return default if item is None else item.getReceivedCount()


def _getTokenItemInCondition(items, tokenName):
    res = None
    for item in items:
        if isinstance(item, ConditionsGroup):
            res = _getTokenItemInCondition(item.items, tokenName)
        if item.getName() == 'token' and item.getID() == tokenName:
            return item

    return res

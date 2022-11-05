# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier/modifier_helpers.py
from typing import Optional, Callable, Union, Dict
from battle_modifiers_ext.constants_ext import UseType

def makeUseTypeMethods(method, copy=False):
    if isinstance(method, dict):
        if copy:
            return method.copy()
        return method
    return dict(((useType, method) for useType in UseType.ALL))


def createLevelTag(level):
    return 'level_' + str(level)


def parseLevelTag(levelTag):
    parts = levelTag.split('_', 1)
    if not (len(parts) == 2 and parts[0] == 'level'):
        return
    else:
        try:
            level = int(parts[1])
        except ValueError:
            level = None

        return level

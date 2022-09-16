# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier_helpers.py
from typing import Callable, Union, Dict
from battle_modifier_constants import UseType

def makeUseTypeMethods(method, copy=False):
    if isinstance(method, dict):
        if copy:
            return method.copy()
        return method
    return dict(((useType, method) for useType in UseType.ALL))

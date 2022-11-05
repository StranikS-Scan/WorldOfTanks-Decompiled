# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/remapping/remapping_composers.py
from typing import TYPE_CHECKING, Optional, Any, Dict, List, FrozenSet
from battle_modifiers_ext.constants_ext import ModifiersWithRemapping
if TYPE_CHECKING:
    from battle_modifiers_common import ModifiersContext
    from battle_modifiers_ext.remapping.remapping_conditions import IRemappingCondition
_START_PATTERN = '{'
_END_PATTERN = '}'

class IComposer(object):
    __slots__ = ()

    def __call__(self, ctx, oldValue):
        raise NotImplementedError


class _BaseComposer(IComposer):
    __slots__ = ('_conditions', '_targetTemplate', '_specialRules')

    def __init__(self, conditions, targetTemplate, specialRules):
        self._conditions = conditions
        self._targetTemplate = targetTemplate
        self._specialRules = specialRules

    def __call__(self, ctx, oldValue):
        resStr = self.__applySpecialRules(ctx, oldValue)
        if resStr is not None:
            return resStr
        else:
            resStr = self._targetTemplate
            for condition in self._conditions:
                part = condition(ctx)
                if part is None:
                    continue
                resStr = resStr.replace(''.join((_START_PATTERN, condition.getName(), _END_PATTERN)), part)

            return resStr

    @classmethod
    def _getItemName(cls, ctx, oldValue):
        pass

    def __applySpecialRules(self, ctx, oldValue):
        if not self._specialRules:
            return None
        else:
            itemName = self._getItemName(ctx, oldValue)
            for sources, target in self._specialRules.iteritems():
                if itemName in sources:
                    return target

            return None


class _DefaultGunEffectsComposer(_BaseComposer):

    @classmethod
    def _getItemName(cls, _, oldValue):
        from items import vehicles
        for k, v in vehicles.g_cache.gunEffects.iteritems():
            if v == oldValue:
                return k

        return None


class _DefaultShotEffectsComposer(_BaseComposer):

    @classmethod
    def _getItemName(cls, _, oldValue):
        from items import vehicles
        return vehicles.g_cache.shotEffectsNames[oldValue]


_DEFAULT_COMPOSERS = {ModifiersWithRemapping.GUN_EFFECTS: _DefaultGunEffectsComposer,
 ModifiersWithRemapping.SHOT_EFFECTS: _DefaultShotEffectsComposer}
_COMPOSERS_FACTORY = {}

def getComposerClass(remappingName, modifierName):
    return _COMPOSERS_FACTORY.get(remappingName, _DEFAULT_COMPOSERS).get(modifierName)

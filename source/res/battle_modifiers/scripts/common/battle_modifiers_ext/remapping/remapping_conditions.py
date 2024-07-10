# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/remapping/remapping_conditions.py
from typing import Dict, FrozenSet, TYPE_CHECKING
from battle_modifiers_ext.constants_ext import ShellCaliber, ShellKind, RemappingConditionNames
from nations import NAMES
if TYPE_CHECKING:
    from battle_modifiers_common import ModifiersContext

class IRemappingCondition(object):
    __slots__ = ()

    @classmethod
    def getName(cls):
        raise NotImplementedError

    def __call__(self, ctx):
        raise NotImplementedError


class _BaseCondition(IRemappingCondition):
    __slots__ = ('_remappingName', '_remapping')
    _CONDITION_NAME = 'baseCondition'

    def __init__(self, remappingName, remapping):
        self._remappingName = remappingName
        self._remapping = remapping

    def __call__(self, ctx):
        currentParam = self._getParam(ctx)
        if not self._remapping:
            return currentParam
        for sources, target in self._remapping.iteritems():
            if currentParam in sources:
                return target

    @classmethod
    def getName(cls):
        return cls._CONDITION_NAME

    def _getParam(self, ctx):
        raise NotImplementedError


class _RemappingNameCondition(_BaseCondition):
    __slots__ = ()
    _CONDITION_NAME = RemappingConditionNames.REMAPPING_NAME

    def _getParam(self, ctx):
        return self._remappingName


class _NationCondition(_BaseCondition):
    __slots__ = ()
    _CONDITION_NAME = RemappingConditionNames.NATION

    def _getParam(self, ctx):
        return NAMES[ctx.modificationCtx['vehType'].id[0]]


class _OutfitCondition(_BaseCondition):
    __slots__ = ()
    _CONDITION_NAME = RemappingConditionNames.OUTFIT

    def _getParam(self, ctx):
        outfit = ctx.modificationCtx['outfit']
        return outfit if outfit != 'default' else ''


class _CaliberCondition(_BaseCondition):
    __slots__ = ()
    _CONDITION_NAME = RemappingConditionNames.CALIBER

    def _getParam(self, ctx):
        return ShellCaliber.get(ctx.modificationCtx['gun'].shots[0].shell.caliber)


class _GunNameCondition(_BaseCondition):
    __slots__ = ()
    _CONDITION_NAME = RemappingConditionNames.GUN_NAME

    def _getParam(self, ctx):
        return ctx.modificationCtx['gun'].name


class _ShellKindCondition(_BaseCondition):
    __slots__ = ()
    _CONDITION_NAME = RemappingConditionNames.SHELL_KIND

    def _getParam(self, ctx):
        return ShellKind.get(ctx.modificationCtx['shell'], withGold=False)


class _ShellShotsCountCondition(_BaseCondition):
    __slots__ = ()
    _CONDITION_NAME = RemappingConditionNames.SHELL_SHOTS_COUNT

    def _getParam(self, ctx):
        return str(ctx.modificationCtx['shotsCount'])


_CONDITIONS_FACTORY = {RemappingConditionNames.REMAPPING_NAME: _RemappingNameCondition,
 RemappingConditionNames.NATION: _NationCondition,
 RemappingConditionNames.OUTFIT: _OutfitCondition,
 RemappingConditionNames.CALIBER: _CaliberCondition,
 RemappingConditionNames.GUN_NAME: _GunNameCondition,
 RemappingConditionNames.SHELL_KIND: _ShellKindCondition,
 RemappingConditionNames.SHELL_SHOTS_COUNT: _ShellShotsCountCondition}

def getConditionClass(conditionName):
    return _CONDITIONS_FACTORY.get(conditionName)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/remapping/remapping_conditions.py
from typing import Any, Dict, FrozenSet, TYPE_CHECKING
from battle_modifiers_ext.constants_ext import ShellCaliber, ShellKind, RemappingConditionNames
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
    __slots__ = ('_remapping',)

    def __init__(self, remapping):
        self._remapping = remapping

    def __call__(self, ctx):
        currentParam = self._getParam(ctx)
        for sources, target in self._remapping.iteritems():
            if currentParam in sources:
                return target

        return None

    def _getParam(self, ctx):
        raise NotImplementedError


class _CaliberCondition(_BaseCondition):
    __slots__ = ()

    @classmethod
    def getName(cls):
        return RemappingConditionNames.CALIBER

    def _getParam(self, ctx):
        return ShellCaliber.get(ctx.gun.shots[0].shell.caliber)


class _ShellKindCondition(_BaseCondition):
    __slots__ = ()

    @classmethod
    def getName(cls):
        return RemappingConditionNames.SHELL_KIND

    def _getParam(self, ctx):
        return ShellKind.get(ctx.shell, withGold=False)


_CONDITIONS_FACTORY = {RemappingConditionNames.CALIBER: _CaliberCondition,
 RemappingConditionNames.SHELL_KIND: _ShellKindCondition}

def getConditionClass(conditionName):
    return _CONDITIONS_FACTORY.get(conditionName)

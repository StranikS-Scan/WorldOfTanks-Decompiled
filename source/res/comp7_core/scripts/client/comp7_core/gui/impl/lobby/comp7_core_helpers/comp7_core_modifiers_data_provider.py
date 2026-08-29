# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/comp7_core_helpers/comp7_core_modifiers_data_provider.py
from __future__ import absolute_import
from typing import Tuple, Any, List
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from battle_modifiers_ext.constants_ext import GameplayImpact

class Comp7CoreModifiersDataProvider(ModifiersDataProvider):
    __slots__ = ('_domain',)

    def __init__(self, domain, modifiers=()):
        self._domain = domain
        super(Comp7CoreModifiersDataProvider, self).__init__(modifiers)

    @classmethod
    def isHiddenModifier(cls, mod):
        return mod.gameplayImpact == GameplayImpact.HIDDEN

    def _readClientDomain(self, modifier):
        return self._domain


class Comp7CoreSubModifiers(object):
    __slots__ = ('__subModesProviders',)

    def __init__(self, subModifiers=()):
        self.__subModesProviders = [ Comp7CoreModifiersDataProvider(name, modifiers) for name, modifiers in subModifiers ]

    @property
    def providers(self):
        return self.__subModesProviders

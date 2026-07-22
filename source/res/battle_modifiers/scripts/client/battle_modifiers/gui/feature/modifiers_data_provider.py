# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/client/battle_modifiers/gui/feature/modifiers_data_provider.py
from typing import Tuple, Any, TYPE_CHECKING
from battle_modifiers_ext.battle_modifiers import BattleModifiers
from battle_modifiers_ext.constants_ext import GameplayImpact
if TYPE_CHECKING:
    from battle_modifiers_ext.battle_modifiers import BattleModifier

class ModifiersDataProvider(object):
    __slots__ = ('__modifiers', '__domains', '__modifiersByDomain')

    def __init__(self, battleModifiersDescr=()):
        self.__modifiers = BattleModifiers(battleModifiersDescr)
        domains = tuple((self._readClientDomain(modifier) for _, modifier in self.__modifiers if not self.isHiddenModifier(modifier)))
        self.__domains = tuple((domain for i, domain in enumerate(domains) if domain not in domains[:i]))
        self.__modifiersByDomain = {domain:tuple((modifier for _, modifier in self.__modifiers if not self.isHiddenModifier(modifier) and self._readClientDomain(modifier) == domain)) for domain in self.__domains}

    @classmethod
    def isHiddenModifier(cls, mod):
        return mod.gameplayImpact == GameplayImpact.HIDDEN or mod.useType not in mod.param.clientData.useTypes

    def getDomains(self):
        return self.__domains

    def getDomainModifiers(self, domain):
        return self.__modifiersByDomain.get(domain, ())

    def getModifiers(self):
        return self.__modifiers

    def _readClientDomain(self, modifier):
        return str(modifier.param.clientData.domain)

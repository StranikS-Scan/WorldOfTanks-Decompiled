# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_modifiers/modifiers_data_provider.py
from typing import Tuple, Any, TYPE_CHECKING
from battle_modifiers.battle_modifiers import BattleModifiers
from battle_modifiers.battle_modifier_constants import GameplayImpact
if TYPE_CHECKING:
    from battle_modifiers.battle_modifiers import BattleModifier

class ModifiersDataProvider(object):
    __slots__ = ('__modifiers', '__domains', '__modifiersByDomain')

    def __init__(self, battleModifiersDescr=()):
        self.__modifiers = BattleModifiers(battleModifiersDescr)
        domains = tuple((str(modifier.param.clientData.domain) for _, modifier in self.__modifiers if not self.isHiddenModifier(modifier)))
        self.__domains = tuple((domain for i, domain in enumerate(domains) if domain not in domains[:i]))
        self.__modifiersByDomain = {domain:tuple((modifier for _, modifier in self.__modifiers if not self.isHiddenModifier(modifier) and modifier.param.clientData.domain == domain)) for domain in self.__domains}

    @classmethod
    def isHiddenModifier(cls, mod):
        return mod.gameplayImpact == GameplayImpact.HIDDEN or mod.useType not in mod.param.clientData.useTypes

    def getDomains(self):
        return self.__domains

    def getDomainModifiers(self, domain):
        return self.__modifiersByDomain.get(domain, ())

    def getModifiers(self):
        return self.__modifiers

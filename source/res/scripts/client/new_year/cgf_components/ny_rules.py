# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/cgf_components/ny_rules.py
import CGF
from cgf_script.managers_registrator import registerRule, registerManager, Rule
from new_year.cgf_components.lobby_customization_components import LobbyCustomizableObjectsManager

@registerRule
class NyHangarRule(Rule):
    category = 'New year rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(LobbyCustomizableObjectsManager)
    def reg1(self):
        return None

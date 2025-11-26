# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hangar_rules.py
import CGF
from cgf_script.managers_registrator import Rule, registerManager, registerRule
from gui.pet_system.cgf_components.pet_place_component import PetPrefabManager
from hover_component import HoverManager
from highlight_component import HighlightManager
from hover_group_components import HoverGroupManager
from on_click_components import ClickManager

@registerRule
class SelectionRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(HoverManager)
    def reg1(self):
        return None

    @registerManager(HighlightManager)
    def reg2(self):
        return None

    @registerManager(ClickManager)
    def reg3(self):
        return None

    @registerManager(HoverGroupManager)
    def reg4(self):
        return None


@registerRule
class PetPlaceRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(PetPrefabManager)
    def reg1(self):
        return None

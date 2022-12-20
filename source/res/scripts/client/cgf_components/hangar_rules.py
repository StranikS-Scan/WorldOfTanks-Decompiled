# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hangar_rules.py
from cgf_script.managers_registrator import registerManager, Rule
from hover_component import HoverManager
from highlight_component import HighlightManager
from on_click_components import ClickManager

class SelectionRule(Rule):
    category = 'Hangar rules'

    @registerManager(HoverManager)
    def reg1(self):
        return None

    @registerManager(HighlightManager)
    def reg2(self):
        return None

    @registerManager(ClickManager)
    def reg3(self):
        return None

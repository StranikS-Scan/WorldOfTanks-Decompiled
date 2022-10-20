# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/cgf_components/hangar_rules.py
from cgf_script.managers_registrator import registerManager, Rule
from halloween.cgf_components.show_view import ClickToOpenViewManager

class ClickToOpenViewRule(Rule):
    category = 'halloween'
    editorTitle = 'Click to open view rule'

    @registerManager(ClickToOpenViewManager)
    def reg1(self):
        return None

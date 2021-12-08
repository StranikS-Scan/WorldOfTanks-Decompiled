# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/cgf_components/registrars.py
from cgf_script.managers_registrator import registerManager, Rule
from new_year.cgf_components.other_entity_manager import OtherEntityManager

class OtherEntityCreatorRule(Rule):
    category = 'Hangar rules'

    @registerManager(OtherEntityManager)
    def reg1(self):
        return None

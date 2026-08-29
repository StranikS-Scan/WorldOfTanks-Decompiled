# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/cgf/museum_rules.py
import CGF
from cgf_script.managers_registrator import registerRule, registerManager, Rule
from museum_of_glory.cgf.museum_entry_manager import MuseumEntryManager

@registerRule
class MuseumHangarRule(Rule):
    category = 'Museum of Glory rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(MuseumEntryManager)
    def reg1(self):
        return None

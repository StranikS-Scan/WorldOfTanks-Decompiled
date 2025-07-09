# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/cgf/birthday_rules.py
import CGF
from cgf_script.managers_registrator import registerRule, registerManager, Rule
from mt_birthday.cgf.birthday_components import BirthdayClickManager, BirthdayTooltipManager

@registerRule
class BirthdayHangarRule(Rule):
    category = 'Birthday rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(BirthdayClickManager)
    def reg1(self):
        return None

    @registerManager(BirthdayTooltipManager)
    def reg2(self):
        return None

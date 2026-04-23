# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common_cgf/rules/manager_rules.py
import CGF
from cgf_script.managers_registrator import Rule, registerRule, ManagerRegistrator
from historical_battles_common_cgf.rules import manager_register

class _HistoricalBattlesRule(Rule):
    category = 'HistoricalBattles'
    domain = None

    def __init__(self):
        for name, (manager, domain) in manager_register.historicalBattlesManagers().iteritems():
            if not self.domain & domain:
                continue
            managerRegistrator = ManagerRegistrator(self.__getWrapper(manager))
            setattr(self.__class__, name, managerRegistrator)

        super(_HistoricalBattlesRule, self).__init__()

    def __getWrapper(self, manager):

        def wrapperSelf(self):
            CGF.createManager(manager, None, self.spaceID)
            return

        return wrapperSelf


@registerRule
class HistoricalBattlesServerManagerRule(_HistoricalBattlesRule):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor


@registerRule
class HistoricalBattlesClientManagerRule(_HistoricalBattlesRule):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

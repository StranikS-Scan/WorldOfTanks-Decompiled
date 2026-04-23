# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common_cgf/rules/manager_register.py
import CGF
_historicalBattlesManagers = {}

def registerHistoricalBattlesManager(domain):

    def registrator(cls):
        CGF.registerManager(cls, False, domain)
        _historicalBattlesManagers[cls.__name__] = (cls, domain)
        return cls

    return registrator


def historicalBattlesManagers():
    return _historicalBattlesManagers

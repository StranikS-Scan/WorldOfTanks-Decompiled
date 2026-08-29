# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/common_cgf/cgf_helpers.py
import CGF
from cgf_script.managers_registrator import Rule, registerRule, ManagerRegistrator
_wtCGFManagers = {}

def registerWTManager(domain):

    def registrator(cls):
        if cls.__name__ not in _wtCGFManagers:
            CGF.registerManager(cls, False, domain)
            _wtCGFManagers[cls.__name__] = (cls, domain)
        return cls

    return registrator


class _WTRule(Rule):
    category = 'White Tiger'
    domain = None

    def __init__(self):
        for name, (manager, domain) in _wtCGFManagers.iteritems():
            if not self.domain & domain:
                continue
            managerRegistrator = ManagerRegistrator(self.__getWrapper(manager))
            setattr(self.__class__, name, managerRegistrator)

        super(_WTRule, self).__init__()

    def __getWrapper(self, manager):

        def wrapperSelf(self):
            CGF.createManager(manager, None, self.spaceID)
            return

        return wrapperSelf


@registerRule
class WTServerManagerRule(_WTRule):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor


@registerRule
class WTClientManagerRule(_WTRule):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common_cgf/portal_rules.py
import CGF
from cgf_script.managers_registrator import Rule, registerRule, ManagerRegistrator
from portal_common_cgf import portal_helpers

class _PortalRule(Rule):
    category = 'Portal'
    domain = None

    def __init__(self):
        for name, (manager, domain) in portal_helpers.portalManagers().iteritems():
            if not self.domain & domain:
                continue
            managerRegistrator = ManagerRegistrator(self.__getWrapper(manager))
            setattr(self.__class__, name, managerRegistrator)

        super(_PortalRule, self).__init__()

    def __getWrapper(self, manager):

        def wrapperSelf(self):
            CGF.createManager(manager, None, self.spaceID)
            return

        return wrapperSelf


@registerRule
class PortalServerManagerRule(_PortalRule):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor


@registerRule
class PortalClientManagerRule(_PortalRule):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common_cgf/rules.py
import CGF
from cgf_script.managers_registrator import Rule, registerRule, ManagerRegistrator
from cosmic_event_common_cgf import helpers

class _CosmicEventRule(Rule):
    category = 'Cosmic'
    domain = None

    def __init__(self):
        for name, (manager, domain) in helpers.cosmicEventManagers().iteritems():
            if not self.domain & domain:
                continue
            managerRegistrator = ManagerRegistrator(self.__getWrapper(manager))
            setattr(self.__class__, name, managerRegistrator)

        super(_CosmicEventRule, self).__init__()

    def __getWrapper(self, manager):

        def wrapperSelf(self):
            CGF.createManager(manager, None, self.spaceID)
            return

        return wrapperSelf


@registerRule
class CosmicEventServerManagerRule(_CosmicEventRule):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor


@registerRule
class CosmicEventClientManagerRule(_CosmicEventRule):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

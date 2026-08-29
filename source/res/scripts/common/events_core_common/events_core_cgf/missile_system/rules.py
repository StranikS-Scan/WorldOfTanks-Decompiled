# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/events_core_cgf/missile_system/rules.py
import CGF
from cgf_script.managers_registrator import Rule, registerRule, ManagerRegistrator
from events_core_common.events_core_cgf.missile_system import helpers

class _EventsCoreMissileRule(Rule):
    category = 'White Tiger'
    domain = None

    def __init__(self):
        for name, (manager, domain) in helpers.EventsCoreMissileManagers().iteritems():
            if not self.domain & domain:
                continue
            managerRegistrator = ManagerRegistrator(self.__getWrapper(manager))
            setattr(self.__class__, name, managerRegistrator)

        super(_EventsCoreMissileRule, self).__init__()

    def __getWrapper(self, manager):

        def wrapperSelf(self):
            CGF.createManager(manager, None, self.spaceID)
            return

        return wrapperSelf


@registerRule
class MissileServerManagerRule(_EventsCoreMissileRule):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor


@registerRule
class MissileClientManagerRule(_EventsCoreMissileRule):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

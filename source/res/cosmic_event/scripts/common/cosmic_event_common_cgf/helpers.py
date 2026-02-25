# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/common/cosmic_event_common_cgf/helpers.py
import CGF
_cosmicEventManagers = {}

def registerCosmicEventManager(domain):

    def registrator(cls):
        if cls.__name__ not in _cosmicEventManagers:
            CGF.registerManager(cls, False, domain)
            _cosmicEventManagers[cls.__name__] = (cls, domain)
        return cls

    return registrator


def cosmicEventManagers():
    return _cosmicEventManagers

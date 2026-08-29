# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/events_core_common/events_core_cgf/missile_system/helpers.py
import CGF
from GenericComponents import TransformComponent
from constants import IS_EDITOR
if IS_EDITOR:

    class MissileComponent(object):
        pass


else:
    from MissileComponent import MissileComponent
MISSILE_COMPONENTS = (CGF.GameObject, MissileComponent, TransformComponent)
_EventsCoreMissileManagers = {}

def registerMissileManager(domain):

    def registrator(cls):
        if cls.__name__ not in _EventsCoreMissileManagers:
            CGF.registerManager(cls, False, domain)
            _EventsCoreMissileManagers[cls.__name__] = (cls, domain)
        return cls

    return registrator


def EventsCoreMissileManagers():
    return _EventsCoreMissileManagers

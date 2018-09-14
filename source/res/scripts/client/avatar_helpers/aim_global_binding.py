# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_helpers/aim_global_binding.py
"""
Module provides access to global descriptors when player is avatar. Global descriptors are read by
multiple packages in a battle. Only AvatarInputHandler package changes values of global descriptors.

Global descriptors are: aim offset, current avatar control mode, etc.

NOTE: This module must be in AvatarInputHandler package. Unfortunately, if this module will be moved to
desired package, we have "cross import" between AvatarInputHandler and gui.battle_control.
AvatarInputHandler package must be refactored to avoid "cross import".

Usage:
    1. Adds binding to global descriptor:

        class SomeClass(object):
            aimOffset = aim_global_binding.bind(BINDING_ID.AIM_OFFSET)

    2. Adds subscriber to start listening descriptor change:

        def on_aim_offset_changed(value):
            ....

        aim_global_binding.subscribe(BINDING_ID.AIM_OFFSET, on_aim_offset_changed)

    3. Removes subscriber to stop listening descriptor change:

        aim_global_binding.unsubscribe(BINDING_ID.AIM_OFFSET, on_aim_offset_changed)
"""
import Math
_FLOAT_EPSILON = 0.001

class BINDING_ID(object):
    CTRL_MODE_NAME = 1
    AIM_OFFSET = 2
    ZOOM_FACTOR = 3
    GUN_MARKER_POSITION = 4
    RANGE = (CTRL_MODE_NAME,
     AIM_OFFSET,
     ZOOM_FACTOR,
     GUN_MARKER_POSITION)


class CTRL_MODE_NAME(object):
    ARCADE = 'arcade'
    STRATEGIC = 'strategic'
    SNIPER = 'sniper'
    POSTMORTEM = 'postmortem'
    DEBUG = 'debug'
    CAT = 'cat'
    VIDEO = 'video'
    MAP_CASE = 'mapcase'
    FALLOUT_DEATH = 'falloutdeath'
    DEFAULT = ARCADE


class _Observable(object):
    """Class contains some value and notifies its subscribes if own value is changed."""

    def __init__(self, value):
        super(_Observable, self).__init__()
        self.value = value
        self.subscribers = []

    def clear(self):
        """Removes all subscribers"""
        del self.subscribers[:]

    def subscribe(self, subscriber):
        """Adds subscriber that wants listening changing value.
        :param subscriber: callable object.
        """
        assert subscriber not in self.subscribers
        self.subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        """Removes subscriber.
        :param subscriber: callable object.
        """
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def change(self, other):
        if self.value != other:
            self.value = other
            self._notify()
            return True
        else:
            return False

    def _notify(self):
        for subscriber in self.subscribers:
            subscriber(self.value)


class _ObservableVector2(_Observable):

    def __init__(self):
        super(_ObservableVector2, self).__init__(Math.Vector2(0.0, 0.0))

    def change(self, other):
        if abs(other.x - self.value.x) > _FLOAT_EPSILON or abs(other.y - self.value.y) > _FLOAT_EPSILON:
            self.value = other
            self._notify()
            return True
        else:
            return False


_DEFAULT_VALUES = {BINDING_ID.CTRL_MODE_NAME: lambda : _Observable(CTRL_MODE_NAME.DEFAULT),
 BINDING_ID.AIM_OFFSET: lambda : _ObservableVector2(),
 BINDING_ID.ZOOM_FACTOR: lambda : _Observable(0.0),
 BINDING_ID.GUN_MARKER_POSITION: lambda : _Observable((Math.Vector3(0.0, 0.0, 0.0), 0.0))}

class _GlobalDataDescriptor(object):
    __slots__ = ('__bindingID',)
    __storage = {}

    def __init__(self, bindingID):
        super(_GlobalDataDescriptor, self).__init__()
        assert bindingID in BINDING_ID.RANGE
        self.__bindingID = bindingID
        if bindingID not in self.__storage:
            self.__storage[bindingID] = _DEFAULT_VALUES[bindingID]()

    def __set__(self, _, value):
        self.__storage[self.__bindingID].change(value)

    def __get__(self, instance, _=None):
        return self.__storage[self.__bindingID] if instance is None else self.__storage[self.__bindingID].value

    @classmethod
    def clear(cls):
        """Clears data"""
        for bindingID, observable in cls.__storage.iteritems():
            observable.clear()
            observable.change(_DEFAULT_VALUES[bindingID]().value)

    @classmethod
    def subscribe(cls, bindingID, subscriber):
        """Adds subscriber that wants listening changing value.
        :param bindingID: one of GLOBAL_BINDING_ID.
        :param subscriber: callable object.
        """
        assert bindingID in cls.__storage, 'The bindingID {} is not found in the storage'.format(bindingID)
        cls.__storage[bindingID].subscribe(subscriber)

    @classmethod
    def unsubscribe(cls, bindingID, subscriber):
        """Removes subscriber.
        :param bindingID: one of GLOBAL_BINDING_ID.
        :param subscriber: callable object.
        """
        assert bindingID in cls.__storage, 'The bindingID {} is not found in the storage'.format(bindingID)
        cls.__storage[bindingID].unsubscribe(subscriber)


def bind(bindingID):
    return _GlobalDataDescriptor(bindingID)


def subscribe(bindingID, observer):
    _GlobalDataDescriptor.subscribe(bindingID, observer)


def unsubscribe(bindingID, observer):
    _GlobalDataDescriptor.unsubscribe(bindingID, observer)


def clear():
    """Clears data"""
    _GlobalDataDescriptor.clear()

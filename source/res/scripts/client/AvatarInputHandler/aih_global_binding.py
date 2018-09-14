# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/aih_global_binding.py
"""
Module provides access to global descriptors when player is avatar. Global descriptors are read by
multiple packages in a battle. Only AvatarInputHandler package changes values of global descriptors.

Global descriptors are: aim offset, current avatar control mode, etc.

Usage:
    1. Adds binding of global descriptor to read its value:

        class SomeClass(object):
            aimOffset = aih_global_binding.bindRO(BINDING_ID.AIM_OFFSET)

    2. DO NOT use aih_global_binding.bindRW in other places outside package AvatarInputHandler.

    3. Adds subscriber to start listening descriptor change:

        def on_aim_offset_changed(value):
            ....

        aih_global_binding.subscribe(BINDING_ID.AIM_OFFSET, on_aim_offset_changed)

    4. Removes subscriber to stop listening descriptor change:

        aih_global_binding.unsubscribe(BINDING_ID.AIM_OFFSET, on_aim_offset_changed)
"""
import Math
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME, GUN_MARKER_FLAG
_FLOAT_EPSILON = 0.002

class BINDING_ID(object):
    CTRL_MODE_NAME = 1
    AIM_OFFSET = 2
    ZOOM_FACTOR = 3
    GUN_MARKERS_FLAGS = 4
    CLIENT_GUN_MARKER_STATE = 5
    SERVER_GUN_MARKER_STATE = 6
    CLIENT_GUN_MARKER_DATA_PROVIDER = 7
    CLIENT_SPG_GUN_MARKER_DATA_PROVIDER = 8
    SERVER_GUN_MARKER_DATA_PROVIDER = 9
    SERVER_SPG_GUN_MARKER_DATA_PROVIDER = 10
    RANGE = (CTRL_MODE_NAME,
     AIM_OFFSET,
     ZOOM_FACTOR,
     GUN_MARKERS_FLAGS,
     CLIENT_GUN_MARKER_STATE,
     SERVER_GUN_MARKER_STATE,
     CLIENT_GUN_MARKER_DATA_PROVIDER,
     CLIENT_SPG_GUN_MARKER_DATA_PROVIDER,
     SERVER_GUN_MARKER_DATA_PROVIDER,
     SERVER_SPG_GUN_MARKER_DATA_PROVIDER)


class _Observable(object):
    """Class contains some value and notifies its subscribes if own value is changed."""

    def __init__(self, value):
        super(_Observable, self).__init__()
        self.value = value
        self.__subscribers = []

    def clear(self):
        """Clears data."""
        del self.__subscribers[:]

    def subscribe(self, subscriber):
        """Adds subscriber that wants listening changing value.
        :param subscriber: callable object.
        """
        assert subscriber not in self.__subscribers
        self.__subscribers.append(subscriber)

    def unsubscribe(self, subscriber):
        """Removes subscriber.
        :param subscriber: callable object.
        """
        if subscriber in self.__subscribers:
            self.__subscribers.remove(subscriber)

    def change(self, other):
        if self._isChanged(other):
            self.value = other
            for subscriber in self.__subscribers:
                subscriber(self.value)

            return True
        else:
            return False

    def _isChanged(self, other):
        return self.value != other


class _ObservableVector2(_Observable):

    def __init__(self):
        super(_ObservableVector2, self).__init__(Math.Vector2(0.0, 0.0))

    def _isChanged(self, other):
        return abs(other.x - self.value.x) > _FLOAT_EPSILON or abs(other.y - self.value.y) > _FLOAT_EPSILON


_DEFAULT_VALUES = {BINDING_ID.CTRL_MODE_NAME: lambda : _Observable(CTRL_MODE_NAME.DEFAULT),
 BINDING_ID.AIM_OFFSET: lambda : _ObservableVector2(),
 BINDING_ID.ZOOM_FACTOR: lambda : _Observable(0.0),
 BINDING_ID.GUN_MARKERS_FLAGS: lambda : _Observable(GUN_MARKER_FLAG.UNDEFINED),
 BINDING_ID.CLIENT_GUN_MARKER_STATE: lambda : _Observable((Math.Vector3(0.0, 0.0, 0.0), 0.0, None)),
 BINDING_ID.SERVER_GUN_MARKER_STATE: lambda : _Observable((Math.Vector3(0.0, 0.0, 0.0), 0.0, None)),
 BINDING_ID.CLIENT_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.CLIENT_SPG_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.SERVER_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.SERVER_SPG_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None)}

class _GlobalDataDescriptor(object):
    __slots__ = ('__bindingID', '__reader', '__writer')
    __storage = {}

    def __init__(self, bindingID, reader=False, writer=False):
        super(_GlobalDataDescriptor, self).__init__()
        assert bindingID in BINDING_ID.RANGE
        self.__bindingID = bindingID
        self.__reader = reader
        self.__writer = writer
        if bindingID not in self.__storage:
            self.__storage[bindingID] = _DEFAULT_VALUES[bindingID]()

    def __set__(self, instance, value):
        if not self.__writer:
            raise AttributeError('{} can not set value of descriptor'.format(instance))
        self.__storage[self.__bindingID].change(value)

    def __get__(self, instance, _=None):
        if not self.__reader:
            raise AttributeError('{} can not get value of descriptor'.format(instance))
        return self.__storage[self.__bindingID] if instance is None else self.__storage[self.__bindingID].value

    @classmethod
    def clear(cls):
        """Clears data"""
        for bindingID, observable in cls.__storage.iteritems():
            observable.clear()
            observable.change(_DEFAULT_VALUES[bindingID]().value)

    @classmethod
    def subscribe(cls, bindingID, subscriber):
        assert bindingID in cls.__storage, 'The bindingID {} is not found in the storage'.format(bindingID)
        cls.__storage[bindingID].subscribe(subscriber)

    @classmethod
    def unsubscribe(cls, bindingID, subscriber):
        assert bindingID in cls.__storage, 'The bindingID {} is not found in the storage'.format(bindingID)
        cls.__storage[bindingID].unsubscribe(subscriber)


def bindRO(bindingID):
    """Creates reference to read only descriptor.
    :param bindingID: one of BINDING_ID.*.
    :return: _GlobalDataDescriptor.
    """
    return _GlobalDataDescriptor(bindingID, reader=True, writer=False)


def bindRW(bindingID):
    """Creates reference to read-write descriptor.
    NOTE: This routine can be used in AvatarInputHandler package only.
    :param bindingID: one of BINDING_ID.*.
    :return: _GlobalDataDescriptor.
    """
    return _GlobalDataDescriptor(bindingID, reader=True, writer=True)


def subscribe(bindingID, observer):
    """Adds subscriber that wants listening changing value.
    :param bindingID: one of GLOBAL_BINDING_ID.
    :param observer: callable object.
    """
    _GlobalDataDescriptor.subscribe(bindingID, observer)


def unsubscribe(bindingID, observer):
    """Removes subscriber.
    :param bindingID: one of GLOBAL_BINDING_ID.
    :param observer: callable object.
    """
    _GlobalDataDescriptor.unsubscribe(bindingID, observer)


def clear():
    """Clears data."""
    _GlobalDataDescriptor.clear()

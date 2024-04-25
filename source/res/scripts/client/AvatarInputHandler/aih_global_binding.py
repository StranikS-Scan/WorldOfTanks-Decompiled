# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/aih_global_binding.py
import logging
import Math
from aih_constants import CTRL_MODE_NAME, GUN_MARKER_FLAG, STRATEGIC_CAMERA, CHARGE_MARKER_STATE
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_FLOAT_EPSILON = 0.003

class BINDING_ID(object):
    CTRL_MODE_NAME = 1
    AIM_OFFSET = 2
    ZOOM_FACTOR = 3
    GUN_MARKERS_FLAGS = 4
    CLIENT_GUN_MARKER_STATE = 5
    SERVER_GUN_MARKER_STATE = 6
    DUAL_ACC_GUN_MARKER_STATE = 7
    CLIENT_GUN_MARKER_DATA_PROVIDER = 8
    CLIENT_SPG_GUN_MARKER_DATA_PROVIDER = 9
    SERVER_GUN_MARKER_DATA_PROVIDER = 10
    SERVER_SPG_GUN_MARKER_DATA_PROVIDER = 11
    DUAL_ACC_GUN_MARKER_DATA_PROVIDER = 12
    STRATEGIC_CAMERA = 13
    CHARGE_MARKER_STATE = 14
    SPG_SHOTS_INDICATOR_STATE = 15
    CLIENT_ASSAULT_SPG_GUN_MARKER_DATA_PROVIDER = 16
    SERVER_ASSAULT_SPG_GUN_MARKER_DATA_PROVIDER = 17
    ASSAULT_SPG_CAMERA_STATE = 18
    RANGE = (CTRL_MODE_NAME,
     AIM_OFFSET,
     ZOOM_FACTOR,
     GUN_MARKERS_FLAGS,
     CLIENT_GUN_MARKER_STATE,
     SERVER_GUN_MARKER_STATE,
     DUAL_ACC_GUN_MARKER_STATE,
     CLIENT_GUN_MARKER_DATA_PROVIDER,
     CLIENT_SPG_GUN_MARKER_DATA_PROVIDER,
     SERVER_GUN_MARKER_DATA_PROVIDER,
     SERVER_SPG_GUN_MARKER_DATA_PROVIDER,
     STRATEGIC_CAMERA,
     CHARGE_MARKER_STATE,
     SPG_SHOTS_INDICATOR_STATE,
     DUAL_ACC_GUN_MARKER_DATA_PROVIDER,
     CLIENT_ASSAULT_SPG_GUN_MARKER_DATA_PROVIDER,
     SERVER_ASSAULT_SPG_GUN_MARKER_DATA_PROVIDER,
     ASSAULT_SPG_CAMERA_STATE)


class _Observable(object):

    def __init__(self, value):
        super(_Observable, self).__init__()
        self.value = value
        self.__subscribers = []

    def clear(self):
        del self.__subscribers[:]

    def subscribe(self, subscriber):
        if subscriber not in self.__subscribers:
            self.__subscribers.append(subscriber)
        else:
            _logger.error('Subscriber %r already added to observable %r', subscriber, self)

    def unsubscribe(self, subscriber):
        if subscriber in self.__subscribers:
            self.__subscribers.remove(subscriber)

    def change(self, other):
        if self._isChanged(other):
            self.value = other
            for subscriber in self.__subscribers:
                subscriber(self.value)

            return True
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
 BINDING_ID.DUAL_ACC_GUN_MARKER_STATE: lambda : _Observable((Math.Vector3(0.0, 0.0, 0.0), 0.0, None)),
 BINDING_ID.CLIENT_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.CLIENT_SPG_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.CLIENT_ASSAULT_SPG_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.SERVER_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.SERVER_SPG_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.SERVER_ASSAULT_SPG_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.DUAL_ACC_GUN_MARKER_DATA_PROVIDER: lambda : _Observable(None),
 BINDING_ID.STRATEGIC_CAMERA: lambda : _Observable(STRATEGIC_CAMERA.DEFAULT),
 BINDING_ID.CHARGE_MARKER_STATE: lambda : _Observable(CHARGE_MARKER_STATE.DEFAULT),
 BINDING_ID.SPG_SHOTS_INDICATOR_STATE: lambda : _Observable({}),
 BINDING_ID.ASSAULT_SPG_CAMERA_STATE: lambda : _Observable(0)}

class _GlobalDataDescriptor(object):
    __slots__ = ('__bindingID', '__reader', '__writer')
    __storage = {}

    def __init__(self, bindingID, reader=False, writer=False):
        super(_GlobalDataDescriptor, self).__init__()
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
        for bindingID, observable in cls.__storage.iteritems():
            observable.clear()
            observable.change(_DEFAULT_VALUES[bindingID]().value)

    @classmethod
    def subscribe(cls, bindingID, subscriber):
        if bindingID in cls.__storage:
            cls.__storage[bindingID].subscribe(subscriber)
        else:
            _logger.error('The bindingID %d is not found in the storage', bindingID)

    @classmethod
    def unsubscribe(cls, bindingID, subscriber):
        if bindingID in cls.__storage:
            cls.__storage[bindingID].unsubscribe(subscriber)
        else:
            _logger.error('The bindingID %d is not found in the storage', bindingID)


def bindRO(bindingID):
    if bindingID not in BINDING_ID.RANGE:
        raise SoftException('bindingID is invalid: {}'.format(bindingID))
    return _GlobalDataDescriptor(bindingID, reader=True, writer=False)


def bindRW(bindingID):
    if bindingID not in BINDING_ID.RANGE:
        raise SoftException('bindingID is invalid: {}'.format(bindingID))
    return _GlobalDataDescriptor(bindingID, reader=True, writer=True)


def subscribe(bindingID, observer):
    _GlobalDataDescriptor.subscribe(bindingID, observer)


def unsubscribe(bindingID, observer):
    _GlobalDataDescriptor.unsubscribe(bindingID, observer)


def clear():
    _GlobalDataDescriptor.clear()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/extension_components.py
import functools
import typing
import weakref
from copy import copy
from Event import EventManager, Event
from metaclass import Metaclass
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Callable, Any, Type

def _checkMethod(func, funcType):
    return getattr(func, funcType, False)


class Extendable(object):
    __metaclass__ = Metaclass
    componentTypes = []
    _extendableMethodNames = set()

    def __init__(self):
        self._components = None
        self.__eventsManager = None
        self.events = None
        return

    @classmethod
    def __init_subclass__(cls, name, bases, attrs):
        cls.componentTypes = []
        cls._extendableMethodNames = copy(cls._extendableMethodNames)
        isTop = True if Extendable in bases else False
        initMethods = 0 if isTop else 1
        destroyMethods = 0 if isTop else 1
        for methodName, item in cls.__dict__.iteritems():
            if not callable(item):
                continue
            if _checkMethod(item, 'isExtendableMethod'):
                cls._extendableMethodNames.add(methodName)
            if _checkMethod(item, 'isInitMethod'):
                initMethods += 1
            if _checkMethod(item, 'isDestroyMethod'):
                destroyMethods += 1

        if initMethods != 1 and destroyMethods != 1:
            raise SoftException('Wrong Extendable {} configuration. initMethods={}, destroyMethods={}'.format(cls.__name__, initMethods, destroyMethods))

    @classmethod
    def hasExtendableMethod(cls, name):
        return name in cls._extendableMethodNames

    @classmethod
    def addComponentType(cls, extensionComponentClass):
        cls.componentTypes.append(extensionComponentClass)
        for subClass in cls.__subclasses__():
            subClass.addComponentType(extensionComponentClass)

    def initComponents(self, *args, **kwargs):
        self._components = []
        self.__eventsManager = EventManager()
        self.events = {methodName:Event(self.__eventsManager) for methodName in self._extendableMethodNames}
        for component in self.componentTypes:
            self._components.append(component(weakref.proxy(self), *args, **kwargs))

    def destroyComponents(self):
        for component in reversed(self._components):
            component.destroy()

        self.__eventsManager.clear()
        self.events = {}
        self._components = []


def extendableMethod(method):
    method.isExtendableMethod = True

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        self.events[method.__name__](*args, **kwargs)

    return wrapper


def initMethod(method):
    method.isInitMethod = True

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        method(self, *args, **kwargs)
        self.initComponents(*args, **kwargs)

    return wrapper


def destroyMethod(method):
    method.isDestroyMethod = True

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self.destroyComponents()
        method(self, *args, **kwargs)

    return wrapper


def extensionMethod(method):
    method.isExtensionMethod = True
    return method


class ExtensionComponent(object):
    __metaclass__ = Metaclass
    _extensionMethodNames = []

    @classmethod
    def __init_subclass__(cls, name, bases, attrs):
        cls._extensionMethodNames = [ name for name, item in cls.__dict__.iteritems() if callable(item) and _checkMethod(item, 'isExtensionMethod') ]

    @classmethod
    def getExtensionMethods(cls):
        return cls._extensionMethodNames

    def __init__(self, parent, *_, **__):
        self.parent = parent
        for methodName in self._extensionMethodNames:
            self.parent.events[methodName] += getattr(self, methodName)

    def destroy(self):
        for methodName in self._extensionMethodNames:
            self.parent.events[methodName] -= getattr(self, methodName)


def registerExtensionClassComponent(extendableClass, extensionComponentClass):
    for name in extensionComponentClass.getExtensionMethods():
        if not extendableClass.hasExtendableMethod(name):
            raise SoftException('Wrong Extension component {} configuration'.format(extensionComponentClass.__name__))

    extendableClass.addComponentType(extensionComponentClass)

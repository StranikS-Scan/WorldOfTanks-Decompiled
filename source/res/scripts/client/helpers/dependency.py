# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/dependency.py
"""
Package to provide external dependencies (dependency injection) to various components of application.

Usage:

1. Creates callable configuration:
    def getServices(manager):
        # creates instance of service and adds it to manager by specified class.
        # uses specified class to get access to desired service.
        manager.addInstance(SomeServiceClass, SomeService(), finalizer='fini')

        # adds callable object to create service to manager by specified class.
        # services will be created at first time when someone get access to desired service.
        manager.bindRuntime(RuntimeServiceClass, createRuntimeService,)

        # adds other callable configuration.
        manager.addConfig(getOtherServices)

    Note: Services are removed from the manager in reverse order to their adding.

2. Creates manager of dependencies:
    dependency.configure(getServices)

3. There are two way to get access to desired service:
    - use descriptor in class:
        class SomeView(...):
            service = dependency.descriptor(SomeServiceClass)

    - use direct access to desired service:
        service = dependency.instance(SomeServiceClass)

4. When application is closing, clears all resources of services:
    dependency.clear()
"""
import functools
import inspect
from debug_utils import LOG_DEBUG
from ids_generators import SequenceIDGenerator
_g_manager = None
_MAX_ORDER_NUMBER = 32767
_orderGen = SequenceIDGenerator(lowBound=0, highBound=_MAX_ORDER_NUMBER)

def configure(config):
    """Creates manager of dependencies and it is configured with callable config.
    :param config: callable object that is invoke with DependencyManager object as argument.
    :return: instance of manager of dependencies.
    :exception: DependencyError.
    """
    global _g_manager
    if _g_manager is not None:
        raise DependencyError('Manager of dependencies is already created and configured')
    _g_manager = DependencyManager()
    _g_manager.addConfig(config)
    return _g_manager


def clear():
    """Clears dependency manager if it's present."""
    global _g_manager
    if _g_manager is not None:
        _g_manager.clear()
        _g_manager = None
    return


def instance(class_):
    """Gets instance of service by class if manager of dependencies is created and configured.
    :param class_: class of service.
    :return: instance of service.
    :exception: DependencyError.
    """
    if _g_manager is None:
        raise DependencyError('Manager of dependencies is not created and configured')
    return _g_manager.getService(class_)


def descriptor(class_):
    """Creates descriptor to get desired service in some classes.
    :param class_: class of service.
    :return: descriptor to get desired service.
    """
    return _ServiceDescriptor(class_)


class replace_none_kwargs(object):
    """ Decorator to replace named argument if it equals None to required service.
    Usage:
    
        @replace_none_kwargs(service=IService)
        def foo(value, service1=None):
            ...
    """

    def __init__(self, **services):
        super(replace_none_kwargs, self).__init__()
        self.__services = {}
        for name, class_ in services.iteritems():
            if not inspect.isclass(class_):
                raise DependencyError('Value is not class, {}'.format(class_))
            self.__services[name] = class_

    def __call__(self, func):
        spec = inspect.getargspec(func)
        for name, class_ in self.__services.iteritems():
            if name not in spec.args:
                raise DependencyError('Argument {} is not found in {}'.format(name, func))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for name, class_ in self.__services.iteritems():
                if name not in kwargs:
                    actual = None
                else:
                    actual = kwargs[name]
                if actual is None:
                    kwargs[name] = instance(class_)

            return func(*args, **kwargs)

        return wrapper


class DependencyError(Exception):
    pass


class DependencyManager(object):
    """Class of dependency manager."""
    __slots__ = ('__services',)

    def __init__(self):
        super(DependencyManager, self).__init__()
        self.__services = {}

    def getService(self, class_):
        """ Gets instance of service by class.
        :param class_: class of service.
        :return: instance of service.
        :exception: DependencyError.
        """
        try:
            result = self.__services[class_].value()
        except KeyError:
            raise DependencyError('Service {} is not created'.format(class_))

        return result

    def addInstance(self, class_, obj, finalizer=None):
        """Adds instance of service to manager by specified class.
        :param class_: class of service.
        :param obj: instance of service.
        :param finalizer: callable object or string containing name of service method
            that is invoked when service is removed from manager (dependency.clear).
        """
        self._validate(class_)
        self.__services[class_] = _DependencyItem(order=_orderGen.next(), service=obj, finalizer=finalizer)
        LOG_DEBUG('Instance of service is added', class_, obj)

    def addRuntime(self, class_, creator, finalizer=None):
        """Adds callable object to create service to manager by specified class.
        This callable object is invoked at first access to service.
        :param class_: class of service.
        :param creator: callable object to create service.
        :param finalizer: callable object or string containing name of service method
            that is invoked when service is removed from manager (dependency.clear).
        """
        self._validate(class_)
        self.__services[class_] = _RuntimeItem(creator, finalizer=finalizer)
        LOG_DEBUG('Factory of service is added', class_)

    def addConfig(self, config):
        """ Adds callable configuration to create services.
        :param config: callable configuration.
        """
        if not callable(config):
            raise DependencyError('Config must be callable')
        config(self)

    def clear(self):
        """Clears dependency manager."""
        services = sorted(self.__services.itervalues(), key=lambda item: item.order(), reverse=True)
        for service in services:
            service.finalize()

        for service in services:
            service.clear()

        self.__services.clear()

    def _validate(self, class_):
        if not inspect.isclass(class_):
            raise DependencyError('First argument is not class, {}'.format(class_))
        if class_ in self.__services:
            raise DependencyError('Service {} is already added'.format(class_))


class _ServiceDescriptor(object):
    __slots__ = ('__class',)

    def __init__(self, class_):
        super(_ServiceDescriptor, self).__init__()
        self.__class = class_

    def __set__(self, _, value):
        raise DependencyError('Service {} can not be rewritten'.format(self.__class))

    def __get__(self, inst, owner=None):
        return instance(self.__class)


class _DependencyItem(object):
    __slots__ = ('_order', '_service', '_finalizer')

    def __init__(self, order=_MAX_ORDER_NUMBER, service=None, finalizer=None):
        super(_DependencyItem, self).__init__()
        self._order = order
        self._service = service
        if finalizer is not None and not callable(finalizer) and not isinstance(finalizer, str):
            raise DependencyError('Finalizer {} is invalid'.format(finalizer))
        self._finalizer = finalizer
        return

    def value(self):
        return self._service

    def order(self):
        return self._order

    def finalize(self):
        if self._service is None or self._finalizer is None:
            return
        else:
            if callable(self._finalizer):
                self._finalizer(self._service)
            else:
                finalizer = getattr(self._service, self._finalizer, None)
                if finalizer is not None and callable(finalizer):
                    finalizer()
                else:
                    raise DependencyError('Finalizer {} is not found'.format(self._finalizer))
            return

    def clear(self):
        self._finalizer = None
        self._service = None
        return


class _RuntimeItem(_DependencyItem):
    __slots__ = ('__isCreatorInvoked', '__creator')

    def __init__(self, creator, finalizer=None):
        super(_RuntimeItem, self).__init__(finalizer=finalizer)
        self.__isCreatorInvoked = False
        self.__creator = creator

    def value(self):
        if not self.__isCreatorInvoked:
            self.__isCreatorInvoked = True
            self._service = self.__creator()
            self._order = _orderGen.next()
        return self._service

    def clear(self):
        self.__creator = None
        super(_RuntimeItem, self).clear()
        return

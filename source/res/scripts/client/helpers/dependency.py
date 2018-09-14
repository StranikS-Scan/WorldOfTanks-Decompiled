# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/dependency.py
"""
Package to provide external dependencies (dependency injection) to various components of application.

Usage:

1. Creates callable configuration:
    def getServices(manager):
        # creates instance of service and binds specified class to created instance of service.
        manager.bindInstance(SomeServiceClass, SomeService(), finalizer='fini')

        # binds specified class to callable object to create service.
        manager.bindRuntime(RuntimeServiceClass, createRuntimeService,)

        # adds other callable configuration.
        manager.install(getOtherServices)

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
    _g_manager.install(config)
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
    """Creates descriptor to get desired service in some object.
    :param class_: class of service.
    :return: descriptor to get desired service.
    """
    return _ServiceDescriptor(class_)


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
        if class_ in self.__services:
            result = self.__services[class_].value()
        else:
            if not callable(class_):
                raise DependencyError('Runtime service can not be created, {} is not callable'.format(class_))
            result = class_()
            LOG_DEBUG('Runtime service is created and added', class_, result)
            self.__services[class_] = _DependencyItem(order=_orderGen.next(), service=result)
        return result

    def bindInstance(self, class_, obj, finalizer=None):
        """Binds specified class to instance of service.
        :param class_: class of service.
        :param obj: instance of service.
        :param finalizer: callable object or string containing name of service method
            that is invoked when service is removed from manager (dependency.clear).
        :return: instance of manager.
        """
        self._validate(class_)
        self.__services[class_] = _DependencyItem(order=_orderGen.next(), service=obj, finalizer=finalizer)
        LOG_DEBUG('Instance of service is added', class_, obj)
        return self

    def bindRuntime(self, class_, creator, finalizer=None):
        """Binds specified class to callable object to create service.
        This callable object is invoked at first access to service.
        :param class_: class of service.
        :param creator: callable object to create service.
        :param finalizer: callable object or string containing name of service method
            that is invoked when service is removed from manager (dependency.clear).
        :return: instance of manager.
        """
        self._validate(class_)
        self.__services[class_] = _RuntimeItem(creator, finalizer=finalizer)
        LOG_DEBUG('Factory of service is added', class_)
        return self

    def install(self, config):
        """ Install callable configuration to create services.
        :param config: callable configuration.
        :return: instance of manager.
        """
        if not callable(config):
            raise DependencyError('Config must be callable')
        config(self)
        return self

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

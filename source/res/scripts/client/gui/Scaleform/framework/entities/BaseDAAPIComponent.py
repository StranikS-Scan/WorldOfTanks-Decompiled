# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/BaseDAAPIComponent.py
import logging
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule
from gui.Scaleform.framework.entities.abstract.BaseDAAPIComponentMeta import BaseDAAPIComponentMeta
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
_logger = logging.getLogger(__name__)

class BaseDAAPIComponent(BaseDAAPIComponentMeta):

    def __init__(self):
        super(BaseDAAPIComponent, self).__init__()
        self.__components = {}
        self.__alias = None
        self.__isActive = False
        return

    @property
    def components(self):
        return self.__components

    def getComponent(self, alias):
        if alias in self.__components:
            component = self.__components[alias]
        else:
            component = None
        return component

    def setAlias(self, alias):
        self.__alias = alias

    def getAlias(self):
        return self.__alias

    def setActive(self, isActive):
        self.__isActive = isActive

    def getActive(self):
        return self.__isActive

    def reloadComponents(self):
        snapshot = [ (viewPy.flashObject, viewAlias) for viewAlias, viewPy in self.__components.iteritems() ]
        self.__destroyPythonComponents(pyReloading=True)
        for flashObject, alias in snapshot:
            self.registerFlashComponent(flashObject, alias)

    def registerFlashComponent(self, component, alias, *args):
        from gui.Scaleform.framework import g_entitiesFactories
        componentPy, idx = g_entitiesFactories.factory(alias, *args)
        if componentPy is not None:
            componentPy = g_entitiesFactories.initialize(componentPy, component, idx)
        else:
            _logger.error('Component %s not found in python', alias)
            return
        if not isinstance(componentPy, BaseDAAPIModule):
            _logger.error('Registered component %r should extend a BaseDAAPIModule class!', componentPy)
            return
        else:
            if alias in self.__components.keys():
                _logger.warning('Class with alias `%s` already registered in object %r. It will be rewritten.', alias, self)
            self.__components[alias] = componentPy
            componentPy.setEnvironment(self.app)
            componentPy.create()
            self.__fireRegisteringEvent(events.ComponentEvent.COMPONENT_REGISTERED, componentPy, alias)
            self._onRegisterFlashComponent(componentPy, alias)
            return

    def isFlashComponentRegistered(self, alias):
        return alias in self.__components

    def unregisterFlashComponent(self, alias):
        res = None
        try:
            res = self.__components[alias]
        except KeyError:
            _logger.critical('Could not unregister component because there is no registered component with such alias: %s', alias)

        if res is not None:
            self.__unregisterPythonComponent(alias, res)
        return

    def _invalidate(self, *args, **kwargs):
        super(BaseDAAPIComponent, self)._invalidate(*args, **kwargs)
        for c in self.__components.itervalues():
            c.validate()

    def _dispose(self):
        self.__destroyPythonComponents(pyReloading=False)
        super(BaseDAAPIComponent, self)._dispose()

    def _disposeWithReloading(self):
        self.__destroyPythonComponents(pyReloading=True)
        super(BaseDAAPIComponent, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        pass

    def _onUnregisterFlashComponent(self, viewPy, alias):
        pass

    def __unregisterPythonComponent(self, alias, viewPy):
        if viewPy not in self.__components.values():
            _logger.warning('There is no flash object registered in %r: %r', self, viewPy)
            return
        self._onUnregisterFlashComponent(viewPy, alias)
        del self.__components[alias]
        self.__fireRegisteringEvent(events.ComponentEvent.COMPONENT_UNREGISTERED, viewPy, alias)
        viewPy.destroy()

    def __destroyPythonComponents(self, pyReloading=False):
        while self.__components:
            alias, viewPy = self.__components.popitem()
            self._onUnregisterFlashComponent(viewPy, alias)
            self.__fireRegisteringEvent(events.ComponentEvent.COMPONENT_UNREGISTERED, viewPy, alias)
            viewPy.setPyReloading(pyReloading)
            viewPy.destroy()

    def __fireRegisteringEvent(self, event, componentPy, alias):
        g_eventBus.handleEvent(events.ComponentEvent(event, self, componentPy, alias), EVENT_BUS_SCOPE.GLOBAL)

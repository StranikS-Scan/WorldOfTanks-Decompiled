# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/BaseDAAPIComponent.py
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_WARNING
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule
from gui.Scaleform.framework.entities.abstract.BaseDAAPIComponentMeta import BaseDAAPIComponentMeta
from gui.shared import g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ComponentEvent

class BaseDAAPIComponent(BaseDAAPIComponentMeta):

    def __init__(self):
        super(BaseDAAPIComponent, self).__init__()
        self.__components = {}

    @property
    def components(self):
        return self.__components

    def getComponent(self, alias):
        if alias in self.__components:
            component = self.__components[alias]
        else:
            component = None
        return component

    def reloadComponents(self):
        """Destroys all components and create new components in the python only.
        NOTE: This method is used in battle replay only, because replay destroys all entities
        when player rewinds replay back.
        """
        snapshot = map(lambda (viewAlias, viewPy): (viewPy.flashObject, viewAlias), self.__components.iteritems())
        self.__destroyPythonComponents(pyReloading=True)
        for flashObject, alias in snapshot:
            self.registerFlashComponent(flashObject, alias)

    def registerFlashComponent(self, component, alias, *args):
        from gui.Scaleform.framework import g_entitiesFactories
        componentPy, idx = g_entitiesFactories.factory(alias, *args)
        if componentPy is not None:
            componentPy = g_entitiesFactories.initialize(componentPy, component, idx)
        else:
            LOG_ERROR('Component %s not found in python'.format(alias), alias)
            return
        if not isinstance(componentPy, BaseDAAPIModule):
            LOG_ERROR('registered component {0} should extend a BaseDAAPIModule class!'.format(str(componentPy)))
            return
        else:
            if alias in self.__components.keys():
                LOG_WARNING('Class with alias `%s` already registered in object %s. It will be rewritten.' % (alias, str(self)))
            self.__components[alias] = componentPy
            componentPy.setEnvironment(self.app)
            componentPy.create()
            self.__fireRegisteringEvent(ComponentEvent.COMPONENT_REGISTERED, componentPy, alias)
            self._onRegisterFlashComponent(componentPy, alias)
            return

    def isFlashComponentRegistered(self, alias):
        try:
            self.__components[alias]
        except Exception:
            return False

        return True

    def unregisterFlashComponent(self, alias):
        res = None
        try:
            res = self.__components[alias]
        except KeyError:
            LOG_ERROR("Couldn't unregister component because there is no registered component with such alias: ", str(alias))
            LOG_CURRENT_EXCEPTION()

        if res is not None:
            self.__unregisterPythonComponent(alias, res)
        return

    def _invalidate(self, *args, **kwargs):
        """
        Performs self re-initialization, including child re-initialization. Note that all parameters should have
        default value (typically None) to prevent crashes when args or/and kwargs are missed.
        """
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
            return LOG_WARNING('There is no flash object registered in %s: %s' % (str(self), str(viewPy)))
        self._onUnregisterFlashComponent(viewPy, alias)
        del self.__components[alias]
        self.__fireRegisteringEvent(ComponentEvent.COMPONENT_UNREGISTERED, viewPy, alias)
        viewPy.destroy()

    def __destroyPythonComponents(self, pyReloading=False):
        while self.__components:
            alias, viewPy = self.__components.popitem()
            self._onUnregisterFlashComponent(viewPy, alias)
            self.__fireRegisteringEvent(ComponentEvent.COMPONENT_UNREGISTERED, viewPy, alias)
            viewPy.setPyReloading(pyReloading)
            viewPy.destroy()

    def __fireRegisteringEvent(self, event, componentPy, alias):
        g_eventBus.handleEvent(ComponentEvent(event, self, componentPy, alias), EVENT_BUS_SCOPE.GLOBAL)

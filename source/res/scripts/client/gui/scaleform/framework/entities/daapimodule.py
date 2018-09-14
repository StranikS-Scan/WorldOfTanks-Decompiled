# Embedded file name: scripts/client/gui/Scaleform/framework/entities/DAAPIModule.py
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared.events import ComponentEvent, FocusEvent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE

class DAAPIModule(EventSystemEntity):

    def __init__(self):
        super(DAAPIModule, self).__init__()
        self.__flashObject = None
        self.__components = {}
        self.__isScriptSet = False
        return

    def _printOverrideError(self, methodName):
        LOG_ERROR('Method must be override!', methodName, self.__class__)

    def _isDAAPIInited(self):
        return self.flashObject is not None and self.__flashObject.as_isDAAPIInited()

    @property
    def flashObject(self):
        return self.__flashObject

    @property
    def components(self):
        return self.__components

    def setFlashObject(self, movieClip, autoPopulate = True, setScript = True):
        if movieClip is not None:
            self.__flashObject = movieClip
            self.__isScriptSet = setScript
            if setScript:
                try:
                    self.__flashObject.script = self
                except:
                    raise Exception, 'Can not initialize daapi in ' + str(self)

            if autoPopulate:
                if self._isCreated():
                    LOG_ERROR('object {0} is already created! Please, set flag autoPopulate=False'.format(str(self)))
                else:
                    self.create()
        else:
            LOG_ERROR('flashObject reference can`t be None!')
        return

    def registerFlashComponent(self, component, alias, *args):
        from gui.Scaleform.framework import g_entitiesFactories
        componentPy, idx = g_entitiesFactories.factory(alias, *args)
        if componentPy is not None:
            componentPy = g_entitiesFactories.initialize(componentPy, component, idx)
        else:
            LOG_ERROR('Component %s not found in python'.format(alias), alias)
            return
        from gui.Scaleform.framework.entities.View import View
        if isinstance(componentPy, View):
            LOG_ERROR('registered component {0} can`t extend a View class. It must be DAAPIModule only!'.format(str(componentPy)))
            return
        else:
            if alias in self.__components.keys():
                LOG_WARNING('Class with alias `%s` already registered in object %s.\t\t\t\tIt will be rewritten.' % (alias, str(self)))
            self.__components[alias] = componentPy
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

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED))

    def _populate(self):
        super(DAAPIModule, self)._populate()
        if self.__flashObject is not None:
            self.__flashObject.as_populate()
        return

    def _dispose(self):
        super(DAAPIModule, self)._dispose()
        while self.__components:
            alias, viewPy = self.__components.popitem()
            self._onUnregisterFlashComponent(viewPy, alias)
            self.__fireRegisteringEvent(ComponentEvent.COMPONENT_UNREGISTERED, viewPy, alias)
            viewPy.destroy()

        if self.__flashObject is not None:
            try:
                if self.__isScriptSet:
                    self.__flashObject.as_dispose()
            except:
                LOG_ERROR('Error during %s flash disposing' % str(self))

            if self.__isScriptSet:
                self.__flashObject.script = None
            self.__flashObject = None
        return

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

    def __fireRegisteringEvent(self, event, componentPy, alias):
        g_eventBus.handleEvent(ComponentEvent(event, self, componentPy, alias), EVENT_BUS_SCOPE.GLOBAL)

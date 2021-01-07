# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/external_components.py
import weakref
from collections import namedtuple
from gui.Scaleform.flash_wrapper import FlashComponentWrapper
from gui.Scaleform.framework.application import DAAPIRootBridge
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class _ExternalComponentState(object):
    UNDEFINED = 0
    CREATED = 1
    CLOSED = 2
    REGISTERED = 4
    UNREGISTERED = 8
    INITED = CREATED | REGISTERED
    DESTROYED = CLOSED | UNREGISTERED


class IExternalFlashComponent(object):

    def setOwner(self, owner):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


ExternalFlashSettings = namedtuple('ExternalFlashSettings', ('alias', 'url', 'rootPath', 'initCallback'))

class ExternalFlashComponent(FlashComponentWrapper, IExternalFlashComponent):

    def __init__(self, settings):
        super(ExternalFlashComponent, self).__init__()
        self.__settings = settings
        self.__owner = None
        self.__state = _ExternalComponentState.UNDEFINED
        self.__bridge = DAAPIRootBridge(settings.rootPath, settings.initCallback)
        return

    @property
    def alias(self):
        return self.__settings.alias

    @property
    def owner(self):
        return self.__owner

    def createExternalComponent(self):
        self.createComponent(swf=self.__settings.url)
        self.__bridge.setPyScript(weakref.proxy(self))

    def setOwner(self, owner):
        self.__owner = owner
        self.__tryToInvokeRegisterEvent(_ExternalComponentState.REGISTERED)

    def close(self):
        self.__invokeUnregisterEvent()
        self.__owner = None
        self.__state ^= ~_ExternalComponentState.CREATED
        self.__state |= _ExternalComponentState.CLOSED
        if self.__bridge is not None:
            self.__bridge.clear()
            self.__bridge = None
        super(ExternalFlashComponent, self).close()
        return

    def getSize(self):
        return self.component.size

    def setSize(self, width, height):
        self.component.size = (width, height)

    def getScale(self):
        return self.movie.stage.scaleX

    def setScale(self, scale):
        stage = self.movie.stage
        stage.scaleX = scale
        stage.scaleY = scale

    def startPlugins(self):
        pass

    def afterCreate(self):
        super(ExternalFlashComponent, self).afterCreate()
        self.__tryToInvokeRegisterEvent(_ExternalComponentState.CREATED)

    def invokeRegisterComponentForReplay(self):
        g_eventBus.handleEvent(events.ComponentEvent(events.ComponentEvent.COMPONENT_REGISTERED, self.owner, self, self.alias), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __tryToInvokeRegisterEvent(self, step):
        prevSteps = self.__state
        self.__state |= step
        if prevSteps != self.__state and self.__state == _ExternalComponentState.INITED:
            g_eventBus.handleEvent(events.ComponentEvent(events.ComponentEvent.COMPONENT_REGISTERED, self.owner, self, self.alias), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __invokeUnregisterEvent(self):
        if self.__state & _ExternalComponentState.REGISTERED > 0:
            self.__state ^= _ExternalComponentState.REGISTERED
            self.__state |= _ExternalComponentState.UNREGISTERED
            g_eventBus.handleEvent(events.ComponentEvent(events.ComponentEvent.COMPONENT_UNREGISTERED, self.owner, self, self.alias), scope=EVENT_BUS_SCOPE.GLOBAL)

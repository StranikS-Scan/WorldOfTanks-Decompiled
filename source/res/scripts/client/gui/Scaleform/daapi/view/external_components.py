# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/external_components.py
import weakref
from collections import namedtuple
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.Flash import Flash
from gui.Scaleform.framework.application import DAAPIRootBridge
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ComponentEvent

class _EXTERNAL_COMPONENT_STATE(object):
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

class ExternalFlashComponent(Flash, IExternalFlashComponent):

    def __init__(self, settings):
        super(ExternalFlashComponent, self).__init__(settings.url, path=SCALEFORM_SWF_PATH_V3)
        self.__settings = settings
        self.__owner = None
        self.__state = _EXTERNAL_COMPONENT_STATE.UNDEFINED
        self.__bridge = DAAPIRootBridge(settings.rootPath, settings.initCallback)
        self.__bridge.setPyScript(weakref.proxy(self))
        return

    @property
    def alias(self):
        return self.__settings.alias

    @property
    def owner(self):
        return self.__owner

    def setOwner(self, owner):
        self.__owner = owner
        self.__tryToInvokeRegisterEvent(_EXTERNAL_COMPONENT_STATE.REGISTERED)

    def close(self):
        self.__invokeUnregisterEvent()
        self.__owner = None
        self.__state ^= ~_EXTERNAL_COMPONENT_STATE.CREATED
        self.__state |= _EXTERNAL_COMPONENT_STATE.CLOSED
        if self.__bridge is not None:
            self.__bridge.clear()
            self.__bridge = None
        super(ExternalFlashComponent, self).close()
        return

    def isVisible(self):
        return self.component.visible

    def setVisible(self, visible):
        self.component.visible = visible

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

    def afterCreate(self):
        super(ExternalFlashComponent, self).afterCreate()
        self.__tryToInvokeRegisterEvent(_EXTERNAL_COMPONENT_STATE.CREATED)

    def __tryToInvokeRegisterEvent(self, step):
        prevSteps = self.__state
        self.__state |= step
        if prevSteps != self.__state and self.__state == _EXTERNAL_COMPONENT_STATE.INITED:
            g_eventBus.handleEvent(ComponentEvent(ComponentEvent.COMPONENT_REGISTERED, self.owner, self, self.alias), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __invokeUnregisterEvent(self):
        if self.__state & _EXTERNAL_COMPONENT_STATE.REGISTERED > 0:
            self.__state ^= _EXTERNAL_COMPONENT_STATE.REGISTERED
            self.__state |= _EXTERNAL_COMPONENT_STATE.UNREGISTERED
            g_eventBus.handleEvent(ComponentEvent(ComponentEvent.COMPONENT_UNREGISTERED, self.owner, self, self.alias), scope=EVENT_BUS_SCOPE.GLOBAL)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/external_components.py
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
        """Sets owner for external component.
        :param owner: object.
        """
        raise NotImplementedError

    def close(self):
        """Removes external component from display list."""
        raise NotImplementedError


ExternalFlashSettings = namedtuple('ExternalFlashSettings', ('alias', 'url', 'rootPath', 'initCallback'))

class ExternalFlashComponent(Flash, IExternalFlashComponent):
    """ Class to create external flash components that are added to battle page.
    Its behavior like ViewTypes.COMPONENT, but python initializes given components."""

    def __init__(self, settings):
        super(ExternalFlashComponent, self).__init__(settings.url, path=SCALEFORM_SWF_PATH_V3)
        assert isinstance(settings, ExternalFlashSettings), 'Settings are invalid'
        self.__settings = settings
        self.__owner = None
        self.__state = _EXTERNAL_COMPONENT_STATE.UNDEFINED
        self.__bridge = DAAPIRootBridge(settings.rootPath, settings.initCallback)
        self.__bridge.setPyScript(weakref.proxy(self))
        return

    @property
    def alias(self):
        """Gets name of view alias.
        :return: string containing name of view alias.
        """
        return self.__settings.alias

    @property
    def owner(self):
        """Gets owner of given component.
        :return: object.
        """
        return self.__owner

    def setOwner(self, owner):
        """Sets owner for external component and tries to register given component
        like other UI components.
        :param owner: object.
        """
        self.__owner = owner
        self.__tryToInvokeRegisterEvent(_EXTERNAL_COMPONENT_STATE.REGISTERED)

    def close(self):
        """Unregisters given component and removes it from display list."""
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
        """Is component visible.
        :return: bool.
        """
        return self.component.visible

    def setVisible(self, visible):
        """Sets visibility of component.
        :param visible: bool.
        """
        self.component.visible = visible

    def getSize(self):
        """Gets size of crosshair panel.
        :return: tuple(width, height).
        """
        return self.component.size

    def setSize(self, width, height):
        """Sets size of crosshair panel in pixels.
        :param width: integer containing width of panel.
        :param height: integer containing height of panel.
        """
        self.component.size = (width, height)

    def getScale(self):
        """Gets scale factor.
        :return: float containing scale factor.
        """
        return self.movie.stage.scaleX

    def setScale(self, scale):
        """Sets scale factor.
        :param scale: float containing new scale factor.
        """
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

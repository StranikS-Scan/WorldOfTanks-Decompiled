# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/camera_switcher.py
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager
from .abstract_switch_handler import AbstractSwitchHandler
from .customization_camera import CustomizationCamera

class CameraSwitcher(AbstractSwitchHandler):

    def __init__(self):
        super(CameraSwitcher, self).__init__()
        self.__cam = CustomizationCamera()

    def init(self):
        self.__cam.init()

    def fini(self):
        self.__cam.destroy()
        super(CameraSwitcher, self).fini()

    def switchTo(self, state, callback=None):
        self._state = state
        self.__onSwitch(callback)

    def subscribeToMouseEvents(self, event):
        event += self.__onMouseMove

    def unsubscribeFromMouseEvents(self, event):
        event -= self.__onMouseMove

    def addScrollListener(self, listener):
        self.__cam.addScrollListener(listener)

    def removeScrollListener(self, listener):
        self.__cam.removeScrollListener(listener)

    def _resetState(self):
        self.__cam.deactivate()
        super(CameraSwitcher, self)._resetState()

    def __onSwitch(self, callback=None):
        self.__cam.deactivate()
        if self._state is not None:
            self.__switchToCameraAnchor()
        super(CameraSwitcher, self).switchTo(self._state, callback)
        return

    @dependency.replace_none_kwargs(objMgr=ICustomizableObjectsManager)
    def __switchToCameraAnchor(self, objMgr=None):
        anchorDescr = objMgr.getCameraAnchor(self._state)
        if anchorDescr:
            entity = objMgr.getCustomizableEntity(self._state)
            if entity is not None:
                self.__cam.activate(entity.position, anchorDescr)
        return

    def __onMouseMove(self, dx, dy, delta):
        self.__cam.handleMouseEvent(dx, dy, delta)

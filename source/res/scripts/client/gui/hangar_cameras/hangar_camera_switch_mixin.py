# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_switch_mixin.py
from helpers import dependency
from hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from skeletons.gui.shared.utils import IHangarSpace

class HangarCameraSwitchMixin(object):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HangarCameraSwitchMixin, self).__init__()
        self.__inited = False

    def __init(self):
        cameraManager = self.__hangarSpace.space.getCameraManager()
        self.__isParalaxEnabled = cameraManager.rotationEnabled
        self.__isMovementEnabled = not cameraManager.isCameraIdleForcedDisable
        self.__inited = True

    def disableCamera(self):
        if not self.__inited:
            self.__init()
        self._disableParalaxMovement(True)
        self._disableCameraMovement(True)

    def restoreCamera(self):
        self._disableParalaxMovement(not self.__isParalaxEnabled)
        self._disableParalaxMovement(not self.__isMovementEnabled)

    def _disableParalaxMovement(self, disable):
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': disable,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)

    def _disableCameraMovement(self, disable):
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_CAMERA_MOVEMENT, ctx={'disable': disable}), EVENT_BUS_SCOPE.LOBBY)

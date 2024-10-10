# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/camera_manager.py
import CGF
from cgf_components.hangar_camera_manager import HangarCameraManager
from cgf_components.armory_yard_components import AssemblyStageIndexManager
from gui.shared import g_eventBus
from gui.shared.events import ArmoryYardEvent
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class CameraManager(object):

    def __init__(self):
        self.__camName = None
        self.__inTransition = False
        self.isStagePlaying = False
        return

    def init(self):
        self.cgfCameraManager.allowSetMinDist(False)
        g_eventBus.removeListener(ArmoryYardEvent.POI_ACTIVATED, self.__poiActivated)
        g_eventBus.addListener(ArmoryYardEvent.POI_ACTIVATED, self.__poiActivated)
        if self.cgfCameraManager.isActive:
            self.cgfCameraManager.onCameraSwitched += self.__onCameraSwitched
        else:
            self.cgfCameraManager.onStateChange += self.__onStateChange

    def destroy(self):
        g_eventBus.removeListener(ArmoryYardEvent.POI_ACTIVATED, self.__poiActivated)
        self.__camName = None
        return

    def __onStateChange(self, active):
        if active:
            self.cgfCameraManager.onCameraSwitched += self.__onCameraSwitched
            self.cgfCameraManager.onStateChange -= self.__onStateChange

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def goToPosition(self, data, instantly=True, hangarSpace=None):
        if data == self.__camName:
            return
        else:
            self.__camName = data
            if hangarSpace is not None and hangarSpace.space is not None:
                self.cgfStageManager.turnOffHighlight()
                self.__inTransition = True
                self.cgfCameraManager.switchByCameraName(self.__camName, instantly=instantly)
            return

    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def goToHangar(self, hangarSpace=None):
        self.__camName = None
        if hangarSpace is not None and hangarSpace.space is not None:
            cgfCameraManager = CGF.getManager(hangarSpace.space.getSpaceID(), HangarCameraManager)
            cgfCameraManager.switchToTank()
        return

    def __onCameraSwitched(self, _):
        if not self.isStagePlaying:
            self.cgfStageManager.turnOnHighlight(self.__camName)
        self.__inTransition = False

    def __poiActivated(self, event):
        cameraName = event.ctx['name']
        self.goToPosition(cameraName, instantly=False)

    @property
    def inTransition(self):
        return self.__inTransition

    @property
    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def cgfCameraManager(self, hangarSpace=None):
        return CGF.getManager(hangarSpace.space.getSpaceID(), HangarCameraManager)

    @property
    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def cgfStageManager(self, hangarSpace=None):
        return CGF.getManager(hangarSpace.space.getSpaceID(), AssemblyStageIndexManager)

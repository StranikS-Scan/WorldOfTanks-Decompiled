# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearBaseEntryObject.py
import BigWorld
from ClientSelectableObject import ClientSelectableObject
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ICustomizableObjectsManager

class NewYearBaseEntryObject(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _nyController = dependency.descriptor(INewYearController)

    def onEnterWorld(self, prereqs):
        super(NewYearBaseEntryObject, self).onEnterWorld(prereqs)
        self._nyController.onStateChanged += self.__onStateChanged
        self.__onStateChanged()
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def onLeaveWorld(self):
        self._nyController.onStateChanged -= self.__onStateChanged
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        super(NewYearBaseEntryObject, self).onLeaveWorld()

    def _addEdgeDetect(self):
        BigWorld.wgAddEdgeDetectEntity(self, 3, self.edgeMode, False)

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        if not self.__isHangarVehicleEntity(entityId):
            return
        if state == CameraMovementStates.FROM_OBJECT:
            self.setEnable(False)
        elif state == CameraMovementStates.ON_OBJECT:
            if not self.enabled and self._nyController.isEnabled():
                self.setEnable(True)

    def __isHangarVehicleEntity(self, entityId):
        return entityId == self._hangarSpace.space.vehicleEntityId

    def __onStateChanged(self):
        self.setEnable(self._nyController.isEnabled())

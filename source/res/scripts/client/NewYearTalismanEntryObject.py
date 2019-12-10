# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanEntryObject.py
import BigWorld
from ClientSelectableObject import ClientSelectableObject
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from helpers import dependency
from new_year.ny_constants import AnchorNames
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController, ICustomizableObjectsManager

class NewYearTalismanEntryObject(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _nyController = dependency.descriptor(INewYearController)

    def onEnterWorld(self, prereqs):
        super(NewYearTalismanEntryObject, self).onEnterWorld(prereqs)
        self._nyController.onStateChanged += self.__onStateChanged
        self.__onStateChanged()
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def onLeaveWorld(self):
        super(NewYearTalismanEntryObject, self).onLeaveWorld()
        self._nyController.onStateChanged -= self.__onStateChanged
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def onMouseClick(self):
        super(NewYearTalismanEntryObject, self).onMouseClick()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.ENTER_CUSTOME)
        NewYearNavigation.switchByAnchorName(AnchorNames.MASCOT)

    def _addEdgeDetect(self):
        BigWorld.wgAddEdgeDetectEntity(self, 3, self.edgeMode, False)

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        if state == CameraMovementStates.FROM_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                self.setEnable(False)
        elif state == CameraMovementStates.ON_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                if not self.enabled and self._nyController.isEnabled():
                    self.setEnable(True)

    def __isHangarVehicleEntity(self, entityId):
        return entityId == self._hangarSpace.space.vehicleEntityId

    def __onStateChanged(self):
        self.setEnable(self._nyController.isEnabled())

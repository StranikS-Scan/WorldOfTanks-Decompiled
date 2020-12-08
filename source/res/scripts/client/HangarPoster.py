# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarPoster.py
from ClientSelectableObject import ClientSelectableObject
from gui.game_control import CalendarInvokeOrigin
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from helpers import dependency
from skeletons.gui.game_control import ICalendarController
from skeletons.gui.shared.utils import IHangarSpace

class HangarPoster(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _calendarController = dependency.descriptor(ICalendarController)

    def onEnterWorld(self, prereqs):
        super(HangarPoster, self).onEnterWorld(prereqs)
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def onLeaveWorld(self):
        super(HangarPoster, self).onLeaveWorld()
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def onMouseClick(self):
        super(HangarPoster, self).onMouseClick()
        self._calendarController.showWindow(invokedFrom=CalendarInvokeOrigin.HANGAR)

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        if state == CameraMovementStates.FROM_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                self.setEnable(False)
        elif state == CameraMovementStates.ON_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                if not self.enabled:
                    self.setEnable(True)

    def __isHangarVehicleEntity(self, entityId):
        return entityId == self._hangarSpace.space.vehicleEntityId

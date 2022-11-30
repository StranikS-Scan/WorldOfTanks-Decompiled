# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarPoster.py
from ClientSelectableObject import ClientSelectableObject
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl.new_year.navigation import NewYearNavigation
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
        g_currentPreviewVehicle.onSelected += self.__onHeroTankSelected

    def onLeaveWorld(self):
        super(HangarPoster, self).onLeaveWorld()
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        g_currentPreviewVehicle.onSelected -= self.__onHeroTankSelected

    def onMouseClick(self):
        super(HangarPoster, self).onMouseClick()
        self._calendarController.showWindow()

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        enabled = None
        if NewYearNavigation.getCurrentObject() is not None:
            enabled = True
        elif state == CameraMovementStates.FROM_OBJECT:
            enabled = not self.__isHangarVehicleEntity(entityId)
        elif state == CameraMovementStates.ON_OBJECT:
            enabled = self.__isHangarVehicleEntity(entityId)
        if enabled is not None and enabled != self.enabled:
            self.setEnable(enabled)
        return

    def __isHangarVehicleEntity(self, entityId):
        return entityId == self._hangarSpace.space.vehicleEntityId

    def __onHeroTankSelected(self):
        if g_currentPreviewVehicle.item is not None:
            self.setEnable(g_currentPreviewVehicle.isHeroTank)
        return

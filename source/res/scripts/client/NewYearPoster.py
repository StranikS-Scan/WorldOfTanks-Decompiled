# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearPoster.py
import BigWorld
from ClientSelectableObject import ClientSelectableObject
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from helpers import dependency
from skeletons.gui.game_control import ICalendarController
from skeletons.gui.shared.utils import IHangarSpace

class NewYearPoster(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _adventCalendarCtrl = dependency.descriptor(ICalendarController)

    def __init__(self):
        super(NewYearPoster, self).__init__()
        self.__alphaFadeFashion = None
        return

    def onEnterWorld(self, prereqs):
        super(NewYearPoster, self).onEnterWorld(prereqs)
        self.__alphaFadeFashion = BigWorld.WGAlphaFadeFashion()
        self.__alphaFadeFashion.minAlpha = self.minAlpha
        self.__alphaFadeFashion.maxAlphaDist = self.maxAlphaDistance * self.maxAlphaDistance
        self.model.fashion = self.__alphaFadeFashion
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def onLeaveWorld(self):
        super(NewYearPoster, self).onLeaveWorld()
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)

    def onMouseClick(self):
        super(NewYearPoster, self).onMouseClick()
        self._adventCalendarCtrl.showCalendar()

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

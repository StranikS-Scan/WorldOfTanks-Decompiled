# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarPoster.py
import BigWorld
from ClientSelectableObject import ClientSelectableObject
from CurrentVehicle import g_currentPreviewVehicle
from gui.game_control import CalendarInvokeOrigin
from gui.shared import g_eventBus
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from helpers import dependency
from skeletons.gui.game_control import ICalendarController
from skeletons.gui.impl import INewYearNavigation
from skeletons.gui.shared.utils import IHangarSpace

class HangarPoster(ClientSelectableObject):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _calendarController = dependency.descriptor(ICalendarController)
    _newYearNavigation = dependency.descriptor(INewYearNavigation)

    def __init__(self):
        super(HangarPoster, self).__init__()
        self.__alphaFadeFashion = None
        return

    def onEnterWorld(self, prereqs):
        super(HangarPoster, self).onEnterWorld(prereqs)
        self.__alphaFadeFashion = BigWorld.WGAlphaFadeFashion()
        self.__alphaFadeFashion.minAlpha = self.minAlpha
        self.__alphaFadeFashion.maxAlphaDist = self.maxAlphaDistance * self.maxAlphaDistance
        self.model.fashion = self.__alphaFadeFashion
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        g_currentPreviewVehicle.onSelected += self.__onHeroTankSelected

    def onLeaveWorld(self):
        super(HangarPoster, self).onLeaveWorld()
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        g_currentPreviewVehicle.onSelected -= self.__onHeroTankSelected

    def onMouseClick(self):
        super(HangarPoster, self).onMouseClick()
        self._calendarController.showWindow(invokedFrom=CalendarInvokeOrigin.HANGAR)

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        enabled = None
        if self._newYearNavigation.getCurrentObject() is not None:
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

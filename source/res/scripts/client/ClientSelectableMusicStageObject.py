# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableMusicStageObject.py
from gui.shared.event_dispatcher import showOffspringConcertView
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class ClientSelectableMusicStageObject(ClientSelectableObject):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(ClientSelectableMusicStageObject, self).__init__()
        self.__isVehiclePreviewActive = False

    def onEnterWorld(self, prereqs):
        super(ClientSelectableMusicStageObject, self).onEnterWorld(prereqs)
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        g_eventBus.addListener(VIEW_ALIAS.VEHICLE_PREVIEW_20, self.__onShowVehiclePreview, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(VIEW_ALIAS.LOBBY_HANGAR, self.__onShowLobbyHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def onLeaveWorld(self):
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        g_eventBus.removeListener(VIEW_ALIAS.VEHICLE_PREVIEW_20, self.__onShowVehiclePreview, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(VIEW_ALIAS.LOBBY_HANGAR, self.__onShowLobbyHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        super(ClientSelectableMusicStageObject, self).onLeaveWorld()

    def onMouseClick(self):
        super(ClientSelectableMusicStageObject, self).onMouseClick()
        showOffspringConcertView(self.initialCameraName, self.environmentName)

    def __onCameraEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        entityId = ctx['entityId']
        if state == CameraMovementStates.FROM_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                self.enable(False)
        elif state == CameraMovementStates.ON_OBJECT:
            if self.__isHangarVehicleEntity(entityId):
                if not self.enabled and not self.__isVehiclePreviewActive:
                    self.enable(True)

    def __isHangarVehicleEntity(self, entityId):
        space = self.hangarSpace.space
        return False if space is None else entityId == space.vehicleEntityId

    def __onShowVehiclePreview(self, event):
        isHeroTank = event.ctx.get('isHeroTank', False)
        if isHeroTank:
            return
        self.enable(False)
        self.__isVehiclePreviewActive = True

    def __onShowLobbyHangar(self, _):
        if self.__isVehiclePreviewActive:
            if not self.enabled:
                self.enable(True)
            self.__isVehiclePreviewActive = False

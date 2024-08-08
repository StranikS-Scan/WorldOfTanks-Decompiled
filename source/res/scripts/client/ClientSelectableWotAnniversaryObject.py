# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableWotAnniversaryObject.py
from ClientSelectableObject import ClientSelectableObject
from CurrentVehicle import g_currentPreviewVehicle
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.server_events.events_dispatcher import showMissionsWotAnniversary
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.wot_anniversary import IWotAnniversaryController

class ClientSelectableWotAnniversaryObject(ClientSelectableObject):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)

    def onEnterWorld(self, prereqs):
        super(ClientSelectableWotAnniversaryObject, self).onEnterWorld(prereqs)
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        g_currentPreviewVehicle.onSelected += self.__onPreviewVehicleSelected
        self.__wotAnniversaryCtrl.onSettingsChanged += self.__onSettingsChanged
        self.__wotAnniversaryCtrl.onEventActivePhaseEnded += self.__onSettingsChanged
        self.__onSettingsChanged()

    def onLeaveWorld(self):
        self.__wotAnniversaryCtrl.onSettingsChanged -= self.__onSettingsChanged
        self.__wotAnniversaryCtrl.onEventActivePhaseEnded -= self.__onSettingsChanged
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__onCameraEntityUpdated)
        g_currentPreviewVehicle.onSelected -= self.__onPreviewVehicleSelected
        super(ClientSelectableWotAnniversaryObject, self).onLeaveWorld()

    def onMouseClick(self):
        super(ClientSelectableWotAnniversaryObject, self).onMouseClick()
        showMissionsWotAnniversary()

    def __onSettingsChanged(self, *_):
        if self.__wotAnniversaryCtrl.isAvailableAndActivePhase():
            self.setEnable(True)
        else:
            self.setEnable(False)

    def __onCameraEntityUpdated(self, event):
        if not self.__wotAnniversaryCtrl.isAvailableAndActivePhase():
            return
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
        return entityId == self.__hangarSpace.space.vehicleEntityId

    def __onPreviewVehicleSelected(self):
        if not self.__wotAnniversaryCtrl.isAvailableAndActivePhase():
            return
        else:
            isEnable = g_currentPreviewVehicle.item is None
            if isEnable != self.enabled:
                self.setEnable(isEnable)
            return

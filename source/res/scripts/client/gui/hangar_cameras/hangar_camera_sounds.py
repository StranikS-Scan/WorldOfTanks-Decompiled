# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_sounds.py
import WWISE
from SoundGroups import g_instance as SoundGroupsInstance
from skeletons.gui.hangar_cameras import IHangarCameraSounds
from gui.shared import g_eventBus
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates

class HangarCameraSounds(IHangarCameraSounds):
    hangarSpace = dependency.descriptor(IHangarSpace)

    class _MoveCameraEvents(object):
        MOVE_TO_HERO = 'ue_hangar_generic_camera_fly_forward'
        MOVE_TO_MAIN = 'ue_hangar_generic_camera_fly_backward'

    class _CameraStates(object):
        STATE_NAME = 'STATE_hangar_camera_state_rotate_or_onproposal'
        MAIN_VEHICLE_AND_NOT_IN_IDLE = 'STATE_hangar_camera_state_rotate_or_onproposal_false'
        HERO_VEHICLE_OR_IN_IDLE = 'STATE_hangar_camera_state_rotate_or_onproposal_true'

    class _SelectedVehicleStates(object):
        STATE_NAME = 'STATE_hangar_tank_view'
        HERO_VEHICLE = 'STATE_hangar_tank_view_proposal'
        MAIN_VEHICLE = 'STATE_hangar_tank_view_main'

    def __init__(self):
        super(HangarCameraSounds, self).__init__()
        self.__isMainView = False

    def init(self):
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleEntityUpdated)
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)

    def fini(self):
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleEntityUpdated)
        g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)

    def __handleEntityUpdated(self, event):
        ctx = event.ctx
        state = ctx['state']
        if state == CameraMovementStates.FROM_OBJECT:
            return
        if self.hangarSpace.spaceInited:
            isMainView = ctx['entityId'] == self.hangarSpace.space.vehicleEntityId
        else:
            isMainView = True
        if state == CameraMovementStates.MOVING_TO_OBJECT:
            SoundGroupsInstance.playSound2D(self._MoveCameraEvents.MOVE_TO_MAIN if isMainView else self._MoveCameraEvents.MOVE_TO_HERO)
        if isMainView != self.__isMainView:
            self.__isMainView = isMainView
            WWISE.WW_setState(self._SelectedVehicleStates.STATE_NAME, self._SelectedVehicleStates.MAIN_VEHICLE if self.__isMainView else self._SelectedVehicleStates.HERO_VEHICLE)
            WWISE.WW_setState(self._CameraStates.STATE_NAME, self._CameraStates.MAIN_VEHICLE_AND_NOT_IN_IDLE if self.__isMainView else self._CameraStates.HERO_VEHICLE_OR_IN_IDLE)

    def __handleIdleCameraActivation(self, event):
        if not self.__isMainView:
            return
        WWISE.WW_setState(self._CameraStates.STATE_NAME, self._CameraStates.HERO_VEHICLE_OR_IN_IDLE if event.ctx['started'] else self._CameraStates.MAIN_VEHICLE_AND_NOT_IN_IDLE)

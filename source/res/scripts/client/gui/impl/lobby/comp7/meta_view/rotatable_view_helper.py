# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/rotatable_view_helper.py
import CGF
from enum import Enum
from ClientSelectableCameraObject import ClientSelectableCameraObject
from cgf_components.hangar_camera_manager import HangarCameraManager
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class Comp7Cameras(Enum):
    DEFAULT = 'Tank'
    SHOP = 'Comp7ShopCamera'
    PURCHASE = 'PreShopCameraStart'
    PRE_FLYBY = 'PreStartShopCamera'


class RotatableViewHelper(object):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def getCameraManager(self):
        spaceID = self.__hangarSpace.spaceID
        return CGF.getManager(spaceID, HangarCameraManager) if spaceID is not None else None

    def getCameraEvents(self, viewModel):
        cameraEvents = [(viewModel.onMoveSpace, self.__onMoveSpace), (viewModel.onMouseOver3dScene, self.__onMouseOver3dScene)]
        return cameraEvents

    def switchCamera(self, cameraName, instantly):
        cameraManager = self.getCameraManager()
        if cameraManager is not None and cameraManager.getCurrentCameraName() != cameraName:
            cameraManager.switchByCameraName(cameraName, instantly)
            ClientSelectableCameraObject.deselectAll()
            self.__hangarSpace.space.getVehicleEntity().onSelect(True)
        return

    def resetCamera(self, duration=0):
        cameraManager = self.getCameraManager()
        if cameraManager is not None:
            cameraManager.resetCameraTarget(duration)
        return

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onMouseOver3dScene(args):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': bool(args.get('isOver3dScene'))}))

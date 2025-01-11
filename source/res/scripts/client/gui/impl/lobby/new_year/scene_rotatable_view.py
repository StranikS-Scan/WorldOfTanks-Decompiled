# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/scene_rotatable_view.py
import typing
import CGF
from gui.impl.gen.view_models.views.lobby.new_year.views.base.ny_scene_rotatable_view import NySceneRotatableView
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from cgf_components.hangar_camera_manager import HangarCameraManager
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace

class SceneRotatableView(object):
    __slots__ = ()
    __hangarSpace = dependency.descriptor(IHangarSpace)

    @property
    def viewModel(self):
        pass

    def isMoveSpaceEnable(self, value):
        self.viewModel.setIsMoveSpaceEnable(value)

    def _getEvents(self):
        return ((self.viewModel.onMoveSpace, self.__onMoveSpace), (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene)) if self.viewModel else ()

    def _resetCamera(self, duration=0):
        cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
        if not cameraManager:
            return
        cameraManager.resetCameraTarget(duration)

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

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/collage_view.py
import typing
from AvatarInputHandler.cameras import FovExtended
from cgf_components.hangar_camera_manager import HangarCameraManager
from frameworks.wulf import ViewFlags, ViewSettings
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import LobbySimpleEvent
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.collage_view_model import CollageViewModel

class CollageView(ViewImpl):
    __slots__ = ('__cachedEvent', '__currentFov', '__defaultFov', '__showHangar')
    _FOV_MAX = 61.5
    _FOV_MIN = 50
    _FOV_STEP = 5
    _SCROLL_DZ_VALUE = 600
    _FOV_ANIM = 0.2

    def __init__(self, layoutId=R.views.mt_birthday.lobby.birthday.CollageView()):
        settings = ViewSettings(layoutId)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CollageViewModel()
        self.__cachedEvent = None
        self.__currentFov = self._FOV_MAX
        self.__defaultFov = FovExtended.instance().horizontalFov
        self.__showHangar = False
        super(CollageView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CollageView, self).getViewModel()

    def _finalize(self):
        cameraMGR = HangarCameraManager.getCameraMgrForCurrentSpace()
        if cameraMGR:
            FovExtended.instance().horizontalFov = self.__defaultFov
            cameraMGR.switchToTank()
        if self.__showHangar:
            showHangar()
        super(CollageView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onStartMoving, self.__onStartMoving),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onStartFadeInAnim, self.__onStartFadeInAnim))

    def __onStartFadeInAnim(self):
        cameraManager = HangarCameraManager.getCameraMgrForCurrentSpace()
        if cameraManager:
            cameraManager.switchByCameraName('Easter_egg', True)
            fovExtended = FovExtended.instance()
            fovExtended.horizontalFov = self.__currentFov
            fovExtended.setFovByAbsoluteValue(self.__currentFov)

    def __onStartMoving(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            scrollValue = args.get('dz')
            if self.__cachedEvent is None:
                self.__cachedEvent = CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': args.get('dx'),
                 'dy': args.get('dy'),
                 'dz': args.get('dz')})
            else:
                ctx = self.__cachedEvent.ctx
                ctx['dx'] = -args.get('dx')
                ctx['dy'] = args.get('dy')
                ctx['dz'] = args.get('dz')
            g_eventBus.handleEvent(self.__cachedEvent, EVENT_BUS_SCOPE.GLOBAL)
            if scrollValue:
                direction = -scrollValue / self._SCROLL_DZ_VALUE
                self.__updateFov(direction)
            return

    def __updateFov(self, direction):
        newValue = self.__currentFov + direction * self._FOV_STEP
        newValue = max(min(newValue, self._FOV_MAX), self._FOV_MIN)
        if newValue != self.__currentFov:
            self.__currentFov = newValue
            FovExtended.instance().setFovByAbsoluteValue(self.__currentFov, self._FOV_ANIM)

    def __onClose(self):
        self.__showHangar = True
        self.destroy()

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/selectable_view_impl.py
import logging
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from gui.impl.pub import ViewImpl
from skeletons.gui.shared.utils import IHangarSpace
from hangar_selectable_objects import ISelectableLogicCallback, HangarSelectableLogic
from gui.impl.gen.view_models.views.selectable_view_model import SelectableViewModel
_logger = logging.getLogger(__name__)

def moveCamera(dx, dy, dz):
    g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
     'dy': dy,
     'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
    g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
     'dy': dy,
     'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)


def notifyCursorOver3DScene(isOver3DScene):
    g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3DScene}), EVENT_BUS_SCOPE.DEFAULT)


class SelectableViewImpl(ViewImpl, ISelectableLogicCallback):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, settings):
        super(SelectableViewImpl, self).__init__(settings)
        self.__selectableLogic = None
        return

    @property
    def viewModel(self):
        return super(SelectableViewImpl, self).getViewModel()

    def onHighlight3DEntity(self, entity):
        self._highlight3DEntityAndShowTT(entity)

    def onFade3DEntity(self, entity):
        self._fade3DEntityAndHideTT(entity)

    def _onLoading(self, *args, **kwargs):
        super(SelectableViewImpl, self)._onLoading(*args, **kwargs)
        self._activateSelectableLogic()

    def _finalize(self):
        super(SelectableViewImpl, self)._finalize()
        self._deactivateSelectableLogic()

    def _subscribe(self):
        super(SelectableViewImpl, self)._subscribe()
        self.viewModel.onMoveSpace += self._onMoveSpace
        self.viewModel.onOverScene += self._onCursorOver3DScene

    def _unsubscribe(self):
        super(SelectableViewImpl, self)._unsubscribe()
        self.viewModel.onMoveSpace -= self._onMoveSpace
        self.viewModel.onOverScene -= self._onCursorOver3DScene

    def _highlight3DEntityAndShowTT(self, entity):
        pass

    def _fade3DEntityAndHideTT(self, entity):
        pass

    def _activateSelectableLogic(self):
        if self.__selectableLogic is not None:
            return
        else:
            self.__selectableLogic = self._createSelectableLogic()
            self.__selectableLogic.init(self)
            return

    def _deactivateSelectableLogic(self):
        if self.__selectableLogic is not None:
            self.__selectableLogic.fini()
            self.__selectableLogic = None
        return

    def _createSelectableLogic(self):
        return HangarSelectableLogic()

    def _onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            moveCamera(dx, dy, dz)
            return

    def _onCursorOver3DScene(self, args=None):
        if args is None:
            _logger.error("Can't notified cursor over changed. args=None. Please fix JS")
            return
        else:
            notifyCursorOver3DScene(args.get('isOver3dScene', False))
            return

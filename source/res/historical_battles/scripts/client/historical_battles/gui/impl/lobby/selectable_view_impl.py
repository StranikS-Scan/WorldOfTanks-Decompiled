# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/selectable_view_impl.py
import logging
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import notifyCursorOver3DScene
_logger = logging.getLogger(__name__)

class SelectableViewImpl(ViewImpl):

    @property
    def viewModel(self):
        return super(SelectableViewImpl, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SelectableViewImpl, self)._onLoading(*args, **kwargs)
        self.viewModel.onMoveSpace += self.__onMoveSpace
        self.viewModel.onOverScene += self.__onCursorOver3DScene

    def _finalize(self):
        self.viewModel.onMoveSpace -= self.__onMoveSpace
        self.viewModel.onOverScene -= self.__onCursorOver3DScene
        super(SelectableViewImpl, self)._finalize()

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            return

    def __onCursorOver3DScene(self, args=None):
        if args is None:
            _logger.error('Args=None. JS should notify about cursor position by isOver3dScene param. Please fix JS')
            return
        else:
            notifyCursorOver3DScene(args.get('isOver3dScene', False))
            return

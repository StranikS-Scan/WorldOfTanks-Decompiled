# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/space_interaction_presenter.py
from __future__ import absolute_import
import logging
import typing
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.space_interaction_model import SpaceInteractionModel
from gui.impl.pub.view_component import ViewComponent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
if typing.TYPE_CHECKING:
    from hangar_selectable_objects.interfaces import ISelectableLogic
_logger = logging.getLogger(__name__)

class SpaceInteractionPresenter(ViewComponent[SpaceInteractionModel]):

    def __init__(self, selectableLogic):
        super(SpaceInteractionPresenter, self).__init__(model=SpaceInteractionModel)
        self._selectableLogic = selectableLogic

    @property
    def viewModel(self):
        return super(SpaceInteractionPresenter, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onMoveSpace, self._onMoveSpace), (self.viewModel.onMouseOver3dScene, self._onCursorOver3DScene))

    def onHighlight3DEntity(self, entity):
        self._highlight3DEntityAndShowTT(entity)

    def onFade3DEntity(self, entity):
        self._fade3DEntityAndHideTT(entity)

    def _onLoading(self, *args, **kwargs):
        super(SpaceInteractionPresenter, self)._onLoading(*args, **kwargs)
        self._selectableLogic.init(self)

    def _finalize(self):
        super(SpaceInteractionPresenter, self)._finalize()
        if self._selectableLogic is not None:
            self._selectableLogic.fini()
            self._selectableLogic = None
        return

    def _highlight3DEntityAndShowTT(self, entity):
        pass

    def _fade3DEntityAndHideTT(self, entity):
        pass

    def _onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=args), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=args), EVENT_BUS_SCOPE.GLOBAL)
            return

    def _onCursorOver3DScene(self, args=None):
        if args is None:
            _logger.error("Can't notified cursor over changed. args=None. Please fix JS")
            return
        else:
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx=args), EVENT_BUS_SCOPE.DEFAULT)
            return

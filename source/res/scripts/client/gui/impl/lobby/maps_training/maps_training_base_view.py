# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_training/maps_training_base_view.py
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from frameworks.wulf import ViewSettings, ViewFlags
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class MapsTrainingBaseView(ViewImpl, LobbyHeaderVisibility):
    appLoader = dependency.descriptor(IAppLoader)
    _BACKGROUND_ALPHA = 0

    def __init__(self, viewResource, viewModel, *args, **kwargs):
        settings = ViewSettings(viewResource)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = viewModel
        settings.args = args
        settings.kwargs = kwargs
        super(MapsTrainingBaseView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MapsTrainingBaseView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(MapsTrainingBaseView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)
        app = self.appLoader.getApp()
        app.setBackgroundAlpha(self._BACKGROUND_ALPHA)

    def _onLoading(self, *args, **kwargs):
        super(MapsTrainingBaseView, self)._onLoading(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        self.resumeLobbyHeader(self.uniqueID)
        super(MapsTrainingBaseView, self)._finalize()

    def _addListeners(self):
        self.viewModel.onMoveSpace += self._onMoveSpace

    def _removeListeners(self):
        self.viewModel.onMoveSpace -= self._onMoveSpace

    def _onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            ctx = {'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            return

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/maps_training/maps_training_base_view.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.pub import ViewImpl
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from frameworks.wulf import ViewSettings, ViewFlags
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader

class MapsTrainingBaseView(ViewImpl):
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
        self._hideMenu()
        app = self.appLoader.getApp()
        app.setBackgroundAlpha(self._BACKGROUND_ALPHA)

    def _onLoading(self, *args, **kwargs):
        super(MapsTrainingBaseView, self)._onLoading(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        if not self._isInCustomization():
            self._showMenu()
        super(MapsTrainingBaseView, self)._finalize()

    def _addListeners(self):
        self.viewModel.onMoveSpace += self._onMoveSpace

    def _removeListeners(self):
        self.viewModel.onMoveSpace -= self._onMoveSpace

    def _hideMenu(self):
        from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _showMenu(self):
        from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)

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

    def _isInCustomization(self):
        app = self.appLoader.getApp()
        return app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION)) is not None

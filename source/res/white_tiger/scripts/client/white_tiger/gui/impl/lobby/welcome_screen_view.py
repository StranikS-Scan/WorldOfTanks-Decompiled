# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/welcome_screen_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.welcome_screen_view_model import WelcomeScreenViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared import g_eventBus, events
from gui.shared.event_dispatcher import showBrowserOverlayView
from white_tiger.gui.wt_event_helpers import getIntroVideoURL

class WelcomeScreenView(ViewImpl):
    LAYOUT_ID = R.views.white_tiger.mono.lobby.welcome_screen()

    def __init__(self, layoutID=LAYOUT_ID, *args, **kwargs):
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, WelcomeScreenViewModel(), *args, **kwargs)
        super(WelcomeScreenView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WelcomeScreenView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose), (self.viewModel.onVideoPlay, self._onVideoPlay), (self.viewModel.onViewLoaded, self._onViewLoaded))

    def _onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def _onClose(self):
        self.destroyWindow()

    def _onVideoPlay(self):
        showBrowserOverlayView(getIntroVideoURL(), alias=VIEW_ALIAS.BROWSER_OVERLAY)


class WelcomeScreenViewWindow(WindowImpl):

    def __init__(self, parent=None):
        super(WelcomeScreenViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WelcomeScreenView(), parent=parent)

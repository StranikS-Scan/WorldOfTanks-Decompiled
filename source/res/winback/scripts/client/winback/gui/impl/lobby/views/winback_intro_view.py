# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/winback_intro_view.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from helpers import dependency
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import toggleMenuVisibility, HeaderMenuVisibilityState
from skeletons.gui.game_control import IWinbackController
from winback.gui.impl.gen.view_models.views.lobby.views.winback_intro_view_model import WinbackIntroViewModel

class WinbackIntroView(ViewImpl):
    __slots__ = ()
    __winbackController = dependency.descriptor(IWinbackController)

    def __init__(self):
        settings = ViewSettings(R.views.winback.lobby.WinbackIntroView())
        settings.model = WinbackIntroViewModel()
        super(WinbackIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WinbackIntroView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self):
        self.destroyWindow()

    def _initialize(self):
        toggleMenuVisibility(HeaderMenuVisibilityState.NOTHING)

    def _finalize(self):
        toggleMenuVisibility(HeaderMenuVisibilityState.ALL)


class WinbackIntroViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WinbackIntroViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackIntroView(), parent=parent, layer=WindowLayer.OVERLAY)

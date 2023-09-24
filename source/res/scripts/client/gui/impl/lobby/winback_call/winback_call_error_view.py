# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback_call/winback_call_error_view.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_error_view_model import WinbackCallErrorViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showHangar
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IWinBackCallController
if typing.TYPE_CHECKING:
    from typing import Optional

class WinbackCallErrorView(ViewImpl):
    __slots__ = ('__holderWindow', '__blur')
    __winBackCallCtrl = dependency.descriptor(IWinBackCallController)

    def __init__(self, blurLayer, holderWindow=None):
        settings = ViewSettings(R.views.lobby.winback_call.WinbackCallErrorView())
        settings.flags = ViewFlags.VIEW
        settings.model = WinbackCallErrorViewModel()
        self.__holderWindow = holderWindow
        self.__blur = CachedBlur(enabled=True, ownLayer=blurLayer, blurAnimRepeatCount=1)
        super(WinbackCallErrorView, self).__init__(settings)

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        if self.__holderWindow:
            self.__holderWindow = None
        super(WinbackCallErrorView, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(WinbackCallErrorView, self).getViewModel()

    def _getEvents(self):
        events = super(WinbackCallErrorView, self)._getEvents()
        return events + ((self.viewModel.onClose, self.__onClose), (self.__winBackCallCtrl.onStateChanged, self.__onStateChanged))

    def __onStateChanged(self):
        if not self.__winBackCallCtrl.isEnabled:
            self.__onClose()

    def __onClose(self):
        if self.__holderWindow is not None:
            self.__holderWindow.destroy()
        else:
            self.destroyWindow()
        showHangar()
        return


class WinbackCallErrorViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        layer = WindowLayer.FULLSCREEN_WINDOW
        blurLayer = parent.layer if parent else layer - 1
        super(WinbackCallErrorViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackCallErrorView(blurLayer, holderWindow=parent), parent=parent, layer=layer)

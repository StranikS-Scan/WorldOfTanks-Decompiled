# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/telecom/telecom_view.py
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.telecom.telecom_view_model import TelecomViewModel
from frameworks.wulf import ViewSettings, WindowFlags

class TelecomView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.telecom.TelecomView())
        settings.model = TelecomViewModel()
        super(TelecomView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TelecomView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__close),)

    def __close(self):
        self.destroyWindow()


class TelecomViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(TelecomViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TelecomView(), parent=parent)

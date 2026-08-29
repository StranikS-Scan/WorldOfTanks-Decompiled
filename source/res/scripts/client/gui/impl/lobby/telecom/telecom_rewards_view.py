# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/telecom/telecom_rewards_view.py
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.telecom.telecom_rewards_view_model import TelecomRewardsViewModel
from frameworks.wulf import ViewSettings, WindowFlags

class TelecomRewardsView(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.telecom.TelecomRewardsView())
        settings.model = TelecomRewardsViewModel()
        super(TelecomRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TelecomRewardsView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__close),)

    def __close(self):
        self.destroyWindow()


class TelecomRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(TelecomRewardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TelecomRewardsView(), parent=parent)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/birthday2023/birthday_intro_view.py
from frameworks.wulf import ViewSettings, WindowLayer, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.birthday2023.birthday2023_intro_view_model import Birthday2023IntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.pub.notification_commands import NotificationCommand
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BIRTHDAY_2023_INTRO_SHOWN

class BirthdayIntro2023View(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.birthday2023.BirthdayIntroScreen())
        settings.model = Birthday2023IntroViewModel()
        super(BirthdayIntro2023View, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(BirthdayIntro2023View, self)._onLoading(*args, **kwargs)
        AccountSettings.setSettings(BIRTHDAY_2023_INTRO_SHOWN, True)

    @property
    def viewModel(self):
        return super(BirthdayIntro2023View, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__close),)

    def __close(self):
        self.destroyWindow()


class BirthdayIntro2023Window(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self):
        super(BirthdayIntro2023Window, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.OVERLAY, content=BirthdayIntro2023View())

    def __eq__(self, other):
        return isinstance(other.getWindow(), BirthdayIntro2023Window) if isinstance(other, NotificationCommand) else False

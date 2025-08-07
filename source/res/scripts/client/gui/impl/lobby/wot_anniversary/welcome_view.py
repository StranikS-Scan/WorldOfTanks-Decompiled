# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/welcome_view.py
import logging
import SoundGroups
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.welcome_view_model import WelcomeViewModel
from gui.impl.lobby.wot_anniversary.sound_helper import SOUNDS
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from helpers import dependency
from skeletons.gui.wot_anniversary import IWotAnniversaryController
_logger = logging.getLogger(__name__)

class WelcomeView(ViewImpl):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.WelcomeView(), model=WelcomeViewModel(), args=args, kwargs=kwargs)
        super(WelcomeView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.__wotAnniversaryController.onSettingsChanged, self.__onSettingsChanged), (self.__wotAnniversaryController.onEndDateReached, self.__onEndDateReached))

    def _onLoading(self, *args, **kwargs):
        super(WelcomeView, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _initialize(self, *args, **kwargs):
        super(WelcomeView, self)._initialize(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(SOUNDS.WELCOME_VIEW_ENTER_EVENT)

    def __onClose(self):
        self.destroyWindow()

    def __updateModel(self):
        config = self.__wotAnniversaryController.config
        with self.viewModel.transaction() as tx:
            tx.setStartDate(config.startDate)
            tx.setEndDate(config.endDate)

    def __onSettingsChanged(self):
        if self.__wotAnniversaryController.isEnabled():
            self.__updateModel()
        else:
            self.destroyWindow()

    def __onEndDateReached(self):
        self.destroyWindow()


class WelcomeWindow(LobbyNotificationWindow):

    def __init__(self, parent=None, **kwargs):
        super(WelcomeWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=WelcomeView(**kwargs), parent=parent)

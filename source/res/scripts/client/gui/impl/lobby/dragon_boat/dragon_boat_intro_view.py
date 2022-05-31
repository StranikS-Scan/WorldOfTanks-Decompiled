# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dragon_boat/dragon_boat_intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dragon_boat.dragon_boat_intro_view_model import DragonBoatIntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class DragonBoatIntroView(ViewImpl):
    __slots__ = ('__closeCallback',)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, closeCallback=None):
        settings = ViewSettings(R.views.lobby.dragon_boats.IntroScreen())
        settings.flags = ViewFlags.VIEW
        settings.model = DragonBoatIntroViewModel()
        self.__closeCallback = closeCallback
        super(DragonBoatIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DragonBoatIntroView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self.__onClose
        self.viewModel.onAccept += self.__onClose

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onAccept -= self.__onClose

    def __onClose(self):
        self.destroyWindow()
        if self.__closeCallback is not None:
            self.__closeCallback()
        return


class DragonBoatIntroWindow(LobbyWindow):

    def __init__(self, parent=None, closeCallback=None):
        super(DragonBoatIntroWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.OVERLAY, content=DragonBoatIntroView(closeCallback), parent=parent)

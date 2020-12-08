# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/snow_maidens_intro_view.py
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.snow_maidens.snow_maidens_intro_view_model import SnowMaidensIntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.new_year import ITalismanSceneController

class SnowMaidensIntroView(ViewImpl):
    __talismanCtrl = dependency.descriptor(ITalismanSceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.SnowMaidensIntroView())
        settings.model = SnowMaidensIntroViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SnowMaidensIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SnowMaidensIntroView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SnowMaidensIntroView, self)._initialize()
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.IS_TALISMAN_INTRO_SHOWED: True})
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        super(SnowMaidensIntroView, self)._finalize()

    def __onCloseBtnClick(self):
        self.__talismanCtrl.switchToPreview()
        self.destroyWindow()


class SnowMaidensIntroWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(SnowMaidensIntroWindow, self).__init__(content=SnowMaidensIntroView(), layer=WindowLayer.TOP_WINDOW)

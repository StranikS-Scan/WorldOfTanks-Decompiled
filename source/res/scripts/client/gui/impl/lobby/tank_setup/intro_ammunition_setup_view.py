# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/intro_ammunition_setup_view.py
import logging
from BWUtil import AsyncReturn
import async
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.intro_ammunition_setup_view_model import IntroAmmunitionSetupViewModel
from gui.impl.lobby.tank_setup.tank_setup_sounds import playEnterTankSetupView, playExitTankSetupView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)

class IntroAmmunitionSetupView(ViewImpl):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _guiLoader = dependency.descriptor(IGuiLoader)
    __slots__ = ('__closeCallback', '__hasTankSetupView')

    def __init__(self, closeCallback):
        settings = ViewSettings(R.views.lobby.tanksetup.IntroScreen())
        settings.model = IntroAmmunitionSetupViewModel()
        super(IntroAmmunitionSetupView, self).__init__(settings)
        self.__closeCallback = closeCallback
        self.__hasTankSetupView = self._guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.tanksetup.HangarAmmunitionSetup())
        self._settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.OPTIONAL_DEVICE_SETUP_INTRO_SHOWN: True})

    @property
    def viewModel(self):
        return super(IntroAmmunitionSetupView, self).getViewModel()

    def destroy(self):
        self.__invokeCloseCallback()
        super(IntroAmmunitionSetupView, self).destroy()

    def _initialize(self, *args, **kwargs):
        super(IntroAmmunitionSetupView, self)._initialize()
        if not self.__hasTankSetupView:
            playEnterTankSetupView()
        self.viewModel.onClose += self.__onClose

    def _finalize(self):
        if not self.__hasTankSetupView:
            playExitTankSetupView()
        self.viewModel.onClose -= self.__onClose
        super(IntroAmmunitionSetupView, self)._finalize()

    def __invokeCloseCallback(self):
        if self.__closeCallback is not None:
            closeCallback, self.__closeCallback = self.__closeCallback, None
            closeCallback(None)
        return

    def __onClose(self):
        self.__invokeCloseCallback()
        self.destroyWindow()


class IntroAmmunitionSetupWindow(LobbyWindow):

    def __init__(self, callback=None, parent=None):
        super(IntroAmmunitionSetupWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, decorator=None, content=IntroAmmunitionSetupView(callback), parent=parent)
        return


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def isIntroAmmunitionSetupShown(settingsCore=None):
    return settingsCore.serverSettings.getUIStorage().get(UI_STORAGE_KEYS.OPTIONAL_DEVICE_SETUP_INTRO_SHOWN)


@async.async
def showIntroAmmunitionSetupWindow():

    def _loadIntroAmmunitonSetupWindow(callback):
        window = IntroAmmunitionSetupWindow(callback)
        window.load()

    yield async.await_callback(_loadIntroAmmunitonSetupWindow)()
    raise AsyncReturn(None)
    return

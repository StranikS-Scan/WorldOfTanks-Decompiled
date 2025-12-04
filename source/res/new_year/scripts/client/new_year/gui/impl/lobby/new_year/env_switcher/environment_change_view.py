# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/env_switcher/environment_change_view.py
import SoundGroups
from PlayerEvents import g_playerEvents
from helpers import dependency
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.environment_change_view_model import EnvironmentChangeViewModel
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from new_year.gui.impl.new_year.sounds import EnvSwitcherAnimSounds
from new_year.skeletons.new_year import INewYearEnvironmentSwitchController

class EnvironmentChangeView(ViewImpl):
    __slots__ = ('__envState',)
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)

    def __init__(self, envState):
        settings = ViewSettings(R.views.new_year.lobby.new_year.EnvironmentChangeView())
        settings.flags = ViewFlags.VIEW
        settings.model = EnvironmentChangeViewModel()
        self.__envState = envState
        super(EnvironmentChangeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EnvironmentChangeView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.viewModel.setSwitchTo(self.__nyEnvSwitcherController.resolveDayNightMode(self.__envState))
        super(EnvironmentChangeView, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return ((self.viewModel.onAnimationFinished, self.__onAnimationFinished),
         (self.viewModel.onAnimationFadeFinished, self.__onAnimationFadeFinished),
         (self.__nyEnvSwitcherController.onEnvironmentSwitched, self.__onEnvironmentSwitched),
         (g_playerEvents.onDisconnected, self.destroyWindow))

    def __onAnimationFinished(self):
        self.__nyEnvSwitcherController.switchEnvironment(self.__envState.value)

    def __onEnvironmentSwitched(self):
        with self.viewModel.transaction() as model:
            model.setIsEnvironmentSwitched(True)

    def __onAnimationFadeFinished(self):
        self.destroyWindow()

    def _finalize(self):
        self.__envState = None
        SoundGroups.g_instance.setState(EnvSwitcherAnimSounds.GROUP, EnvSwitcherAnimSounds.OFF)
        super(EnvironmentChangeView, self)._finalize()
        return


class EnvironmentChangeViewWindow(WindowImpl):

    def __init__(self, envState, parent=None):
        super(EnvironmentChangeViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EnvironmentChangeView(envState), parent=parent)

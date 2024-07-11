# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/battle/races_hud/races_help_window.py
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
from gui.app_loader.settings import APP_NAME_SPACE
from helpers import dependency
from races.gui.impl.gen.view_models.views.battle.races_hud.races_f1_helper_view_model import RacesF1HelperViewModel
from account_helpers.AccountSettings import RACES_F1_HELPER_SHOWN
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from races.gui.shared.event import RacesEvent
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IRacesBattleController

class RacesBattleHelpView(ViewImpl, BattleGUIKeyHandler):
    __slots__ = ('__closeCallback',)
    __appLoader = dependency.descriptor(IAppLoader)
    __racesCtrl = dependency.descriptor(IRacesBattleController)

    def __init__(self, layoutID=R.views.races.battle.races_hud.RacesF1HelperView(), closeCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = RacesF1HelperViewModel()
        self.__closeCallback = closeCallback
        super(RacesBattleHelpView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RacesBattleHelpView, self).getViewModel()

    @property
    def _battleApp(self):
        return self.__appLoader.getApp(APP_NAME_SPACE.SF_BATTLE)

    def _onLoading(self, *args, **kwargs):
        super(RacesBattleHelpView, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(RacesEvent(RacesEvent.ON_OPEN_F1_HELP), scope=EVENT_BUS_SCOPE.BATTLE)

    def _subscribe(self):
        super(RacesBattleHelpView, self)._subscribe()
        battleApp = self._battleApp
        if battleApp:
            battleApp.registerGuiKeyHandler(self)

    def _unsubscribe(self):
        super(RacesBattleHelpView, self)._unsubscribe()
        battleApp = self._battleApp
        if battleApp:
            battleApp.unregisterGuiKeyHandler(self)

    def _finalize(self):
        self.__racesCtrl.setRacesAccountSettings(RACES_F1_HELPER_SHOWN, True)
        if self.__closeCallback is not None:
            self.__closeCallback()
        super(RacesBattleHelpView, self)._finalize()
        return

    def handleEscKey(self, isDown):
        self.destroyWindow()
        return True


class RacesHelpWindow(WindowImpl):

    def __init__(self, closeCallback=None):
        super(RacesHelpWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RacesBattleHelpView(closeCallback=closeCallback))

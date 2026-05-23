# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/intro_view.py
from __future__ import absolute_import
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import WindowFlags, ViewSettings
from gui.battle_pass.battle_pass_helpers import getIntroSlidesNames
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_intro_view_model import BattlePassIntroViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController

class IntroPresenter(ViewImpl):
    __battlePass = dependency.descriptor(IBattlePassController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.battle_pass.intro())
        settings.model = BattlePassIntroViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__callback = None
        super(IntroPresenter, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(IntroPresenter, self).getViewModel()

    def _onLoading(self, callback, *args, **kwargs):
        super(IntroPresenter, self)._onLoading(*args, **kwargs)
        self.__callback = callback
        self.__updateViewModel()
        self.__setIntroShown()

    def _finalize(self):
        if callable(self.__callback):
            self.__callback()
            self.__callback = None
        super(IntroPresenter, self)._finalize()
        return

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            slides = tx.getSlides()
            for slideName in getIntroSlidesNames():
                slides.addString(slideName)

    def __setIntroShown(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})


class IntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, callback=None, parent=None):
        super(IntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=IntroPresenter(callback=callback), parent=parent)

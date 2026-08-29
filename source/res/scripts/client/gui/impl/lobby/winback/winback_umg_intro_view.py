# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_umg_intro_view.py
from frameworks.wulf import WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback.winback_umg_intro_view_model import WinbackUmgIntroViewModel
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.pub.view_component import ViewComponent
from gui.shared.system_factory import collectDynamicUmgWinbackPresenters
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class WinbackUmgIntroView(ViewComponent[WinbackUmgIntroViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        super(WinbackUmgIntroView, self).__init__(layoutID=R.views.mono.winback.winback_umg_intro_view(), model=WinbackUmgIntroViewModel)

    @property
    def viewModel(self):
        return super(WinbackUmgIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WinbackUmgIntroView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.__battlePass.onBattlePassSettingsChange, self.__update))

    def _getChildComponents(self):
        return collectDynamicUmgWinbackPresenters()

    def __update(self, *_):
        self.viewModel.setHasBattlePass(self.__battlePass.isActive())

    def __onClose(self):
        self.destroyWindow()


class WinbackUmgIntroWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(WinbackUmgIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackUmgIntroView(), parent=parent)

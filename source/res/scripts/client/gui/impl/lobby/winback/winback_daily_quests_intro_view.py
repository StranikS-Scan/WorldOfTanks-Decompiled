# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_daily_quests_intro_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen.view_models.views.lobby.winback.winback_daily_quests_intro_view_model import WinbackDailyQuestsIntroViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController

class WinbackDailyQuestsIntroView(ViewImpl):
    __slots__ = ()
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.winback.WinbackDailyQuestsIntroView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = WinbackDailyQuestsIntroViewModel()
        super(WinbackDailyQuestsIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WinbackDailyQuestsIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WinbackDailyQuestsIntroView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.__battlePass.onBattlePassSettingsChange, self.__update))

    def __update(self, *_):
        self.viewModel.setHasBattlePass(self.__battlePass.isActive())

    def __onClose(self):
        self.destroyWindow()


class WinbackDailyQuestsIntroWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WinbackDailyQuestsIntroWindow, self).__init__(WindowFlags.WINDOW, content=WinbackDailyQuestsIntroView(), parent=parent, layer=WindowLayer.TOP_SUB_VIEW)

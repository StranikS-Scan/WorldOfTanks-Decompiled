# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/progression_main_view.py
import typing
from battle_royale_progression.gui.impl.gen.view_models.views.lobby.views.progression.progression_main_view_model import ProgressionMainViewModel, MainViews
from battle_royale_progression.gui.impl.lobby.views.progression_view import ProgressionView
from battle_royale_progression.gui.sounds_constants import GENERAL_SOUND_SPACE
from battle_royale.gui.impl.lobby.tooltips.leaderboard_reward_tooltip_view import LeaderboardRewardTooltipView
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
if typing.TYPE_CHECKING:
    from typing import Dict

class ProgressionMainView(ViewImpl):
    _COMMON_SOUND_SPACE = GENERAL_SOUND_SPACE

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.battle_royale_progression.ProgressionMainView())
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ProgressionMainViewModel()
        self.__viewType = None
        self.__ctx = kwargs.get('ctx', {})
        self.__contentPresentersMap = {}
        super(ProgressionMainView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(ProgressionMainView, self).getViewModel()

    @property
    def currentPresenter(self):
        if self.__viewType not in self.__contentPresentersMap.keys():
            self.__contentPresentersMap[self.__viewType] = self.__loadersMap[self.__viewType]()
        return self.__contentPresentersMap[self.__viewType]

    def createToolTipContent(self, event, contentID):
        return LeaderboardRewardTooltipView() if contentID == R.views.battle_royale.lobby.tooltips.LeaderboardRewardTooltipView() else self.currentPresenter.createToolTipContent(event, contentID) or super(ProgressionMainView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        return self.currentPresenter.createToolTip(event) or super(ProgressionMainView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(ProgressionMainView, self)._onLoading(args, kwargs)
        self.switchSubView(self.__ctx.get('menuName'))

    def _finalize(self):
        if self.__viewType is not None:
            self.currentPresenter.finalize()
        for presenter in self.__contentPresentersMap.itervalues():
            presenter.clear()

        self.__contentPresentersMap = None
        self.__ctx = None
        super(ProgressionMainView, self)._finalize()
        return

    def switchSubView(self, menuName):
        if self.__viewType and self.currentPresenter.isLoaded:
            self.currentPresenter.finalize()
        if not menuName:
            menuName = MainViews.PROGRESSION
        self.__viewType = menuName
        with self.viewModel.transaction() as tx:
            self.currentPresenter.initialize(**self.__ctx)
            tx.setViewType(self.__viewType)

    @property
    def __loadersMap(self):
        return {MainViews.PROGRESSION: self.loadProgression}

    def loadProgression(self):
        return ProgressionView(self.viewModel.progressionModel, self)


class ProgressionViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(ProgressionViewWindow, self).__init__(content=ProgressionMainView(), wndFlags=WindowFlags.WINDOW, decorator=None, parent=parent)
        return

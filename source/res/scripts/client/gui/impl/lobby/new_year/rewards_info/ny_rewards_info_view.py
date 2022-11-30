# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/rewards_info/ny_rewards_info_view.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.rewards_info.level_reward_presenter import LevelRewardPresenter
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundStates
from new_year.ny_level_helper import getLevelIndexes
if typing.TYPE_CHECKING:
    from typing import List
    from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_levels_rewards_model import NyLevelsRewardsModel

class NyRewardsInfoView(NyHistoryPresenter):
    __slots__ = ('__levels',)

    def __init__(self, viewModel, parentView):
        super(NyRewardsInfoView, self).__init__(viewModel, parentView, soundConfig={NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.REWARDS_LEVELS})
        self.__levels = []

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            toolTipData = None
            tooltipId = event.getArgument('tooltipId')
            idx = event.getArgument('idx')
            if idx is not None:
                toolTipData = self.__levels[int(idx)].createToolTipData(tooltipId)
            if not toolTipData:
                return
            window = backport.BackportTooltipWindow(toolTipData, self.parentView.getParentWindow())
            window.load()
            return window
        else:
            return super(NyRewardsInfoView, self).createToolTip(event)

    def createToolTipContent(self, event, ctID):
        toolTipContent = None
        idx = event.getArgument('idx')
        if idx is not None:
            toolTipContent = self.__levels[int(idx)].createToolTipContent(event, ctID)
        return toolTipContent

    def initialize(self, *args, **kwargs):
        super(NyRewardsInfoView, self).initialize(*args, **kwargs)
        self.__createData()

    def finalize(self):
        while self.__levels:
            self.__levels.pop().clear()

        super(NyRewardsInfoView, self).finalize()

    def _getEvents(self):
        return ((self._nyController.onDataUpdated, self.__onDataUpdated),)

    def __onDataUpdated(self, *_):
        self.__updateData()

    def __createData(self):
        for index, level in enumerate(getLevelIndexes()):
            self.__levels.append(LevelRewardPresenter(index, level))

        with self.viewModel.transaction() as tx:
            renderers = tx.rewardRenderers.getItems()
            renderers.clear()
            for levelPresenter in self.__levels:
                renderer = levelPresenter.getRenderer()
                renderers.addViewModel(renderer)

            renderers.invalidate()

    def __updateData(self):
        with self.viewModel.transaction() as tx:
            renderers = tx.rewardRenderers.getItems()
            for idx, renderer in enumerate(renderers):
                self.__levels[idx].updateRenderer(renderer)

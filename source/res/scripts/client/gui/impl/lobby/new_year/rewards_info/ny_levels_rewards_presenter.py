# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/rewards_info/ny_levels_rewards_presenter.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.new_year.rewards_info.level_reward_presenter import LevelRewardPresenter
from gui.impl.lobby.new_year.rewards_info.rewards_sub_model_presenter import RewardsSubModelPresenter
from gui.impl.new_year.sounds import NewYearSoundStates, NewYearSoundConfigKeys
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from helpers import dependency
from new_year.ny_level_helper import getLevelIndexes
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_levels_rewards_model import NyLevelsRewardsModel

class NyLevelsRewardsPresenter(RewardsSubModelPresenter):
    __slots__ = ('__levels',)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, viewModel, parentView):
        soundConfig = {NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.REWARDS_LEVELS}
        super(NyLevelsRewardsPresenter, self).__init__(viewModel, parentView, soundConfig)
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
            if toolTipData is None:
                return
            window = backport.BackportTooltipWindow(toolTipData, self.parentView.getParentWindow())
            window.load()
            return window
        else:
            return super(NyLevelsRewardsPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        else:
            toolTipContent = None
            idx = event.getArgument('idx')
            if idx is not None:
                toolTipContent = self.__levels[int(idx)].createToolTipContent(event, ctID)
            return toolTipContent

    def initialize(self, *args, **kwargs):
        self.__nyController.onDataUpdated += self.__onDataUpdated
        self.__createData()
        super(NyLevelsRewardsPresenter, self).initialize(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.__updateData()

    def finalize(self):
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        while self.__levels:
            self.__levels.pop().clear()

        super(NyLevelsRewardsPresenter, self).finalize()

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

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/rewards_info/ny_levels_rewards_presenter.py
import typing
from new_year_common.items import new_year
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from new_year.gui.impl.lobby.new_year.rewards_info.level_reward_presenter import LevelRewardPresenter
from new_year.gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from new_year.gui.impl.new_year.tooltips.ny_discount_reward_tooltip import NyDiscountRewardTooltip
from new_year.gui.shared.ny_level_helper import getLevelIndexes
from new_year.skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.rewards_info.ny_levels_rewards_model import NyLevelsRewardsModel

class NyLevelsRewardsPresenter(object):
    __slots__ = ('__levels', '__parentView', '__viewModel')
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, viewModel, parentView):
        self.__parentView = parentView
        self.__viewModel = viewModel
        self.__levels = []

    @property
    def viewModel(self):
        return self.__viewModel

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            toolTipData = None
            tooltipId = event.getArgument('tooltipId')
            idx = event.getArgument('idx')
            if idx is not None:
                toolTipData = self.__levels[int(idx) - 1].createToolTipData(tooltipId)
            if toolTipData is None:
                return
            window = backport.BackportTooltipWindow(toolTipData, self.__parentView.getParentWindow())
            window.load()
            return window
        else:
            return

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        elif ctID == R.views.new_year.lobby.new_year.tooltips.NyDiscountRewardTooltip():
            variadicID, discount = event.getArgument('variadicID'), event.getArgument('discount')
            return NyDiscountRewardTooltip(variadicID, discount)
        else:
            toolTipContent = None
            idx = event.getArgument('idx')
            if idx is not None:
                toolTipContent = self.__levels[int(idx) - 1].createToolTipContent(event, ctID)
            return toolTipContent

    def initialize(self, *args, **kwargs):
        self.__nyController.onDataUpdated += self.__onDataUpdated
        self.__createData()

    def update(self, *args, **kwargs):
        self.__updateData()

    def finalize(self):
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        while self.__levels:
            self.__levels.pop().clear()

    def __onDataUpdated(self, *_):
        self.__updateData()

    def __createData(self):
        levelRewardsByID = new_year.g_cache.levelRewardsByID
        for index, level in enumerate(getLevelIndexes()):
            if level in levelRewardsByID:
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

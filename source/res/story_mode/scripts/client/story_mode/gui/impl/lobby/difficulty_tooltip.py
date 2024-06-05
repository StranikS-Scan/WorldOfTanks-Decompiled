# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/difficulty_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from story_mode.gui.impl.gen.view_models.views.lobby.mission_difficulty_tooltip_model import MissionDifficultyTooltipModel
from gui.impl.pub import ViewImpl

class DifficultyTooltip(ViewImpl):

    def __init__(self, difficulty, isSelected):
        settings = ViewSettings(R.views.story_mode.lobby.DifficultyTooltip(), model=MissionDifficultyTooltipModel())
        super(DifficultyTooltip, self).__init__(settings)
        self._difficulty = difficulty
        self._isSelected = isSelected

    @property
    def viewModel(self):
        return super(DifficultyTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DifficultyTooltip, self)._onLoading(*args, **kwargs)
        self.viewModel.setDifficulty(self._difficulty)
        self.viewModel.setIsSelected(self._isSelected)

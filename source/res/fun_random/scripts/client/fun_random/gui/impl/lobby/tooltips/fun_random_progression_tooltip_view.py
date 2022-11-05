# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_progression_tooltip_view.py
from frameworks.wulf import ViewSettings
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_progression_tooltip_view_model import FunRandomProgressionTooltipViewModel
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.impl.lobby.common.fun_view_helpers import packProgressionActiveStage, packProgressionCondition, packProgressionState
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class FunRandomProgressionTooltipView(ViewImpl, FunProgressionWatcher):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.tooltips.FunRandomProgressionTooltipView(), model=FunRandomProgressionTooltipViewModel())
        super(FunRandomProgressionTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomProgressionTooltipView, self).getViewModel()

    def _finalize(self):
        self.stopProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)

    def _onLoading(self, *args, **kwargs):
        super(FunRandomProgressionTooltipView, self)._onLoading(*args, **kwargs)
        self.startProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)
        self.__invalidateAll()

    @hasActiveProgression()
    def __invalidateAll(self, *_):
        progression = self.getActiveProgression()
        with self.viewModel.transaction() as model:
            packProgressionState(progression, model.state)
            packProgressionCondition(progression, model.condition)
            packProgressionActiveStage(progression, model.currentStage)

    @hasActiveProgression()
    def __invalidateTimer(self, *_):
        self.viewModel.state.setResetTimer(self.getActiveProgression().condition.resetTimer)

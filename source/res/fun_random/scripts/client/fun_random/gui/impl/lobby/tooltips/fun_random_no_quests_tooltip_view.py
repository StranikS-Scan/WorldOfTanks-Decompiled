# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_no_quests_tooltip_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_base_quest_tooltip_view_model import FunRandomBaseQuestTooltipViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import packQuestTooltip
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class FunRandomNoQuestsTooltipView(ViewImpl, FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher):

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.fun_random.mono.lobby.tooltips.base_quest_tooltip(), model=FunRandomBaseQuestTooltipViewModel())
        super(FunRandomNoQuestsTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomNoQuestsTooltipView, self).getViewModel()

    def _finalize(self):
        super(FunRandomNoQuestsTooltipView, self)._finalize()
        self.stopProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)

    def _onLoading(self, *args, **kwargs):
        super(FunRandomNoQuestsTooltipView, self)._onLoading(*args, **kwargs)
        self.startProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)
        self.__invalidateAll()

    @hasActiveProgression()
    def __invalidateAll(self, *_):
        progression = self.getActiveProgression()
        with self.viewModel.transaction() as model:
            packQuestTooltip(model, progression, self.getModeAssetsPointer())

    @hasActiveProgression()
    def __invalidateTimer(self, *_):
        self.viewModel.state.setStatusTimer(self.getActiveProgression().statusTimer)

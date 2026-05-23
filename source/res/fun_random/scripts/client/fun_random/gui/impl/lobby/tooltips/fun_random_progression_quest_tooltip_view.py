# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/tooltips/fun_random_progression_quest_tooltip_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_progression_quest_tooltip_view_model import FunRandomProgressionQuestTooltipViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import packTrigger, packQuestTooltip
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class FunRandomProgressionQuestTooltipView(ViewImpl, FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.fun_random.mono.lobby.tooltips.progression_quest_tooltip(), model=FunRandomProgressionQuestTooltipViewModel(), args=args, kwargs=kwargs)
        super(FunRandomProgressionQuestTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomProgressionQuestTooltipView, self).getViewModel()

    def _finalize(self):
        super(FunRandomProgressionQuestTooltipView, self)._finalize()
        self.stopProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)

    def _onLoading(self, triggerId, *args, **kwargs):
        super(FunRandomProgressionQuestTooltipView, self)._onLoading(*args, **kwargs)
        self.startProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)
        self.__invalidateAll(triggerId)

    @hasActiveProgression()
    def __invalidateAll(self, triggerId, *_):
        progression = self.getActiveProgression()
        with self.viewModel.transaction() as model:
            if progression.isInUnlimitedProgression:
                unlimitedProgression = progression.unlimitedProgression
                unlimitedTrigger = unlimitedProgression.unlimitedTrigger
                if triggerId == unlimitedTrigger.getID():
                    packTrigger(model.quest, unlimitedTrigger)
            else:
                triggers = progression.conditions.triggers
                for tr in triggers:
                    if tr.getID() == triggerId:
                        packTrigger(model.quest, tr)
                        break

            packQuestTooltip(model.tooltip, progression, self.getModeAssetsPointer())

    @hasActiveProgression()
    def __invalidateTimer(self, *_):
        self.viewModel.state.setStatusTimer(self.getActiveProgression().statusTimer)

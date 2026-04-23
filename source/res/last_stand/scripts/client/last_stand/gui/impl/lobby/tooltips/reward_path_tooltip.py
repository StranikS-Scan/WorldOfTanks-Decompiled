# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tooltips/reward_path_tooltip.py
from __future__ import absolute_import
import typing
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from helpers import dependency
from ids_generators import SequenceIDGenerator
from last_stand.gui.impl.gen.view_models.views.lobby.tooltips.reward_path_tooltip_view_model import RewardPathTooltipViewModel
from last_stand.gui.impl.lobby.ls_helpers import fillRewardPathWidgetViewModel, fillRewards
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_artefacts_controller import Artefact

class RewardPathTooltip(ViewImpl):
    lsArtefactsCtrl = dependency.descriptor(ILSArtefactsController)
    _MAX_BONUSES_IN_VIEW = 6

    def __init__(self):
        settings = ViewSettings(R.views.last_stand.mono.lobby.tooltips.reward_path_tooltip(), model=RewardPathTooltipViewModel())
        super(RewardPathTooltip, self).__init__(settings)
        self.__idGen = SequenceIDGenerator()

    @property
    def viewModel(self):
        return super(RewardPathTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RewardPathTooltip, self)._onLoading(*args, **kwargs)
        lastUnopenedArtefactId = self.lsArtefactsCtrl.getLastUnopenedArtefactId()
        fillRewardPathWidgetViewModel(self.viewModel, lastUnopenedArtefactId)
        if lastUnopenedArtefactId is not None:
            artefact = self.lsArtefactsCtrl.getArtefact(lastUnopenedArtefactId)
            fillRewards(artefact.bonusRewards, self.viewModel.getRewards(), self._MAX_BONUSES_IN_VIEW, self.__idGen)
        return

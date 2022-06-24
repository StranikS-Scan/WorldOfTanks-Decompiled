# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/frontline/rewards_selection_view_model.py
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_base_model import SelectableRewardBaseModel

class RewardsSelectionViewModel(SelectableRewardBaseModel):
    __slots__ = ('onLoadedView',)

    def __init__(self, properties=1, commands=1):
        super(RewardsSelectionViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(RewardsSelectionViewModel, self)._initialize()
        self.onLoadedView = self._addCommand('onLoadedView')

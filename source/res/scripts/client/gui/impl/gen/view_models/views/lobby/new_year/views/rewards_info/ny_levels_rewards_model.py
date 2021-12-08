# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/rewards_info/ny_levels_rewards_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_rewards_renderer_model import NewYearRewardsRendererModel

class NyLevelsRewardsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyLevelsRewardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardRenderers(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(NyLevelsRewardsModel, self)._initialize()
        self._addViewModelProperty('rewardRenderers', UserListModel())

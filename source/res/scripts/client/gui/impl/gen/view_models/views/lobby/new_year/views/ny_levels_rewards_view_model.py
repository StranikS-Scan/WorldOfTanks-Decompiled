# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_levels_rewards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NyLevelsRewardsViewModel(ViewModel):
    __slots__ = ('onTankwomanClick', 'onTankSlotClick', 'onTalismanClick', 'onRewardsCapacityChanged', 'onAlbumClick')

    def __init__(self, properties=2, commands=5):
        super(NyLevelsRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardRenderers(self):
        return self._getViewModel(0)

    def getCurrentLvl(self):
        return self._getNumber(1)

    def setCurrentLvl(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyLevelsRewardsViewModel, self)._initialize()
        self._addViewModelProperty('rewardRenderers', UserListModel())
        self._addNumberProperty('currentLvl', 0)
        self.onTankwomanClick = self._addCommand('onTankwomanClick')
        self.onTankSlotClick = self._addCommand('onTankSlotClick')
        self.onTalismanClick = self._addCommand('onTalismanClick')
        self.onRewardsCapacityChanged = self._addCommand('onRewardsCapacityChanged')
        self.onAlbumClick = self._addCommand('onAlbumClick')

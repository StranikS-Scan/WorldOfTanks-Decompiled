# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_rewards_view_model.py
import typing
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearRewardsViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onTankDiscountClick', 'onTankwomanRecruitClick', 'onAlbumClick')

    @property
    def rewardRenderers(self):
        return self._getViewModel(0)

    def getCurrentLvl(self):
        return self._getNumber(1)

    def setCurrentLvl(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NewYearRewardsViewModel, self)._initialize()
        self._addViewModelProperty('rewardRenderers', UserListModel())
        self._addNumberProperty('currentLvl', 0)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onTankDiscountClick = self._addCommand('onTankDiscountClick')
        self.onTankwomanRecruitClick = self._addCommand('onTankwomanRecruitClick')
        self.onAlbumClick = self._addCommand('onAlbumClick')

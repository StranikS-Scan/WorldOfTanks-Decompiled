# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/frontline/awards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.frontline.reward_item_model import RewardItemModel

class AwardsViewModel(ViewModel):
    __slots__ = ('onCloseClick', 'onAnimationEnded')

    def __init__(self, properties=2, commands=2):
        super(AwardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getMainRewardsType():
        return RewardItemModel

    @property
    def additionalRewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getAdditionalRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(AwardsViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onAnimationEnded = self._addCommand('onAnimationEnded')

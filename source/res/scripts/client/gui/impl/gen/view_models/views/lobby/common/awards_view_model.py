# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/awards_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.common.reward_item_model import RewardItemModel

class AwardsViewModel(ViewModel):
    __slots__ = ('onAnimationEnded', 'onRedirect', 'onClose')
    CLOSE_REASON_CANCEL = 'cancel'
    CLOSE_REASON_CONFIRM = 'confirm'

    def __init__(self, properties=9, commands=3):
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

    def getBackground(self):
        return self._getResource(2)

    def setBackground(self, value):
        self._setResource(2, value)

    def getTitle(self):
        return self._getResource(3)

    def setTitle(self, value):
        self._setResource(3, value)

    def getSubTitle(self):
        return self._getResource(4)

    def setSubTitle(self, value):
        self._setResource(4, value)

    def getUnderTitle(self):
        return self._getResource(5)

    def setUnderTitle(self, value):
        self._setResource(5, value)

    def getBottomNote(self):
        return self._getResource(6)

    def setBottomNote(self, value):
        self._setResource(6, value)

    def getDefaultButtonTitle(self):
        return self._getResource(7)

    def setDefaultButtonTitle(self, value):
        self._setResource(7, value)

    def getRedirectButtonTitle(self):
        return self._getResource(8)

    def setRedirectButtonTitle(self, value):
        self._setResource(8, value)

    def _initialize(self):
        super(AwardsViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addViewModelProperty('additionalRewards', UserListModel())
        self._addResourceProperty('background', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addResourceProperty('underTitle', R.invalid())
        self._addResourceProperty('bottomNote', R.invalid())
        self._addResourceProperty('defaultButtonTitle', R.invalid())
        self._addResourceProperty('redirectButtonTitle', R.invalid())
        self.onAnimationEnded = self._addCommand('onAnimationEnded')
        self.onRedirect = self._addCommand('onRedirect')
        self.onClose = self._addCommand('onClose')

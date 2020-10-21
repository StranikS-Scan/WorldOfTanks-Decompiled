# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/congratulation_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.halloween.reward_model import RewardModel

class CongratulationViewModel(ViewModel):
    __slots__ = ('onClose',)
    PLAYER_PACK = 0
    ITEM_PACK = 1

    def __init__(self, properties=3, commands=1):
        super(CongratulationViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(0)

    @property
    def additionRewards(self):
        return self._getViewModel(1)

    def getType(self):
        return self._getNumber(2)

    def setType(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(CongratulationViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addViewModelProperty('additionRewards', UserListModel())
        self._addNumberProperty('type', 0)
        self.onClose = self._addCommand('onClose')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/reward_level_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class RewardLevelModel(ViewModel):
    __slots__ = ()
    DISABLED = 0
    NOT_REACHED = 1
    REACHED = 2
    NOT_CHOSEN = 3

    def __init__(self, properties=4, commands=0):
        super(RewardLevelModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardItems(self):
        return self._getViewModel(0)

    def getLevelPoints(self):
        return self._getNumber(1)

    def setLevelPoints(self, value):
        self._setNumber(1, value)

    def getIsRare(self):
        return self._getBool(2)

    def setIsRare(self, value):
        self._setBool(2, value)

    def getState(self):
        return self._getNumber(3)

    def setState(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(RewardLevelModel, self)._initialize()
        self._addViewModelProperty('rewardItems', UserListModel())
        self._addNumberProperty('levelPoints', 0)
        self._addBoolProperty('isRare', False)
        self._addNumberProperty('state', -1)

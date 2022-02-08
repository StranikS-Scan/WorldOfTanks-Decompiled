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

    def __init__(self, properties=10, commands=0):
        super(RewardLevelModel, self).__init__(properties=properties, commands=commands)

    @property
    def freeRewardItems(self):
        return self._getViewModel(0)

    @property
    def paidRewardItems(self):
        return self._getViewModel(1)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getLevelPoints(self):
        return self._getNumber(3)

    def setLevelPoints(self, value):
        self._setNumber(3, value)

    def getIsRare(self):
        return self._getBool(4)

    def setIsRare(self, value):
        self._setBool(4, value)

    def getState(self):
        return self._getNumber(5)

    def setState(self, value):
        self._setNumber(5, value)

    def getNeedTakeFree(self):
        return self._getBool(6)

    def setNeedTakeFree(self, value):
        self._setBool(6, value)

    def getIsFreeRewardChoiceEnabled(self):
        return self._getBool(7)

    def setIsFreeRewardChoiceEnabled(self, value):
        self._setBool(7, value)

    def getNeedTakePaid(self):
        return self._getBool(8)

    def setNeedTakePaid(self, value):
        self._setBool(8, value)

    def getIsPaidRewardChoiceEnabled(self):
        return self._getBool(9)

    def setIsPaidRewardChoiceEnabled(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(RewardLevelModel, self)._initialize()
        self._addViewModelProperty('freeRewardItems', UserListModel())
        self._addViewModelProperty('paidRewardItems', UserListModel())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('levelPoints', 0)
        self._addBoolProperty('isRare', False)
        self._addNumberProperty('state', -1)
        self._addBoolProperty('needTakeFree', False)
        self._addBoolProperty('isFreeRewardChoiceEnabled', False)
        self._addBoolProperty('needTakePaid', False)
        self._addBoolProperty('isPaidRewardChoiceEnabled', False)

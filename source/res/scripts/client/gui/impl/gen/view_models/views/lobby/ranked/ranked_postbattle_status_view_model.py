# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_postbattle_status_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.ranked.ranked_state_model import RankedStateModel

class RankedPostbattleStatusViewModel(ViewModel):
    __slots__ = ('onClose', 'onSwitchAnimation', 'onSelectReward')

    def __init__(self, properties=9, commands=3):
        super(RankedPostbattleStatusViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def oldState(self):
        return self._getViewModel(0)

    @staticmethod
    def getOldStateType():
        return RankedStateModel

    @property
    def newState(self):
        return self._getViewModel(1)

    @staticmethod
    def getNewStateType():
        return RankedStateModel

    @property
    def rewards(self):
        return self._getViewModel(2)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def getMaxRank(self):
        return self._getNumber(3)

    def setMaxRank(self, value):
        self._setNumber(3, value)

    def getShowAnimation(self):
        return self._getBool(4)

    def setShowAnimation(self, value):
        self._setBool(4, value)

    def getCanTakeReward(self):
        return self._getBool(5)

    def setCanTakeReward(self, value):
        self._setBool(5, value)

    def getIsFinal(self):
        return self._getBool(6)

    def setIsFinal(self, value):
        self._setBool(6, value)

    def getTotalSteps(self):
        return self._getNumber(7)

    def setTotalSteps(self, value):
        self._setNumber(7, value)

    def getUnburnableRanks(self):
        return self._getArray(8)

    def setUnburnableRanks(self, value):
        self._setArray(8, value)

    @staticmethod
    def getUnburnableRanksType():
        return int

    def _initialize(self):
        super(RankedPostbattleStatusViewModel, self)._initialize()
        self._addViewModelProperty('oldState', RankedStateModel())
        self._addViewModelProperty('newState', RankedStateModel())
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('maxRank', 0)
        self._addBoolProperty('showAnimation', False)
        self._addBoolProperty('canTakeReward', False)
        self._addBoolProperty('isFinal', False)
        self._addNumberProperty('totalSteps', 0)
        self._addArrayProperty('unburnableRanks', Array())
        self.onClose = self._addCommand('onClose')
        self.onSwitchAnimation = self._addCommand('onSwitchAnimation')
        self.onSelectReward = self._addCommand('onSelectReward')

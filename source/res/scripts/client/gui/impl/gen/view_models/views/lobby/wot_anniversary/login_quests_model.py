# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/login_quests_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.login_bonus_model import LoginBonusModel

class State(IntEnum):
    CLAIM_REWARD = 0
    WAIT_NEXT_DAY = 1
    ALL_COMPLETED = 2


class LoginQuestsModel(ViewModel):
    __slots__ = ('claimReward',)

    def __init__(self, properties=4, commands=1):
        super(LoginQuestsModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getIsWaitingRewards(self):
        return self._getBool(1)

    def setIsWaitingRewards(self, value):
        self._setBool(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return LoginBonusModel

    def _initialize(self):
        super(LoginQuestsModel, self)._initialize()
        self._addNumberProperty('state')
        self._addBoolProperty('isWaitingRewards', False)
        self._addNumberProperty('endDate', 0)
        self._addArrayProperty('rewards', Array())
        self.claimReward = self._addCommand('claimReward')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/surprise_machine/robot_tv_screen_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RobotTvScreenState(Enum):
    IDLE = 'idle'
    ACTIVE = 'active'
    REWARDING = 'rewarding'
    VEHICLEREWARDING = 'vehicleRewarding'
    ERROR = 'error'


class RobotTvScreenViewModel(ViewModel):
    __slots__ = ('rewardingFinished', 'goToRewardVehicle', 'onCoinApplied')

    def __init__(self, properties=3, commands=3):
        super(RobotTvScreenViewModel, self).__init__(properties=properties, commands=commands)

    def getTokensCount(self):
        return self._getNumber(0)

    def setTokensCount(self, value):
        self._setNumber(0, value)

    def getScreenState(self):
        return RobotTvScreenState(self._getString(1))

    def setScreenState(self, value):
        self._setString(1, value.value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(RobotTvScreenViewModel, self)._initialize()
        self._addNumberProperty('tokensCount', 0)
        self._addStringProperty('screenState', RobotTvScreenState.IDLE.value)
        self._addArrayProperty('rewards', Array())
        self.rewardingFinished = self._addCommand('rewardingFinished')
        self.goToRewardVehicle = self._addCommand('goToRewardVehicle')
        self.onCoinApplied = self._addCommand('onCoinApplied')

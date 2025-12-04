# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/surprise_machine/robot_tv_screen_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class RobotTvScreenState(Enum):
    IDLE = 'idle'
    ACTIVE = 'active'
    CHOOSEAMOUNT = 'chooseAmount'
    REWARDING = 'rewarding'
    VEHICLEREWARDING = 'vehicleRewarding'
    ERROR = 'error'


class RobotTvButtons(Enum):
    ONE = 'one'
    NOT_ONE = 'notOne'
    CHANGE = 'change'
    NOT_SELECTED = 'notSelected'


class RobotTvScreenViewModel(ViewModel):
    __slots__ = ('rewardingFinished', 'goToRewardVehicle', 'onCoinApplied')

    def __init__(self, properties=4, commands=3):
        super(RobotTvScreenViewModel, self).__init__(properties=properties, commands=commands)

    def getSelectedButton(self):
        return RobotTvButtons(self._getString(0))

    def setSelectedButton(self, value):
        self._setString(0, value.value)

    def getTokensCount(self):
        return self._getNumber(1)

    def setTokensCount(self, value):
        self._setNumber(1, value)

    def getScreenState(self):
        return RobotTvScreenState(self._getString(2))

    def setScreenState(self, value):
        self._setString(2, value.value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(RobotTvScreenViewModel, self)._initialize()
        self._addStringProperty('selectedButton')
        self._addNumberProperty('tokensCount', 0)
        self._addStringProperty('screenState')
        self._addArrayProperty('rewards', Array())
        self.rewardingFinished = self._addCommand('rewardingFinished')
        self.goToRewardVehicle = self._addCommand('goToRewardVehicle')
        self.onCoinApplied = self._addCommand('onCoinApplied')

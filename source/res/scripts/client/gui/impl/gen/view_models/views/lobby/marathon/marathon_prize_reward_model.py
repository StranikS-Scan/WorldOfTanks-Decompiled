# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/marathon_prize_reward_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.marathon.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.marathon.marathon_prize_vehicle_model import MarathonPrizeVehicleModel

class MarathonPrizeRewardModel(ViewModel):
    __slots__ = ('onAcceptClicked', 'onSecondaryClicked', 'onCancelClicked')

    def __init__(self, properties=11, commands=3):
        super(MarathonPrizeRewardModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return MarathonPrizeVehicleModel

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getSupTitle(self):
        return self._getResource(2)

    def setSupTitle(self, value):
        self._setResource(2, value)

    def getSubTitle(self):
        return self._getResource(3)

    def setSubTitle(self, value):
        self._setResource(3, value)

    def getStage(self):
        return self._getNumber(4)

    def setStage(self, value):
        self._setNumber(4, value)

    def getImage(self):
        return self._getResource(5)

    def setImage(self, value):
        self._setResource(5, value)

    def getIconReward(self):
        return self._getResource(6)

    def setIconReward(self, value):
        self._setResource(6, value)

    def getHasVehicle(self):
        return self._getBool(7)

    def setHasVehicle(self, value):
        self._setBool(7, value)

    def getRewards(self):
        return self._getArray(8)

    def setRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def getRestRewards(self):
        return self._getArray(9)

    def setRestRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getRestRewardsType():
        return BonusModel

    def getRestRewardsCount(self):
        return self._getNumber(10)

    def setRestRewardsCount(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(MarathonPrizeRewardModel, self)._initialize()
        self._addViewModelProperty('vehicle', MarathonPrizeVehicleModel())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('supTitle', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addNumberProperty('stage', 0)
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('iconReward', R.invalid())
        self._addBoolProperty('hasVehicle', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('restRewards', Array())
        self._addNumberProperty('restRewardsCount', 0)
        self.onAcceptClicked = self._addCommand('onAcceptClicked')
        self.onSecondaryClicked = self._addCommand('onSecondaryClicked')
        self.onCancelClicked = self._addCommand('onCancelClicked')

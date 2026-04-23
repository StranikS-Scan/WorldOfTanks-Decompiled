# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/congrats_main_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.main_reward_bonus_model import MainRewardBonusModel
from historical_battles.gui.impl.gen.view_models.views.lobby.main_reward_vehicle_model import MainRewardVehicleModel

class CongratsMainRewardViewModel(ViewModel):
    __slots__ = ('onShowInHangar', 'onClose')

    def __init__(self, properties=2, commands=2):
        super(CongratsMainRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return MainRewardVehicleModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return MainRewardBonusModel

    def _initialize(self):
        super(CongratsMainRewardViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', MainRewardVehicleModel())
        self._addArrayProperty('rewards', Array())
        self.onShowInHangar = self._addCommand('onShowInHangar')
        self.onClose = self._addCommand('onClose')

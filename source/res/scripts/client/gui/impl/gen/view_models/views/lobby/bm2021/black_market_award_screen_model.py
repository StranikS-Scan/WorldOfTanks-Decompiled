# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/black_market_award_screen_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.bm2021.reward_item_model import RewardItemModel

class BlackMarketAwardScreenModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BlackMarketAwardScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainReward(self):
        return self._getViewModel(0)

    def getAdditionalRewards(self):
        return self._getArray(1)

    def setAdditionalRewards(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(BlackMarketAwardScreenModel, self)._initialize()
        self._addViewModelProperty('mainReward', VehicleModel())
        self._addArrayProperty('additionalRewards', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/reward_info_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.collection.reward_model import RewardModel

class RewardState(Enum):
    JUSTRECEIVED = 'justReceived'
    RECEIVED = 'received'
    UNRECEIVED = 'unreceived'


class RewardInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RewardInfoModel, self).__init__(properties=properties, commands=commands)

    def getRequiredItemsCount(self):
        return self._getNumber(0)

    def setRequiredItemsCount(self, value):
        self._setNumber(0, value)

    def getState(self):
        return RewardState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def _initialize(self):
        super(RewardInfoModel, self)._initialize()
        self._addNumberProperty('requiredItemsCount', 0)
        self._addStringProperty('state')
        self._addArrayProperty('rewards', Array())

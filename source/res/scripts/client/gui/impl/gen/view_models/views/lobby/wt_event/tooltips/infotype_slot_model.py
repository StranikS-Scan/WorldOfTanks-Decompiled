# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tooltips/infotype_slot_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.infotype_reward_model import InfotypeRewardModel

class RewardType(Enum):
    VEHICLE = 'vehicle'
    DEFAULT = 'default'
    RENTALTANK = 'rentalTank'
    GOLD = 'gold'


class InfotypeSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(InfotypeSlotModel, self).__init__(properties=properties, commands=commands)

    def getProbability(self):
        return self._getReal(0)

    def setProbability(self, value):
        self._setReal(0, value)

    def getRewardType(self):
        return RewardType(self._getString(1))

    def setRewardType(self, value):
        self._setString(1, value.value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return InfotypeRewardModel

    def _initialize(self):
        super(InfotypeSlotModel, self)._initialize()
        self._addRealProperty('probability', 0.0)
        self._addStringProperty('rewardType')
        self._addArrayProperty('rewards', Array())

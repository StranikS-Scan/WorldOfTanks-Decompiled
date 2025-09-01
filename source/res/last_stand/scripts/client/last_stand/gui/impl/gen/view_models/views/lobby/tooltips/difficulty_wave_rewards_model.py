# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/difficulty_wave_rewards_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class DifficultyWaveRewardsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DifficultyWaveRewardsModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIndex(self):
        return self._getNumber(1)

    def setIndex(self, value):
        self._setNumber(1, value)

    def getIsReceived(self):
        return self._getBool(2)

    def setIsReceived(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(DifficultyWaveRewardsModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('index', 0)
        self._addBoolProperty('isReceived', False)
        self._addArrayProperty('rewards', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/battle_result/player_results/battle_reward_item_model.py
from frameworks.wulf import ViewModel

class BattleRewardItemModel(ViewModel):
    __slots__ = ()
    PROGRESSION_POINTS = 'progressionTokens'
    UPGRADE_POINTS = 'vehicleExperience'

    def __init__(self, properties=2, commands=0):
        super(BattleRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(BattleRewardItemModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('value', 0)

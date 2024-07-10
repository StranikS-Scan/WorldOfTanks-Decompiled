# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/reward_item_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class RewardTypes(Enum):
    CREDITS = 'credits'
    CRYSTALS = 'crystal'
    XP = 'xp'


class RewardItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getNumber(1)

    def setValue(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('value', 0)

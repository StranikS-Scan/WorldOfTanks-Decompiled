# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/reward_model.py
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RewardModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(10)

    def setItem(self, value):
        self._setString(10, value)

    def getIcon(self):
        return self._getString(11)

    def setIcon(self, value):
        self._setString(11, value)

    def getUserName(self):
        return self._getString(12)

    def setUserName(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('userName', '')

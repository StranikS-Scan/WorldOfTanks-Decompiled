# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RewardItemModel(ItemBonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(9)

    def setIcon(self, value):
        self._setString(9, value)

    def getType(self):
        return self._getString(10)

    def setType(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('type', '')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/congratulation_reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class CongratulationRewardItemModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(CongratulationRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getItem(self):
        return self._getString(7)

    def setItem(self, value):
        self._setString(7, value)

    def getIcon(self):
        return self._getString(8)

    def setIcon(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(CongratulationRewardItemModel, self)._initialize()
        self._addStringProperty('item', '')
        self._addStringProperty('icon', '')

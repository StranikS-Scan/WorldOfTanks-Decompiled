# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/progress_reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel

class ProgressRewardItemModel(DiscountBonusModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(ProgressRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(11)

    def setIntCD(self, value):
        self._setNumber(11, value)

    def getIcon(self):
        return self._getString(12)

    def setIcon(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(ProgressRewardItemModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('icon', '')

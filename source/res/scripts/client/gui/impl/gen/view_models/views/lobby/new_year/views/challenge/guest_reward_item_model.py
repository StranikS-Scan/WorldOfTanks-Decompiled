# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/guest_reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class GuestRewardItemModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(GuestRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(8)

    def setIntCD(self, value):
        self._setNumber(8, value)

    def getHasNewActivity(self):
        return self._getBool(9)

    def setHasNewActivity(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(GuestRewardItemModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addBoolProperty('hasNewActivity', False)

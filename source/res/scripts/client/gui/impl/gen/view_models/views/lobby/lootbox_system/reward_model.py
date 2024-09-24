# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/reward_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class RewardType(Enum):
    VEHICLE = 'vehicles'
    DEFAULT = 'default'
    CUSTOMIZATION = 'customizations'


class RewardModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(8)

    def setCount(self, value):
        self._setNumber(8, value)

    def getOverlayType(self):
        return self._getString(9)

    def setOverlayType(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addStringProperty('overlayType', '')

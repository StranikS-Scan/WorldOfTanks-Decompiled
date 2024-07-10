# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/gen/view_models/views/lobby/event_lootboxes/reward_model.py
from enum import Enum
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class RewardType(Enum):
    VEHICLE = 'vehicle'
    DEFAULT = 'default'


class RewardModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getIconSource(self):
        return self._getResource(9)

    def setIconSource(self, value):
        self._setResource(9, value)

    def getCount(self):
        return self._getNumber(10)

    def setCount(self, value):
        self._setNumber(10, value)

    def getOverlayType(self):
        return self._getString(11)

    def setOverlayType(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addResourceProperty('iconSource', R.invalid())
        self._addNumberProperty('count', 0)
        self._addStringProperty('overlayType', '')

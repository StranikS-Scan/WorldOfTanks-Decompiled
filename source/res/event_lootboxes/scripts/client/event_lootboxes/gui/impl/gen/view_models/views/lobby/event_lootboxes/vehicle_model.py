# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/gen/view_models/views/lobby/event_lootboxes/vehicle_model.py
from enum import Enum
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.reward_model import RewardModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class VehicleModel(RewardModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(VehicleModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(12)

    def setName(self, value):
        self._setString(12, value)

    def getType(self):
        return VehicleType(self._getString(13))

    def setType(self, value):
        self._setString(13, value.value)

    def getLevel(self):
        return self._getNumber(14)

    def setLevel(self, value):
        self._setNumber(14, value)

    def _initialize(self):
        super(VehicleModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type')
        self._addNumberProperty('level', 0)

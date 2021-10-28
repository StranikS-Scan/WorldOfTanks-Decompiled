# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/timeline_item_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel

class PrizeEnum(IntEnum):
    NO_PRIZE = 0
    PRIZE_GIFT = 1
    PRIZE_TANK = 2


class ItemStateEnum(Enum):
    DEFAULT = 'default'
    RECEIVED = 'received'
    DECODED = 'decoded'


class TimelineItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TimelineItemModel, self).__init__(properties=properties, commands=commands)

    def getItemId(self):
        return self._getNumber(0)

    def setItemId(self, value):
        self._setNumber(0, value)

    def getCost(self):
        return self._getNumber(1)

    def setCost(self, value):
        self._setNumber(1, value)

    def getBackgroundImage(self):
        return self._getString(2)

    def setBackgroundImage(self, value):
        self._setString(2, value)

    def getPrize(self):
        return PrizeEnum(self._getNumber(3))

    def setPrize(self, value):
        self._setNumber(3, value.value)

    def getItemState(self):
        return ItemStateEnum(self._getString(4))

    def setItemState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(TimelineItemModel, self)._initialize()
        self._addNumberProperty('itemId', 0)
        self._addNumberProperty('cost', 0)
        self._addStringProperty('backgroundImage', '')
        self._addNumberProperty('prize')
        self._addStringProperty('itemState')

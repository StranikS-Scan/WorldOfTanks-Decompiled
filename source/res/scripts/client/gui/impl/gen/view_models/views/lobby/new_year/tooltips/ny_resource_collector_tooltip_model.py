# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_resource_collector_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CollectorTooltipType(Enum):
    AVAILABLE = 'available'
    AVAILABLEEXTRA = 'availableExtra'
    COLLECTED = 'collected'
    UNAVAILABLE = 'unavailable'
    FINISHED = 'finished'


class NyResourceCollectorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyResourceCollectorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return CollectorTooltipType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getCooldown(self):
        return self._getNumber(1)

    def setCooldown(self, value):
        self._setNumber(1, value)

    def getBaseCollectAmount(self):
        return self._getNumber(2)

    def setBaseCollectAmount(self, value):
        self._setNumber(2, value)

    def getExtraCollectAmount(self):
        return self._getNumber(3)

    def setExtraCollectAmount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(NyResourceCollectorTooltipModel, self)._initialize()
        self._addStringProperty('type')
        self._addNumberProperty('cooldown', 0)
        self._addNumberProperty('baseCollectAmount', 0)
        self._addNumberProperty('extraCollectAmount', 0)

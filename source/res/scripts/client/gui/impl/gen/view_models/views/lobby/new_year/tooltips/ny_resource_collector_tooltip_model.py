# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_resource_collector_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CollectorTooltipType(Enum):
    AUTO = 'auto'
    MANUALUNAVAILABLE = 'manualUnavailable'
    CANCELAUTO = 'cancelAuto'
    MANUALAVAILABLE = 'manualAvailable'


class NyResourceCollectorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(NyResourceCollectorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return CollectorTooltipType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getCredits(self):
        return self._getNumber(2)

    def setCredits(self, value):
        self._setNumber(2, value)

    def getCooldown(self):
        return self._getNumber(3)

    def setCooldown(self, value):
        self._setNumber(3, value)

    def getSecondCollectCooldown(self):
        return self._getNumber(4)

    def setSecondCollectCooldown(self, value):
        self._setNumber(4, value)

    def getCollectedAmount(self):
        return self._getNumber(5)

    def setCollectedAmount(self, value):
        self._setNumber(5, value)

    def getCreditsSpent(self):
        return self._getNumber(6)

    def setCreditsSpent(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(NyResourceCollectorTooltipModel, self)._initialize()
        self._addStringProperty('type')
        self._addNumberProperty('price', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('cooldown', 0)
        self._addNumberProperty('secondCollectCooldown', 0)
        self._addNumberProperty('collectedAmount', 0)
        self._addNumberProperty('creditsSpent', 0)

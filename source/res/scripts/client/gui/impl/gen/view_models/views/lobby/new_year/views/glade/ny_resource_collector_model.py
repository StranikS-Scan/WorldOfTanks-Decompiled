# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/ny_resource_collector_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CollectState(Enum):
    AVAILABLE = 'available'
    AVAILABLEEXTRA = 'availableExtra'
    COLLECTED = 'collected'
    UNAVAILABLE = 'unavailable'
    UNAVAILABLEEXTRA = 'unavailableExtra'
    FINISHED = 'finished'
    FINISHEDHIDDEN = 'finishedHidden'


class NyResourceCollectorModel(ViewModel):
    __slots__ = ('onCollect', 'onHideFinishedStatus')

    def __init__(self, properties=5, commands=2):
        super(NyResourceCollectorModel, self).__init__(properties=properties, commands=commands)

    def getCollectState(self):
        return CollectState(self._getString(0))

    def setCollectState(self, value):
        self._setString(0, value.value)

    def getBaseCollectAmount(self):
        return self._getNumber(1)

    def setBaseCollectAmount(self, value):
        self._setNumber(1, value)

    def getExtraCollectAmount(self):
        return self._getNumber(2)

    def setExtraCollectAmount(self, value):
        self._setNumber(2, value)

    def getCooldown(self):
        return self._getNumber(3)

    def setCooldown(self, value):
        self._setNumber(3, value)

    def getSkippedDays(self):
        return self._getNumber(4)

    def setSkippedDays(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NyResourceCollectorModel, self)._initialize()
        self._addStringProperty('collectState')
        self._addNumberProperty('baseCollectAmount', 0)
        self._addNumberProperty('extraCollectAmount', 0)
        self._addNumberProperty('cooldown', 0)
        self._addNumberProperty('skippedDays', 0)
        self.onCollect = self._addCommand('onCollect')
        self.onHideFinishedStatus = self._addCommand('onHideFinishedStatus')

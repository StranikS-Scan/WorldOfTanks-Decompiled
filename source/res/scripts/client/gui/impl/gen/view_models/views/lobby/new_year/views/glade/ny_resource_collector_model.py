# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/ny_resource_collector_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CollectState(Enum):
    AVAILABLEMANUAL = 'availableManual'
    AVAILABLEAUTO = 'availableAuto'
    AVAILABLEBOTH = 'availableBoth'
    UNAVAILABLE = 'unavailable'
    AUTOACTIVE = 'autoActive'
    FINISHED = 'finished'
    FINISHEDHIDDEN = 'finishedHidden'


class NyResourceCollectorModel(ViewModel):
    __slots__ = ('onCollect', 'onEnableAuto', 'onDisableAuto', 'onHideFinishedStatus')

    def __init__(self, properties=3, commands=4):
        super(NyResourceCollectorModel, self).__init__(properties=properties, commands=commands)

    def getCollectState(self):
        return CollectState(self._getString(0))

    def setCollectState(self, value):
        self._setString(0, value.value)

    def getCollectAmount(self):
        return self._getNumber(1)

    def setCollectAmount(self, value):
        self._setNumber(1, value)

    def getCooldown(self):
        return self._getNumber(2)

    def setCooldown(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyResourceCollectorModel, self)._initialize()
        self._addStringProperty('collectState')
        self._addNumberProperty('collectAmount', 0)
        self._addNumberProperty('cooldown', 0)
        self.onCollect = self._addCommand('onCollect')
        self.onEnableAuto = self._addCommand('onEnableAuto')
        self.onDisableAuto = self._addCommand('onDisableAuto')
        self.onHideFinishedStatus = self._addCommand('onHideFinishedStatus')

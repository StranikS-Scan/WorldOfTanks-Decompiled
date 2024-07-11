# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_queue_view/races_queue_view_model.py
from frameworks.wulf import ViewModel

class RacesQueueViewModel(ViewModel):
    __slots__ = ('onLeave',)

    def __init__(self, properties=2, commands=1):
        super(RacesQueueViewModel, self).__init__(properties=properties, commands=commands)

    def getPlayersInQueue(self):
        return self._getNumber(0)

    def setPlayersInQueue(self, value):
        self._setNumber(0, value)

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(RacesQueueViewModel, self)._initialize()
        self._addNumberProperty('playersInQueue', 0)
        self._addStringProperty('vehicleName', '')
        self.onLeave = self._addCommand('onLeave')

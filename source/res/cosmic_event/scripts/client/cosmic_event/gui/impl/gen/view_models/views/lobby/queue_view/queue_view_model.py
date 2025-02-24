# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/queue_view/queue_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class RoverEnum(IntEnum):
    OLD = 1
    NEW = 2


class QueueViewModel(ViewModel):
    __slots__ = ('onLeave',)

    def __init__(self, properties=5, commands=1):
        super(QueueViewModel, self).__init__(properties=properties, commands=commands)

    def getPlayersInQueue(self):
        return self._getNumber(0)

    def setPlayersInQueue(self, value):
        self._setNumber(0, value)

    def getOldRoverQueue(self):
        return self._getNumber(1)

    def setOldRoverQueue(self, value):
        self._setNumber(1, value)

    def getNewRoverQueue(self):
        return self._getNumber(2)

    def setNewRoverQueue(self, value):
        self._setNumber(2, value)

    def getSelectedVehicleResource(self):
        return self._getString(3)

    def setSelectedVehicleResource(self, value):
        self._setString(3, value)

    def getVehicle(self):
        return RoverEnum(self._getNumber(4))

    def setVehicle(self, value):
        self._setNumber(4, value.value)

    def _initialize(self):
        super(QueueViewModel, self)._initialize()
        self._addNumberProperty('playersInQueue', 0)
        self._addNumberProperty('oldRoverQueue', 0)
        self._addNumberProperty('newRoverQueue', 0)
        self._addStringProperty('selectedVehicleResource', '')
        self._addNumberProperty('vehicle', RoverEnum.OLD.value)
        self.onLeave = self._addCommand('onLeave')

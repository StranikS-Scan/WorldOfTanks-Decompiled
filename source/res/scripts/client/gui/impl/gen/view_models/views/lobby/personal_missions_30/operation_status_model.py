# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/operation_status_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class OperationStatus(Enum):
    CAMPAIGN_FINISHED = 'campaignFinished'
    NOT_ALL_COMPLETED = 'notAllCompleted'
    NOT_ALL_COMPLETED_WITH_HONOR = 'notAllCompletedWithHonor'
    PAUSED = 'paused'
    NEXT_OPERATION_AVAILABLE = 'nextOperationAvailable'
    COMPLETED = 'completed'
    PRECEDING_OPERATION_NOT_COMPLETED = 'precedingOperationNotCompleted'
    REQUIRES_VEHICLE = 'requiresVehicle'
    VEHICLE_IS_IN_BATTLE = 'vehicleIsInBattle'
    ACTIVE = 'active'
    AVAILABLE = 'available'


class OperationStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(OperationStatusModel, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return OperationStatus(self._getString(0))

    def setStatus(self, value):
        self._setString(0, value.value)

    def getRequiredVehicleLevel(self):
        return self._getNumber(1)

    def setRequiredVehicleLevel(self, value):
        self._setNumber(1, value)

    def getCurrentOperationId(self):
        return self._getNumber(2)

    def setCurrentOperationId(self, value):
        self._setNumber(2, value)

    def getNextOperationName(self):
        return self._getString(3)

    def setNextOperationName(self, value):
        self._setString(3, value)

    def getCurrentOperationName(self):
        return self._getString(4)

    def setCurrentOperationName(self, value):
        self._setString(4, value)

    def getOperationIdToPerform(self):
        return self._getNumber(5)

    def setOperationIdToPerform(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(OperationStatusModel, self)._initialize()
        self._addStringProperty('status')
        self._addNumberProperty('requiredVehicleLevel', 0)
        self._addNumberProperty('currentOperationId', 0)
        self._addStringProperty('nextOperationName', '')
        self._addStringProperty('currentOperationName', '')
        self._addNumberProperty('operationIdToPerform', 0)

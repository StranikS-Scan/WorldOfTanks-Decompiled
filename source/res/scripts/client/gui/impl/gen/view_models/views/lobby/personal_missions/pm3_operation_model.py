# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/pm3_operation_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class MissionStatus(Enum):
    AVAILABLE = 'available'
    AVAILABLEPAUSED = 'availablePaused'
    ACTIVE = 'active'
    ACTIVEPAUSED = 'activePaused'
    DISABLED = 'disabled'
    DISABLEDPAUSED = 'disabledPaused'
    COMPLETED = 'completed'
    COMPLETEDPERFECTLY = 'completedPerfectly'
    COMPLETEDPAUSED = 'completedPaused'


class LastMissionStatus(Enum):
    DEVELOPMENT = 'development'
    DISABLED = 'disabled'
    ACTIVE = 'active'
    COMPLETED = 'completed'


class Pm3OperationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(Pm3OperationModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getOperationId(self):
        return self._getNumber(1)

    def setOperationId(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getLevel(self):
        return self._getString(3)

    def setLevel(self, value):
        self._setString(3, value)

    def getTypeIcon(self):
        return self._getString(4)

    def setTypeIcon(self, value):
        self._setString(4, value)

    def getTotalQuests(self):
        return self._getNumber(5)

    def setTotalQuests(self, value):
        self._setNumber(5, value)

    def getCompletedQuests(self):
        return self._getNumber(6)

    def setCompletedQuests(self, value):
        self._setNumber(6, value)

    def getDelta(self):
        return self._getNumber(7)

    def setDelta(self, value):
        self._setNumber(7, value)

    def getStatus(self):
        return MissionStatus(self._getString(8))

    def setStatus(self, value):
        self._setString(8, value.value)

    def getVehicleName(self):
        return self._getString(9)

    def setVehicleName(self, value):
        self._setString(9, value)

    def getIsElite(self):
        return self._getBool(10)

    def setIsElite(self, value):
        self._setBool(10, value)

    def getPrevOperationName(self):
        return self._getString(11)

    def setPrevOperationName(self, value):
        self._setString(11, value)

    def getIsHasLevels(self):
        return self._getBool(12)

    def setIsHasLevels(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(Pm3OperationModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('operationId', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('level', '')
        self._addStringProperty('typeIcon', '')
        self._addNumberProperty('totalQuests', 0)
        self._addNumberProperty('completedQuests', 0)
        self._addNumberProperty('delta', 0)
        self._addStringProperty('status')
        self._addStringProperty('vehicleName', '')
        self._addBoolProperty('isElite', False)
        self._addStringProperty('prevOperationName', '')
        self._addBoolProperty('isHasLevels', True)

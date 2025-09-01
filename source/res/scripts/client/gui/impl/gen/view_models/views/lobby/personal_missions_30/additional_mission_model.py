# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/additional_mission_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class AdditionalMissionType(Enum):
    DAILY = 'daily'
    WEEKLY = 'weekly'


class AdditionalMissionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(AdditionalMissionModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return AdditionalMissionType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getMaxPoints(self):
        return self._getNumber(1)

    def setMaxPoints(self, value):
        self._setNumber(1, value)

    def getCurrentPoints(self):
        return self._getNumber(2)

    def setCurrentPoints(self, value):
        self._setNumber(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getIsProgressHidden(self):
        return self._getBool(4)

    def setIsProgressHidden(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(AdditionalMissionModel, self)._initialize()
        self._addStringProperty('type')
        self._addNumberProperty('maxPoints', 0)
        self._addNumberProperty('currentPoints', 0)
        self._addBoolProperty('isEnabled', False)
        self._addBoolProperty('isProgressHidden', False)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/tooltips/task_condition_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class TaskConditionTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TaskConditionTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getLevels(self):
        return self._getString(0)

    def setLevels(self, value):
        self._setString(0, value)

    def getVehicleTypes(self):
        return self._getArray(1)

    def setVehicleTypes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehicleTypesType():
        return unicode

    def getBattleTypes(self):
        return self._getArray(2)

    def setBattleTypes(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def _initialize(self):
        super(TaskConditionTooltipViewModel, self)._initialize()
        self._addStringProperty('levels', '')
        self._addArrayProperty('vehicleTypes', Array())
        self._addArrayProperty('battleTypes', Array())

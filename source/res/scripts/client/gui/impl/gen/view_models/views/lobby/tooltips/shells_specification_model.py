# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/shells_specification_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ShellsSpecificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ShellsSpecificationModel, self).__init__(properties=properties, commands=commands)

    def getParamName(self):
        return self._getString(0)

    def setParamName(self, value):
        self._setString(0, value)

    def getValues(self):
        return self._getArray(1)

    def setValues(self, value):
        self._setArray(1, value)

    def getMetricValue(self):
        return self._getString(2)

    def setMetricValue(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ShellsSpecificationModel, self)._initialize()
        self._addStringProperty('paramName', '')
        self._addArrayProperty('values', Array())
        self._addStringProperty('metricValue', '')

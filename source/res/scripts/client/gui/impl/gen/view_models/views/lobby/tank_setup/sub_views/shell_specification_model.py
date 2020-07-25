# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/shell_specification_model.py
from frameworks.wulf import ViewModel

class ShellSpecificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ShellSpecificationModel, self).__init__(properties=properties, commands=commands)

    def getParamName(self):
        return self._getString(0)

    def setParamName(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getMetricValue(self):
        return self._getString(2)

    def setMetricValue(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ShellSpecificationModel, self)._initialize()
        self._addStringProperty('paramName', '')
        self._addStringProperty('value', '')
        self._addStringProperty('metricValue', '')

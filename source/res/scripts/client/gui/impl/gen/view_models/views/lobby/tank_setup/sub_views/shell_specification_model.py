# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/shell_specification_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.param_value_model import ParamValueModel

class ShellSpecificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ShellSpecificationModel, self).__init__(properties=properties, commands=commands)

    def getParamName(self):
        return self._getString(0)

    def setParamName(self, value):
        self._setString(0, value)

    def getMetricValue(self):
        return self._getString(1)

    def setMetricValue(self, value):
        self._setString(1, value)

    def getValues(self):
        return self._getArray(2)

    def setValues(self, value):
        self._setArray(2, value)

    @staticmethod
    def getValuesType():
        return ParamValueModel

    def _initialize(self):
        super(ShellSpecificationModel, self)._initialize()
        self._addStringProperty('paramName', '')
        self._addStringProperty('metricValue', '')
        self._addArrayProperty('values', Array())

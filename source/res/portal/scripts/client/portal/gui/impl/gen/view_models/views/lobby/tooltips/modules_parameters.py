# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/modules_parameters.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.tooltips.parameters_values import ParametersValues

class ModulesParameters(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ModulesParameters, self).__init__(properties=properties, commands=commands)

    def getValues(self):
        return self._getArray(0)

    def setValues(self, value):
        self._setArray(0, value)

    @staticmethod
    def getValuesType():
        return ParametersValues

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getUnitOfMeasurement(self):
        return self._getString(2)

    def setUnitOfMeasurement(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ModulesParameters, self)._initialize()
        self._addArrayProperty('values', Array())
        self._addStringProperty('description', '')
        self._addStringProperty('unitOfMeasurement', '')

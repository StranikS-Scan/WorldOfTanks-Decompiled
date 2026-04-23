# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_style_parameter_model.py
from frameworks.wulf import ViewModel

class CustomizationStyleParameterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CustomizationStyleParameterModel, self).__init__(properties=properties, commands=commands)

    def getPoId(self):
        return self._getString(0)

    def setPoId(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getValue(self):
        return self._getString(2)

    def setValue(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(CustomizationStyleParameterModel, self)._initialize()
        self._addStringProperty('poId', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('value', '')

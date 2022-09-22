# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/tooltips/benefit_value_model.py
from frameworks.wulf import ViewModel

class BenefitValueModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BenefitValueModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getReal(0)

    def setValue(self, value):
        self._setReal(0, value)

    def getSubstitutionID(self):
        return self._getString(1)

    def setSubstitutionID(self, value):
        self._setString(1, value)

    def getValueType(self):
        return self._getString(2)

    def setValueType(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BenefitValueModel, self)._initialize()
        self._addRealProperty('value', 0.0)
        self._addStringProperty('substitutionID', '')
        self._addStringProperty('valueType', '')

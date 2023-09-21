# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/tooltips/premium_benefit_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.benefit_value_model import BenefitValueModel

class PremiumBenefitModel(ViewModel):
    __slots__ = ()
    NUMBER_VALUE = 'number_value'
    PERCENT_VALUE = 'percent_value'

    def __init__(self, properties=2, commands=0):
        super(PremiumBenefitModel, self).__init__(properties=properties, commands=commands)

    def getStringID(self):
        return self._getResource(0)

    def setStringID(self, value):
        self._setResource(0, value)

    def getValue(self):
        return self._getArray(1)

    def setValue(self, value):
        self._setArray(1, value)

    @staticmethod
    def getValueType():
        return BenefitValueModel

    def _initialize(self):
        super(PremiumBenefitModel, self)._initialize()
        self._addResourceProperty('stringID', R.invalid())
        self._addArrayProperty('value', Array())

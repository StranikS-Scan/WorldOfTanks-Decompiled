# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_economic_bonus_model.py
from frameworks.wulf import ViewModel

class NyEconomicBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyEconomicBonusModel, self).__init__(properties=properties, commands=commands)

    def getBonusName(self):
        return self._getString(0)

    def setBonusName(self, value):
        self._setString(0, value)

    def getBonusValue(self):
        return self._getReal(1)

    def setBonusValue(self, value):
        self._setReal(1, value)

    def _initialize(self):
        super(NyEconomicBonusModel, self)._initialize()
        self._addStringProperty('bonusName', '')
        self._addRealProperty('bonusValue', 0.0)

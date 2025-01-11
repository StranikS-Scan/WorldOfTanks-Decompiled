# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_vehicle_bonuses_tooltip_model.py
from frameworks.wulf import ViewModel

class NyVehicleBonusesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyVehicleBonusesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBonusType(self):
        return self._getString(0)

    def setBonusType(self, value):
        self._setString(0, value)

    def getBonusValue(self):
        return self._getNumber(1)

    def setBonusValue(self, value):
        self._setNumber(1, value)

    def getCreditBonusValue(self):
        return self._getNumber(2)

    def setCreditBonusValue(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyVehicleBonusesTooltipModel, self)._initialize()
        self._addStringProperty('bonusType', '')
        self._addNumberProperty('bonusValue', 0)
        self._addNumberProperty('creditBonusValue', 0)

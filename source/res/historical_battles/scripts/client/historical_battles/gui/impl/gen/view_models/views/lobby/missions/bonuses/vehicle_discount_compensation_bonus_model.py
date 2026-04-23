# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/missions/bonuses/vehicle_discount_compensation_bonus_model.py
from historical_battles.gui.impl.gen.view_models.views.lobby.missions.bonuses.vehicle_discount_bonus_model import VehicleDiscountBonusModel

class VehicleDiscountCompensationBonusModel(VehicleDiscountBonusModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(VehicleDiscountCompensationBonusModel, self).__init__(properties=properties, commands=commands)

    def getCompensationAmount(self):
        return self._getNumber(16)

    def setCompensationAmount(self, value):
        self._setNumber(16, value)

    def getCompensationCurrency(self):
        return self._getString(17)

    def setCompensationCurrency(self, value):
        self._setString(17, value)

    def _initialize(self):
        super(VehicleDiscountCompensationBonusModel, self)._initialize()
        self._addNumberProperty('compensationAmount', 0)
        self._addStringProperty('compensationCurrency', '0')

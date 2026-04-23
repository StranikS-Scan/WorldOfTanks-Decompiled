# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/missions/bonuses/vehicle_discount_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel

class VehicleDiscountBonusModel(TokenBonusModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(VehicleDiscountBonusModel, self).__init__(properties=properties, commands=commands)

    def getTankType(self):
        return self._getString(11)

    def setTankType(self, value):
        self._setString(11, value)

    def getTankUserName(self):
        return self._getString(12)

    def setTankUserName(self, value):
        self._setString(12, value)

    def getTankLevel(self):
        return self._getNumber(13)

    def setTankLevel(self, value):
        self._setNumber(13, value)

    def getIsElite(self):
        return self._getBool(14)

    def setIsElite(self, value):
        self._setBool(14, value)

    def getDiscountPercent(self):
        return self._getNumber(15)

    def setDiscountPercent(self, value):
        self._setNumber(15, value)

    def _initialize(self):
        super(VehicleDiscountBonusModel, self)._initialize()
        self._addStringProperty('tankType', '')
        self._addStringProperty('tankUserName', '')
        self._addNumberProperty('tankLevel', 0)
        self._addBoolProperty('isElite', True)
        self._addNumberProperty('discountPercent', 0)

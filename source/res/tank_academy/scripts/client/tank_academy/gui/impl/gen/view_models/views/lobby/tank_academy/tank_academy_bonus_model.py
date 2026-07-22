# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class TankAcademyBonusModel(IconBonusModel):
    __slots__ = ()
    NAME_VEHICLE_REWARD = 'vehicle'
    NAME_TOKEN_VEHICLE_REWARD = 'tokenVehicle'

    def __init__(self, properties=12, commands=0):
        super(TankAcademyBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsEssential(self):
        return self._getBool(8)

    def setIsEssential(self, value):
        self._setBool(8, value)

    def getTier(self):
        return self._getNumber(9)

    def setTier(self, value):
        self._setNumber(9, value)

    def getIsPremium(self):
        return self._getBool(10)

    def setIsPremium(self, value):
        self._setBool(10, value)

    def getType(self):
        return self._getString(11)

    def setType(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(TankAcademyBonusModel, self)._initialize()
        self._addBoolProperty('isEssential', False)
        self._addNumberProperty('tier', 0)
        self._addBoolProperty('isPremium', False)
        self._addStringProperty('type', '')

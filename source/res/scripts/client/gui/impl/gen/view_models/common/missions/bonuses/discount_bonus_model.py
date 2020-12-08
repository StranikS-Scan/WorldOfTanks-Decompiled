# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/discount_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class DiscountBonusModel(BonusModel):
    __slots__ = ()
    NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID = 'NYSelectVehicleForDiscountPopover'

    def __init__(self, properties=9, commands=0):
        super(DiscountBonusModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getDiscount(self):
        return self._getNumber(6)

    def setDiscount(self, value):
        self._setNumber(6, value)

    def getSelectedVehicle(self):
        return self._getString(7)

    def setSelectedVehicle(self, value):
        self._setString(7, value)

    def getVariadicID(self):
        return self._getString(8)

    def setVariadicID(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(DiscountBonusModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('discount', 0)
        self._addStringProperty('selectedVehicle', '')
        self._addStringProperty('variadicID', '')

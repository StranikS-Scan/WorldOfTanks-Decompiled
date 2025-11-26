# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/tooltips/pet_tooltip_model.py
from frameworks.wulf import Array, ViewModel

class PetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPetNameID(self):
        return self._getNumber(0)

    def setPetNameID(self, value):
        self._setNumber(0, value)

    def getPetID(self):
        return self._getNumber(1)

    def setPetID(self, value):
        self._setNumber(1, value)

    def getPetType(self):
        return self._getString(2)

    def setPetType(self, value):
        self._setString(2, value)

    def getBreedName(self):
        return self._getString(3)

    def setBreedName(self, value):
        self._setString(3, value)

    def getPromotionBonuses(self):
        return self._getArray(4)

    def setPromotionBonuses(self, value):
        self._setArray(4, value)

    @staticmethod
    def getPromotionBonusesType():
        return unicode

    def _initialize(self):
        super(PetTooltipModel, self)._initialize()
        self._addNumberProperty('petNameID', 0)
        self._addNumberProperty('petID', 0)
        self._addStringProperty('petType', '')
        self._addStringProperty('breedName', '')
        self._addArrayProperty('promotionBonuses', Array())

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/pet_card_model.py
from frameworks.wulf import ViewModel

class PetCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PetCardModel, self).__init__(properties=properties, commands=commands)

    def getPetID(self):
        return self._getNumber(0)

    def setPetID(self, value):
        self._setNumber(0, value)

    def getPetNameID(self):
        return self._getNumber(1)

    def setPetNameID(self, value):
        self._setNumber(1, value)

    def getBonusName(self):
        return self._getString(2)

    def setBonusName(self, value):
        self._setString(2, value)

    def getBonusValue(self):
        return self._getNumber(3)

    def setBonusValue(self, value):
        self._setNumber(3, value)

    def getIsMaxSynergyLevel(self):
        return self._getBool(4)

    def setIsMaxSynergyLevel(self, value):
        self._setBool(4, value)

    def getIsNew(self):
        return self._getBool(5)

    def setIsNew(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(PetCardModel, self)._initialize()
        self._addNumberProperty('petID', 0)
        self._addNumberProperty('petNameID', 0)
        self._addStringProperty('bonusName', '')
        self._addNumberProperty('bonusValue', 0)
        self._addBoolProperty('isMaxSynergyLevel', False)
        self._addBoolProperty('isNew', False)

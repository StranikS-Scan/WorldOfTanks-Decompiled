# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/tooltips/pet_storage_tooltip_model.py
from frameworks.wulf import ViewModel

class PetStorageTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PetStorageTooltipModel, self).__init__(properties=properties, commands=commands)

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

    def getBonusName(self):
        return self._getString(4)

    def setBonusName(self, value):
        self._setString(4, value)

    def getBonusValue(self):
        return self._getNumber(5)

    def setBonusValue(self, value):
        self._setNumber(5, value)

    def getTotalBattleCount(self):
        return self._getNumber(6)

    def setTotalBattleCount(self, value):
        self._setNumber(6, value)

    def getCurrentBattleCount(self):
        return self._getNumber(7)

    def setCurrentBattleCount(self, value):
        self._setNumber(7, value)

    def getIsUnsuitableMode(self):
        return self._getBool(8)

    def setIsUnsuitableMode(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(PetStorageTooltipModel, self)._initialize()
        self._addNumberProperty('petNameID', 0)
        self._addNumberProperty('petID', 0)
        self._addStringProperty('petType', '')
        self._addStringProperty('breedName', '')
        self._addStringProperty('bonusName', '')
        self._addNumberProperty('bonusValue', 0)
        self._addNumberProperty('totalBattleCount', 0)
        self._addNumberProperty('currentBattleCount', 0)
        self._addBoolProperty('isUnsuitableMode', False)

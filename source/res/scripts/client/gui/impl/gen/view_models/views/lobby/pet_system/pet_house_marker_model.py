# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/pet_house_marker_model.py
from frameworks.wulf import ViewModel

class PetHouseMarkerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PetHouseMarkerModel, self).__init__(properties=properties, commands=commands)

    def getPetNameID(self):
        return self._getNumber(0)

    def setPetNameID(self, value):
        self._setNumber(0, value)

    def getHasUpdate(self):
        return self._getBool(1)

    def setHasUpdate(self, value):
        self._setBool(1, value)

    def getIsVisible(self):
        return self._getBool(2)

    def setIsVisible(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PetHouseMarkerModel, self)._initialize()
        self._addNumberProperty('petNameID', 0)
        self._addBoolProperty('hasUpdate', False)
        self._addBoolProperty('isVisible', True)

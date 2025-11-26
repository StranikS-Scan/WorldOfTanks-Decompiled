# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pet_system/pet_name_model.py
from frameworks.wulf import ViewModel

class PetNameModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PetNameModel, self).__init__(properties=properties, commands=commands)

    def getPetNameID(self):
        return self._getNumber(0)

    def setPetNameID(self, value):
        self._setNumber(0, value)

    def getIsNew(self):
        return self._getBool(1)

    def setIsNew(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(PetNameModel, self)._initialize()
        self._addNumberProperty('petNameID', 0)
        self._addBoolProperty('isNew', False)

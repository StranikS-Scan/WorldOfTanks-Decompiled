# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/personal_data_card_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DataCardState(Enum):
    DEFAULT = 'default'
    SELECTED = 'selected'
    DISABLED = 'disabled'


class DataCardType(Enum):
    DOCUMENT = 'document'
    SKIN = 'skin'


class DataCardFilter(Enum):
    DOCUMENT = 'document'
    SUITABLESKIN = 'suitableSkin'


class PersonalDataCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PersonalDataCardModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getNation(self):
        return self._getString(2)

    def setNation(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getResource(3)

    def setIcon(self, value):
        self._setResource(3, value)

    def getInventoryCount(self):
        return self._getNumber(4)

    def setInventoryCount(self, value):
        self._setNumber(4, value)

    def getNewAmount(self):
        return self._getNumber(5)

    def setNewAmount(self, value):
        self._setNumber(5, value)

    def getRestrictions(self):
        return self._getArray(6)

    def setRestrictions(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRestrictionsType():
        return unicode

    def getCardState(self):
        return DataCardState(self._getString(7))

    def setCardState(self, value):
        self._setString(7, value.value)

    def getCardType(self):
        return DataCardType(self._getString(8))

    def setCardType(self, value):
        self._setString(8, value.value)

    def _initialize(self):
        super(PersonalDataCardModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('nation', '')
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('inventoryCount', 0)
        self._addNumberProperty('newAmount', 0)
        self._addArrayProperty('restrictions', Array())
        self._addStringProperty('cardState')
        self._addStringProperty('cardType')

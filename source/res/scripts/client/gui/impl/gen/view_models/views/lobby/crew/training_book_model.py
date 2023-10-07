# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/training_book_model.py
from frameworks.wulf import ViewModel

class TrainingBookModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(TrainingBookModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(0)

    def setIntCD(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def getMainText(self):
        return self._getString(4)

    def setMainText(self, value):
        self._setString(4, value)

    def getAdditionalText(self):
        return self._getString(5)

    def setAdditionalText(self, value):
        self._setString(5, value)

    def getBookAddedXp(self):
        return self._getNumber(6)

    def setBookAddedXp(self, value):
        self._setNumber(6, value)

    def getAvailableCount(self):
        return self._getNumber(7)

    def setAvailableCount(self, value):
        self._setNumber(7, value)

    def getSelectedCount(self):
        return self._getNumber(8)

    def setSelectedCount(self, value):
        self._setNumber(8, value)

    def getIsEligibleForBuy(self):
        return self._getBool(9)

    def setIsEligibleForBuy(self, value):
        self._setBool(9, value)

    def getHasError(self):
        return self._getBool(10)

    def setHasError(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(TrainingBookModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('type', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('title', '')
        self._addStringProperty('mainText', '')
        self._addStringProperty('additionalText', '')
        self._addNumberProperty('bookAddedXp', 0)
        self._addNumberProperty('availableCount', 0)
        self._addNumberProperty('selectedCount', 0)
        self._addBoolProperty('isEligibleForBuy', False)
        self._addBoolProperty('hasError', False)

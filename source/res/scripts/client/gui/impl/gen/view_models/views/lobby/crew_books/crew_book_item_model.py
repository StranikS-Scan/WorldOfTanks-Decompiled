# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew_books/crew_book_item_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CrewBookItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(CrewBookItemModel, self).__init__(properties=properties, commands=commands)

    def getBookIcon(self):
        return self._getResource(0)

    def setBookIcon(self, value):
        self._setResource(0, value)

    def getCompactDesc(self):
        return self._getNumber(1)

    def setCompactDesc(self, value):
        self._setNumber(1, value)

    def getAmount(self):
        return self._getNumber(2)

    def setAmount(self, value):
        self._setNumber(2, value)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def getIsDisabled(self):
        return self._getBool(4)

    def setIsDisabled(self, value):
        self._setBool(4, value)

    def getTitle(self):
        return self._getResource(5)

    def setTitle(self, value):
        self._setResource(5, value)

    def getDescription(self):
        return self._getResource(6)

    def setDescription(self, value):
        self._setResource(6, value)

    def getDescriptionFmtArgs(self):
        return self._getArray(7)

    def setDescriptionFmtArgs(self, value):
        self._setArray(7, value)

    def getOverlayDescription(self):
        return self._getResource(8)

    def setOverlayDescription(self, value):
        self._setResource(8, value)

    def getOverlayDescriptionFmtArgs(self):
        return self._getArray(9)

    def setOverlayDescriptionFmtArgs(self, value):
        self._setArray(9, value)

    def getIsInShop(self):
        return self._getBool(10)

    def setIsInShop(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(CrewBookItemModel, self)._initialize()
        self._addResourceProperty('bookIcon', R.invalid())
        self._addNumberProperty('compactDesc', 0)
        self._addNumberProperty('amount', 0)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isDisabled', False)
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addArrayProperty('descriptionFmtArgs', Array())
        self._addResourceProperty('overlayDescription', R.invalid())
        self._addArrayProperty('overlayDescriptionFmtArgs', Array())
        self._addBoolProperty('isInShop', False)

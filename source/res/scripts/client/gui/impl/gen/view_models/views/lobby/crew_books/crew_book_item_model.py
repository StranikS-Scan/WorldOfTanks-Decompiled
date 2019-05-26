# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew_books/crew_book_item_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CrewBookItemModel(ViewModel):
    __slots__ = ()

    def getIdx(self):
        return self._getNumber(0)

    def setIdx(self, value):
        self._setNumber(0, value)

    def getBookIcon(self):
        return self._getResource(1)

    def setBookIcon(self, value):
        self._setResource(1, value)

    def getCompactDesc(self):
        return self._getNumber(2)

    def setCompactDesc(self, value):
        self._setNumber(2, value)

    def getAmount(self):
        return self._getNumber(3)

    def setAmount(self, value):
        self._setNumber(3, value)

    def getIsSelected(self):
        return self._getBool(4)

    def setIsSelected(self, value):
        self._setBool(4, value)

    def getIsDisabled(self):
        return self._getBool(5)

    def setIsDisabled(self, value):
        self._setBool(5, value)

    def getTitle(self):
        return self._getResource(6)

    def setTitle(self, value):
        self._setResource(6, value)

    def getDescription(self):
        return self._getResource(7)

    def setDescription(self, value):
        self._setResource(7, value)

    def getDescriptionFmtArgs(self):
        return self._getArray(8)

    def setDescriptionFmtArgs(self, value):
        self._setArray(8, value)

    def getOverlayDescription(self):
        return self._getResource(9)

    def setOverlayDescription(self, value):
        self._setResource(9, value)

    def getOverlayDescriptionFmtArgs(self):
        return self._getArray(10)

    def setOverlayDescriptionFmtArgs(self, value):
        self._setArray(10, value)

    def getIsInShop(self):
        return self._getBool(11)

    def setIsInShop(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(CrewBookItemModel, self)._initialize()
        self._addNumberProperty('idx', 0)
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

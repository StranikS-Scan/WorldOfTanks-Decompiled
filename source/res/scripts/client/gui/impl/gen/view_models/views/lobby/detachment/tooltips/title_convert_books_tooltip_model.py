# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/title_convert_books_tooltip_model.py
from frameworks.wulf import ViewModel

class TitleConvertBooksTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TitleConvertBooksTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBooksCount(self):
        return self._getNumber(0)

    def setBooksCount(self, value):
        self._setNumber(0, value)

    def getExpCount(self):
        return self._getNumber(1)

    def setExpCount(self, value):
        self._setNumber(1, value)

    def getRecruitsCount(self):
        return self._getNumber(2)

    def setRecruitsCount(self, value):
        self._setNumber(2, value)

    def getShowPersonal(self):
        return self._getBool(3)

    def setShowPersonal(self, value):
        self._setBool(3, value)

    def getShowNation(self):
        return self._getBool(4)

    def setShowNation(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(TitleConvertBooksTooltipModel, self)._initialize()
        self._addNumberProperty('booksCount', 0)
        self._addNumberProperty('expCount', 0)
        self._addNumberProperty('recruitsCount', 0)
        self._addBoolProperty('showPersonal', False)
        self._addBoolProperty('showNation', False)

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/conversion_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.conversion_tooltip_book_model import ConversionTooltipBookModel

class ConversionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ConversionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getBooksList(self):
        return self._getArray(2)

    def setBooksList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBooksListType():
        return ConversionTooltipBookModel

    def _initialize(self):
        super(ConversionTooltipModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addArrayProperty('booksList', Array())

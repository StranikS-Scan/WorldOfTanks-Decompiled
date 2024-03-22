# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/conversion_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.conversion_tooltip_book_model import ConversionTooltipBookModel

class ConversionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ConversionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsReceived(self):
        return self._getBool(0)

    def setIsReceived(self, value):
        self._setBool(0, value)

    def getBooksList(self):
        return self._getArray(1)

    def setBooksList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBooksListType():
        return ConversionTooltipBookModel

    def _initialize(self):
        super(ConversionTooltipModel, self)._initialize()
        self._addBoolProperty('isReceived', False)
        self._addArrayProperty('booksList', Array())

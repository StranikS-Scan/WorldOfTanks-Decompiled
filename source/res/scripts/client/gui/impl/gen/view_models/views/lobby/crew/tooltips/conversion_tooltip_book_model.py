# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/conversion_tooltip_book_model.py
from frameworks.wulf import ViewModel

class ConversionTooltipBookModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ConversionTooltipBookModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getNation(self):
        return self._getString(2)

    def setNation(self, value):
        self._setString(2, value)

    def getValue(self):
        return self._getNumber(3)

    def setValue(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ConversionTooltipBookModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('title', '')
        self._addStringProperty('nation', '')
        self._addNumberProperty('value', 0)

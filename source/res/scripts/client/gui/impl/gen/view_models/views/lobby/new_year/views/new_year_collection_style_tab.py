# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_collection_style_tab.py
from frameworks.wulf import ViewModel

class NewYearCollectionStyleTab(ViewModel):
    __slots__ = ('onCollectionNameChanged',)

    def __init__(self, properties=5, commands=1):
        super(NewYearCollectionStyleTab, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getYear(self):
        return self._getString(1)

    def setYear(self, value):
        self._setString(1, value)

    def getCount(self):
        return self._getNumber(2)

    def setCount(self, value):
        self._setNumber(2, value)

    def getTotal(self):
        return self._getNumber(3)

    def setTotal(self, value):
        self._setNumber(3, value)

    def getIsSelected(self):
        return self._getBool(4)

    def setIsSelected(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NewYearCollectionStyleTab, self)._initialize()
        self._addStringProperty('name', 'NewYear')
        self._addStringProperty('year', 'ny21')
        self._addNumberProperty('count', 0)
        self._addNumberProperty('total', 0)
        self._addBoolProperty('isSelected', False)
        self.onCollectionNameChanged = self._addCommand('onCollectionNameChanged')

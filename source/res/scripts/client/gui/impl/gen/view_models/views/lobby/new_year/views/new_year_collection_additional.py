# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_collection_additional.py
from frameworks.wulf import ViewModel

class NewYearCollectionAdditional(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearCollectionAdditional, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getString(0)

    def setCount(self, value):
        self._setString(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getItemType(self):
        return self._getString(2)

    def setItemType(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(NewYearCollectionAdditional, self)._initialize()
        self._addStringProperty('count', 'x1')
        self._addNumberProperty('id', 0)
        self._addStringProperty('itemType', '')

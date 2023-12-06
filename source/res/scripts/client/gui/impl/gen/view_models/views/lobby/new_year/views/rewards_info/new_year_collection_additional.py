# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/rewards_info/new_year_collection_additional.py
from frameworks.wulf import ViewModel

class NewYearCollectionAdditional(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NewYearCollectionAdditional, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getItemType(self):
        return self._getString(2)

    def setItemType(self, value):
        self._setString(2, value)

    def getTooltipId(self):
        return self._getNumber(3)

    def setTooltipId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(NewYearCollectionAdditional, self)._initialize()
        self._addNumberProperty('count', 1)
        self._addStringProperty('name', '')
        self._addStringProperty('itemType', '')
        self._addNumberProperty('tooltipId', 0)

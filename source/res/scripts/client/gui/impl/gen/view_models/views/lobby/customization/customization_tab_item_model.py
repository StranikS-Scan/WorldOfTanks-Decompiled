# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_tab_item_model.py
from frameworks.wulf import ViewModel

class CustomizationTabItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CustomizationTabItemModel, self).__init__(properties=properties, commands=commands)

    def getGroupId(self):
        return self._getNumber(0)

    def setGroupId(self, value):
        self._setNumber(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getItemType(self):
        return self._getString(2)

    def setItemType(self, value):
        self._setString(2, value)

    def getIsPlus(self):
        return self._getBool(3)

    def setIsPlus(self, value):
        self._setBool(3, value)

    def getNoveltyCounter(self):
        return self._getNumber(4)

    def setNoveltyCounter(self, value):
        self._setNumber(4, value)

    def getIsSelected(self):
        return self._getBool(5)

    def setIsSelected(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(CustomizationTabItemModel, self)._initialize()
        self._addNumberProperty('groupId', 0)
        self._addNumberProperty('id', 0)
        self._addStringProperty('itemType', '')
        self._addBoolProperty('isPlus', False)
        self._addNumberProperty('noveltyCounter', 0)
        self._addBoolProperty('isSelected', False)

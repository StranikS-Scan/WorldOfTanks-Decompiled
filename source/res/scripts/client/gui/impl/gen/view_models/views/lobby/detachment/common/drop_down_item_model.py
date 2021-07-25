# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/drop_down_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DropDownItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DropDownItemModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsSelected(self):
        return self._getBool(3)

    def setIsSelected(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(DropDownItemModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('title', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isSelected', False)

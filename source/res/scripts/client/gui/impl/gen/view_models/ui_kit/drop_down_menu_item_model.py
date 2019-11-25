# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/drop_down_menu_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DropDownMenuItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DropDownMenuItemModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getId(self):
        return self._getNumber(3)

    def setId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(DropDownMenuItemModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('id', 0)

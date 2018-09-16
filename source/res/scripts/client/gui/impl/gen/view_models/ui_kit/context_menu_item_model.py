# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/context_menu_item_model.py
from frameworks.wulf.gui_constants import ResourceValue
from frameworks.wulf import ViewModel

class ContextMenuItemModel(ViewModel):
    __slots__ = ('onItemClicked',)

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

    def getIsSeparator(self):
        return self._getBool(3)

    def setIsSeparator(self, value):
        self._setBool(3, value)

    def getHasSubItems(self):
        return self._getBool(4)

    def setHasSubItems(self, value):
        self._setBool(4, value)

    def getIsSubItem(self):
        return self._getBool(5)

    def setIsSubItem(self, value):
        self._setBool(5, value)

    def getId(self):
        return self._getNumber(6)

    def setId(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        self._addResourceProperty('label', ResourceValue.DEFAULT)
        self._addResourceProperty('icon', ResourceValue.DEFAULT)
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isSeparator', False)
        self._addBoolProperty('hasSubItems', False)
        self._addBoolProperty('isSubItem', False)
        self._addNumberProperty('id', 0)
        self.onItemClicked = self._addCommand('onItemClicked')

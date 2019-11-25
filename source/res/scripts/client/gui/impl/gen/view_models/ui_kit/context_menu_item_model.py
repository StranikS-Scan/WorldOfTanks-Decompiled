# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/context_menu_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class ContextMenuItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(ContextMenuItemModel, self).__init__(properties=properties, commands=commands)

    @property
    def subItemsList(self):
        return self._getViewModel(0)

    def getLabel(self):
        return self._getResource(1)

    def setLabel(self, value):
        self._setResource(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getIsSeparator(self):
        return self._getBool(4)

    def setIsSeparator(self, value):
        self._setBool(4, value)

    def getId(self):
        return self._getNumber(5)

    def setId(self, value):
        self._setNumber(5, value)

    def getSubItemsCount(self):
        return self._getNumber(6)

    def setSubItemsCount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ContextMenuItemModel, self)._initialize()
        self._addViewModelProperty('subItemsList', ListModel())
        self._addResourceProperty('label', R.invalid())
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('isSeparator', False)
        self._addNumberProperty('id', 0)
        self._addNumberProperty('subItemsCount', 0)

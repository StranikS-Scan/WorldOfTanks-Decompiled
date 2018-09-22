# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/context_menu_sub_item_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class ContextMenuSubItemModel(ViewModel):
    __slots__ = ()

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
        super(ContextMenuSubItemModel, self)._initialize()
        self._addResourceProperty('label', Resource.INVALID)
        self._addResourceProperty('icon', Resource.INVALID)
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('id', 0)

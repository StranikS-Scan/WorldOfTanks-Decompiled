# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/context_menu_content_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class ContextMenuContentModel(ViewModel):
    __slots__ = ('onItemClicked',)

    @property
    def contextMenuList(self):
        return self._getViewModel(0)

    def getItemsCount(self):
        return self._getNumber(1)

    def setItemsCount(self, value):
        self._setNumber(1, value)

    def getSeparatorsCount(self):
        return self._getNumber(2)

    def setSeparatorsCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ContextMenuContentModel, self)._initialize()
        self._addViewModelProperty('contextMenuList', ListModel())
        self._addNumberProperty('itemsCount', 0)
        self._addNumberProperty('separatorsCount', 0)
        self.onItemClicked = self._addCommand('onItemClicked')

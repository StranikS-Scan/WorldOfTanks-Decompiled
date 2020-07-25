# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/demount_kit/selector_dialog_model.py
from gui.impl.gen.view_models.views.lobby.demount_kit.item_base_dialog_model import ItemBaseDialogModel
from gui.impl.gen.view_models.views.lobby.demount_kit.selector_dialog_item_model import SelectorDialogItemModel

class SelectorDialogModel(ItemBaseDialogModel):
    __slots__ = ('onSelectItem',)

    def __init__(self, properties=15, commands=4):
        super(SelectorDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def firstItem(self):
        return self._getViewModel(12)

    @property
    def secondItem(self):
        return self._getViewModel(13)

    def getSelectedItem(self):
        return self._getString(14)

    def setSelectedItem(self, value):
        self._setString(14, value)

    def _initialize(self):
        super(SelectorDialogModel, self)._initialize()
        self._addViewModelProperty('firstItem', SelectorDialogItemModel())
        self._addViewModelProperty('secondItem', SelectorDialogItemModel())
        self._addStringProperty('selectedItem', '')
        self.onSelectItem = self._addCommand('onSelectItem')

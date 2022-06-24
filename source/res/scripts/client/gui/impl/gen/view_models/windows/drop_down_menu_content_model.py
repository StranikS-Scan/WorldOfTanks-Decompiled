# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/drop_down_menu_content_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class DropDownMenuContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DropDownMenuContentModel, self).__init__(properties=properties, commands=commands)

    @property
    def dropDownList(self):
        return self._getViewModel(0)

    @staticmethod
    def getDropDownListType():
        return ListModel

    def getListItemRenderer(self):
        return self._getString(1)

    def setListItemRenderer(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(DropDownMenuContentModel, self)._initialize()
        self._addViewModelProperty('dropDownList', ListModel())
        self._addStringProperty('listItemRenderer', '')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/dropdown_item.py
from gui.impl.gen.view_models.ui_kit.gf_drop_down_item import GfDropDownItem
from gui.impl.gen.view_models.views.lobby.platoon.dropdown_item_meta import DropdownItemMeta

class DropdownItem(GfDropDownItem):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DropdownItem, self).__init__(properties=properties, commands=commands)

    @property
    def meta(self):
        return self._getViewModel(3)

    @staticmethod
    def getMetaType():
        return DropdownItemMeta

    def _initialize(self):
        super(DropdownItem, self)._initialize()
        self._addViewModelProperty('meta', DropdownItemMeta())

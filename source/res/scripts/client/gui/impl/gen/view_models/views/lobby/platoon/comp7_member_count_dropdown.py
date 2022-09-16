# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/comp7_member_count_dropdown.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.ui_kit.gf_drop_down_model import GfDropDownModel
from gui.impl.gen.view_models.views.lobby.platoon.comp7_dropdown_item import Comp7DropdownItem

class Comp7MemberCountDropdown(GfDropDownModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=1):
        super(Comp7MemberCountDropdown, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(3)

    def setItems(self, value):
        self._setArray(3, value)

    @staticmethod
    def getItemsType():
        return Comp7DropdownItem

    def getIsDisabled(self):
        return self._getBool(4)

    def setIsDisabled(self, value):
        self._setBool(4, value)

    def getTooltipText(self):
        return self._getString(5)

    def setTooltipText(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(Comp7MemberCountDropdown, self)._initialize()
        self._addArrayProperty('items', Array())
        self._addBoolProperty('isDisabled', False)
        self._addStringProperty('tooltipText', '')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/dropdown_item_meta.py
from frameworks.wulf import ViewModel

class DropdownItemMeta(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(DropdownItemMeta, self).__init__(properties=properties, commands=commands)

    def getTooltipText(self):
        return self._getString(0)

    def setTooltipText(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(DropdownItemMeta, self)._initialize()
        self._addStringProperty('tooltipText', '')

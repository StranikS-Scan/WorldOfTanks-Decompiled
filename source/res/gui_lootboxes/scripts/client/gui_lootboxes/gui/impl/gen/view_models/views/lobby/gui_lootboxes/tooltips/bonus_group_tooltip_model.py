# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/bonus_group_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.bg_tooltip_row_model import BgTooltipRowModel

class BonusGroupTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BonusGroupTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBonusGroup(self):
        return self._getString(0)

    def setBonusGroup(self, value):
        self._setString(0, value)

    def getBonusRows(self):
        return self._getArray(1)

    def setBonusRows(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusRowsType():
        return BgTooltipRowModel

    def _initialize(self):
        super(BonusGroupTooltipModel, self)._initialize()
        self._addStringProperty('bonusGroup', '')
        self._addArrayProperty('bonusRows', Array())

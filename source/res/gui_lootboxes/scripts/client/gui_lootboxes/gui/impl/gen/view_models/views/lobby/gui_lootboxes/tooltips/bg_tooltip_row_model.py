# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/bg_tooltip_row_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lb_bonus_type_model import LbBonusTypeModel

class BgTooltipRowModel(LbBonusTypeModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BgTooltipRowModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(1)

    def setBonuses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(BgTooltipRowModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())

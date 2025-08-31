# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_bonus_group_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class WtBonusGroupTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtBonusGroupTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBonusGroup(self):
        return self._getString(0)

    def setBonusGroup(self, value):
        self._setString(0, value)

    def getBonuses(self):
        return self._getArray(1)

    def setBonuses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusesType():
        return ItemBonusModel

    def _initialize(self):
        super(WtBonusGroupTooltipModel, self)._initialize()
        self._addStringProperty('bonusGroup', '')
        self._addArrayProperty('bonuses', Array())

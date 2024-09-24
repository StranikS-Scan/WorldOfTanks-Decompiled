# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/trade_in_nation_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.trade_in_branch_view_model import TradeInBranchViewModel

class TradeInNationViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TradeInNationViewModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(0)

    def setNation(self, value):
        self._setString(0, value)

    def getBranches(self):
        return self._getArray(1)

    def setBranches(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBranchesType():
        return TradeInBranchViewModel

    def _initialize(self):
        super(TradeInNationViewModel, self)._initialize()
        self._addStringProperty('nation', '0')
        self._addArrayProperty('branches', Array())

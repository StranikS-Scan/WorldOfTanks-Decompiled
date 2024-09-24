# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/post_trade_view_model.py
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.trade_in_branch_view_model import TradeInBranchViewModel

class PostTradeViewModel(ViewModel):
    __slots__ = ('onConfirm',)

    def __init__(self, properties=2, commands=1):
        super(PostTradeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def branchToReceive(self):
        return self._getViewModel(0)

    @staticmethod
    def getBranchToReceiveType():
        return TradeInBranchViewModel

    def getNation(self):
        return self._getString(1)

    def setNation(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(PostTradeViewModel, self)._initialize()
        self._addViewModelProperty('branchToReceive', TradeInBranchViewModel())
        self._addStringProperty('nation', '')
        self.onConfirm = self._addCommand('onConfirm')

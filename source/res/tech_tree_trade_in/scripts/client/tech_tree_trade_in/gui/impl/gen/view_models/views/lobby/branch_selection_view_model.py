# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/branch_selection_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.trade_in_nation_view_model import TradeInNationViewModel

class BranchSelectionViewModel(ViewModel):
    __slots__ = ('onSelectBranchToTradeId', 'onSelectBranchToReceiveId', 'onConfirm')

    def __init__(self, properties=5, commands=3):
        super(BranchSelectionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getBranchesToTrade(self):
        return self._getArray(1)

    def setBranchesToTrade(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBranchesToTradeType():
        return TradeInNationViewModel

    def getBranchesToReceive(self):
        return self._getArray(2)

    def setBranchesToReceive(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBranchesToReceiveType():
        return TradeInNationViewModel

    def getSelectedBranchToTradeId(self):
        return self._getNumber(3)

    def setSelectedBranchToTradeId(self, value):
        self._setNumber(3, value)

    def getSelectedBranchToReceiveId(self):
        return self._getNumber(4)

    def setSelectedBranchToReceiveId(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(BranchSelectionViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addArrayProperty('branchesToTrade', Array())
        self._addArrayProperty('branchesToReceive', Array())
        self._addNumberProperty('selectedBranchToTradeId', 0)
        self._addNumberProperty('selectedBranchToReceiveId', 0)
        self.onSelectBranchToTradeId = self._addCommand('onSelectBranchToTradeId')
        self.onSelectBranchToReceiveId = self._addCommand('onSelectBranchToReceiveId')
        self.onConfirm = self._addCommand('onConfirm')

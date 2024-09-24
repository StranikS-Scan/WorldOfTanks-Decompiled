# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/summary_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.branch_info_view_model import BranchInfoViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.vehicle_properties_view_model import VehiclePropertiesViewModel

class SummaryViewModel(ViewModel):
    __slots__ = ()
    VEHICLE_NOT_TRADED_RESEARCH = 'notTradedResearch'
    VEHICLE_NOT_TRADED_RESEARCH_INVENTORY = 'notTradedResearchInventory'
    VEHICLE_TRADED_RESEARCH = 'tradedResearch'
    VEHICLE_TRADED_RESEARCH_INVENTORY = 'tradedResearchInventory'

    def __init__(self, properties=3, commands=0):
        super(SummaryViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def branchToGive(self):
        return self._getViewModel(0)

    @staticmethod
    def getBranchToGiveType():
        return BranchInfoViewModel

    @property
    def branchToReceive(self):
        return self._getViewModel(1)

    @staticmethod
    def getBranchToReceiveType():
        return BranchInfoViewModel

    def getVehicleProperties(self):
        return self._getArray(2)

    def setVehicleProperties(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclePropertiesType():
        return VehiclePropertiesViewModel

    def _initialize(self):
        super(SummaryViewModel, self)._initialize()
        self._addViewModelProperty('branchToGive', BranchInfoViewModel())
        self._addViewModelProperty('branchToReceive', BranchInfoViewModel())
        self._addArrayProperty('vehicleProperties', Array())

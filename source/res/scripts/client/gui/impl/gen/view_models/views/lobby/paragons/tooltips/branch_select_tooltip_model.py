# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/branch_select_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.paragons_vehicle_model import ParagonsVehicleModel

class BranchSelectTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BranchSelectTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicles(self):
        return self._getArray(0)

    def setVehicles(self, value):
        self._setArray(0, value)

    @staticmethod
    def getVehiclesType():
        return ParagonsVehicleModel

    def _initialize(self):
        super(BranchSelectTooltipModel, self)._initialize()
        self._addArrayProperty('vehicles', Array())

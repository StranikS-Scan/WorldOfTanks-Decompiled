# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/tooltips/vehicle_tabs_tooltip_model.py
from frameworks.wulf import ViewModel

class VehicleTabsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(VehicleTabsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getMinVehicleLevel(self):
        return self._getNumber(0)

    def setMinVehicleLevel(self, value):
        self._setNumber(0, value)

    def getMaxVehicleLevel(self):
        return self._getNumber(1)

    def setMaxVehicleLevel(self, value):
        self._setNumber(1, value)

    def getBranchName(self):
        return self._getString(2)

    def setBranchName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(VehicleTabsTooltipModel, self)._initialize()
        self._addNumberProperty('minVehicleLevel', 0)
        self._addNumberProperty('maxVehicleLevel', 0)
        self._addStringProperty('branchName', '')

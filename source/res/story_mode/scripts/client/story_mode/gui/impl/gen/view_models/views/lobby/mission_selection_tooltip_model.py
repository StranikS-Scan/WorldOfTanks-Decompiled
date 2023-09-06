# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/mission_selection_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class MissionSelectionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(MissionSelectionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getResource(0)

    def setVehicleName(self, value):
        self._setResource(0, value)

    def getVehicleIcon(self):
        return self._getResource(1)

    def setVehicleIcon(self, value):
        self._setResource(1, value)

    def getVehicleDescription(self):
        return self._getResource(2)

    def setVehicleDescription(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(MissionSelectionTooltipModel, self)._initialize()
        self._addResourceProperty('vehicleName', R.invalid())
        self._addResourceProperty('vehicleIcon', R.invalid())
        self._addResourceProperty('vehicleDescription', R.invalid())

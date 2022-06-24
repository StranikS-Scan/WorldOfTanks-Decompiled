# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/resources_loading_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.resource_well.resources_tab_model import ResourcesTabModel
from gui.impl.gen.view_models.views.lobby.resource_well.vehicle_counter_model import VehicleCounterModel

class ProgressionState(Enum):
    ACTIVE = 'active'
    NOPROGRESS = 'noProgress'
    NOVEHICLES = 'noVehicles'


class ResourcesLoadingViewModel(ViewModel):
    __slots__ = ('showHangar', 'loadResources')

    def __init__(self, properties=5, commands=2):
        super(ResourcesLoadingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleCounter(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleCounterType():
        return VehicleCounterModel

    def getProgressionState(self):
        return ProgressionState(self._getString(1))

    def setProgressionState(self, value):
        self._setString(1, value.value)

    def getProgression(self):
        return self._getNumber(2)

    def setProgression(self, value):
        self._setNumber(2, value)

    def getResourcesTabs(self):
        return self._getArray(3)

    def setResourcesTabs(self, value):
        self._setArray(3, value)

    @staticmethod
    def getResourcesTabsType():
        return ResourcesTabModel

    def getIsLoadingError(self):
        return self._getBool(4)

    def setIsLoadingError(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ResourcesLoadingViewModel, self)._initialize()
        self._addViewModelProperty('vehicleCounter', VehicleCounterModel())
        self._addStringProperty('progressionState')
        self._addNumberProperty('progression', 0)
        self._addArrayProperty('resourcesTabs', Array())
        self._addBoolProperty('isLoadingError', False)
        self.showHangar = self._addCommand('showHangar')
        self.loadResources = self._addCommand('loadResources')

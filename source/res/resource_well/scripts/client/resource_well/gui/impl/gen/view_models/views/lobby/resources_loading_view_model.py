# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/resources_loading_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from resource_well.gui.impl.gen.view_models.views.lobby.resources_tab_model import ResourcesTabModel
from resource_well.gui.impl.gen.view_models.views.lobby.vehicle_counter_model import VehicleCounterModel

class ProgressionState(Enum):
    ACTIVE = 'active'
    NOPROGRESS = 'noProgress'
    NOVEHICLES = 'noVehicles'


class ResourcesLoadingViewModel(ViewModel):
    __slots__ = ('showHangar', 'close', 'loadResources')

    def __init__(self, properties=6, commands=3):
        super(ResourcesLoadingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleCounter(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleCounterType():
        return VehicleCounterModel

    @property
    def vehicleInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getProgressionState(self):
        return ProgressionState(self._getString(2))

    def setProgressionState(self, value):
        self._setString(2, value.value)

    def getProgression(self):
        return self._getNumber(3)

    def setProgression(self, value):
        self._setNumber(3, value)

    def getResourcesTabs(self):
        return self._getArray(4)

    def setResourcesTabs(self, value):
        self._setArray(4, value)

    @staticmethod
    def getResourcesTabsType():
        return ResourcesTabModel

    def getIsLoadingError(self):
        return self._getBool(5)

    def setIsLoadingError(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ResourcesLoadingViewModel, self)._initialize()
        self._addViewModelProperty('vehicleCounter', VehicleCounterModel())
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addStringProperty('progressionState')
        self._addNumberProperty('progression', 0)
        self._addArrayProperty('resourcesTabs', Array())
        self._addBoolProperty('isLoadingError', False)
        self.showHangar = self._addCommand('showHangar')
        self.close = self._addCommand('close')
        self.loadResources = self._addCommand('loadResources')

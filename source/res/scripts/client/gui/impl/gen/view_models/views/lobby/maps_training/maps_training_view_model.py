# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/maps_training/maps_training_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.maps_training.maps_training_group_model import MapsTrainingGroupModel
from gui.impl.gen.view_models.views.lobby.maps_training.maps_training_map_model import MapsTrainingMapModel
from gui.impl.gen.view_models.views.lobby.maps_training.maps_training_selected_map_model import MapsTrainingSelectedMapModel
from gui.impl.gen.view_models.views.lobby.maps_training.maps_training_vehicle_marker_model import MapsTrainingVehicleMarkerModel

class MapsTrainingViewModel(ViewModel):
    __slots__ = ('onBack', 'onSelect', 'onScenarioSelect', 'onFilteringChange', 'onBlurRectUpdated', 'onMoveSpace', 'onInfoClicked', 'onClose')

    def __init__(self, properties=8, commands=8):
        super(MapsTrainingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selectedMapModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getSelectedMapModelType():
        return MapsTrainingSelectedMapModel

    @property
    def vehicleMarker(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleMarkerType():
        return MapsTrainingVehicleMarkerModel

    def getIsMapSelected(self):
        return self._getBool(2)

    def setIsMapSelected(self, value):
        self._setBool(2, value)

    def getIncompleteFilter(self):
        return self._getBool(3)

    def setIncompleteFilter(self, value):
        self._setBool(3, value)

    def getTitleFilter(self):
        return self._getString(4)

    def setTitleFilter(self, value):
        self._setString(4, value)

    def getIsDataLoaded(self):
        return self._getBool(5)

    def setIsDataLoaded(self, value):
        self._setBool(5, value)

    def getMaps(self):
        return self._getArray(6)

    def setMaps(self, value):
        self._setArray(6, value)

    @staticmethod
    def getMapsType():
        return MapsTrainingMapModel

    def getGroups(self):
        return self._getArray(7)

    def setGroups(self, value):
        self._setArray(7, value)

    @staticmethod
    def getGroupsType():
        return MapsTrainingGroupModel

    def _initialize(self):
        super(MapsTrainingViewModel, self)._initialize()
        self._addViewModelProperty('selectedMapModel', MapsTrainingSelectedMapModel())
        self._addViewModelProperty('vehicleMarker', MapsTrainingVehicleMarkerModel())
        self._addBoolProperty('isMapSelected', False)
        self._addBoolProperty('incompleteFilter', False)
        self._addStringProperty('titleFilter', '')
        self._addBoolProperty('isDataLoaded', False)
        self._addArrayProperty('maps', Array())
        self._addArrayProperty('groups', Array())
        self.onBack = self._addCommand('onBack')
        self.onSelect = self._addCommand('onSelect')
        self.onScenarioSelect = self._addCommand('onScenarioSelect')
        self.onFilteringChange = self._addCommand('onFilteringChange')
        self.onBlurRectUpdated = self._addCommand('onBlurRectUpdated')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onInfoClicked = self._addCommand('onInfoClicked')
        self.onClose = self._addCommand('onClose')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/popovers/vehicle_selector_popover_content_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.drop_down_item_model import DropDownItemModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.vehicle_selector_list_item_model import VehicleSelectorListItemModel

class VehicleSelectorPopoverContentModel(ViewModel):
    __slots__ = ('onLevelChange', 'onTypeChange', 'onToggleShowOnlyVehiclesInHangar', 'onVehicleSelect', 'onSortingChange', 'onFiltersReset')
    SORTING_BY_TYPE = 'type'
    SORTING_BY_LEVEL = 'level'
    SORTING_BY_NAME = 'name'
    SORTING_BY_STATUS = 'hangar'

    def __init__(self, properties=7, commands=6):
        super(VehicleSelectorPopoverContentModel, self).__init__(properties=properties, commands=commands)

    def getLevels(self):
        return self._getArray(0)

    def setLevels(self, value):
        self._setArray(0, value)

    def getTypes(self):
        return self._getArray(1)

    def setTypes(self, value):
        self._setArray(1, value)

    def getIsShowOnlyVehiclesInHangar(self):
        return self._getBool(2)

    def setIsShowOnlyVehiclesInHangar(self, value):
        self._setBool(2, value)

    def getSelectedSortTab(self):
        return self._getString(3)

    def setSelectedSortTab(self, value):
        self._setString(3, value)

    def getSelectedSortTabState(self):
        return self._getNumber(4)

    def setSelectedSortTabState(self, value):
        self._setNumber(4, value)

    def getSelectedVehicle(self):
        return self._getNumber(5)

    def setSelectedVehicle(self, value):
        self._setNumber(5, value)

    def getVehicleList(self):
        return self._getArray(6)

    def setVehicleList(self, value):
        self._setArray(6, value)

    def _initialize(self):
        super(VehicleSelectorPopoverContentModel, self)._initialize()
        self._addArrayProperty('levels', Array())
        self._addArrayProperty('types', Array())
        self._addBoolProperty('isShowOnlyVehiclesInHangar', False)
        self._addStringProperty('selectedSortTab', '')
        self._addNumberProperty('selectedSortTabState', 0)
        self._addNumberProperty('selectedVehicle', 0)
        self._addArrayProperty('vehicleList', Array())
        self.onLevelChange = self._addCommand('onLevelChange')
        self.onTypeChange = self._addCommand('onTypeChange')
        self.onToggleShowOnlyVehiclesInHangar = self._addCommand('onToggleShowOnlyVehiclesInHangar')
        self.onVehicleSelect = self._addCommand('onVehicleSelect')
        self.onSortingChange = self._addCommand('onSortingChange')
        self.onFiltersReset = self._addCommand('onFiltersReset')

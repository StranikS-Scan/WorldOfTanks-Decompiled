# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_vehicles_selection_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.popovers.filter_control_view_model import FilterControlViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_vehicle_model import TankAcademyVehicleModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_vehicles_selection_tabs_model import TankAcademyVehiclesSelectionTabsModel

class TankAcademyVehiclesSelectionViewModel(ViewModel):
    __slots__ = ('onGoBack', 'onShowVehicle', 'onCompareVehicle', 'onResetFilter', 'onSelectTab')
    ARG_VEHICLE_ID = 'vehCD'
    ARG_TAB_LEVEL = 'level'
    ARG_TAB_IS_PREMIUM = 'isPremium'

    def __init__(self, properties=6, commands=5):
        super(TankAcademyVehiclesSelectionViewModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getNumber(0)

    def setEndDate(self, value):
        self._setNumber(0, value)

    def getTotalVehiclesCount(self):
        return self._getNumber(1)

    def setTotalVehiclesCount(self, value):
        self._setNumber(1, value)

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return TankAcademyVehicleModel

    def getTabs(self):
        return self._getArray(3)

    def setTabs(self, value):
        self._setArray(3, value)

    @staticmethod
    def getTabsType():
        return TankAcademyVehiclesSelectionTabsModel

    def getTypes(self):
        return self._getArray(4)

    def setTypes(self, value):
        self._setArray(4, value)

    @staticmethod
    def getTypesType():
        return FilterControlViewModel

    def getNations(self):
        return self._getArray(5)

    def setNations(self, value):
        self._setArray(5, value)

    @staticmethod
    def getNationsType():
        return FilterControlViewModel

    def _initialize(self):
        super(TankAcademyVehiclesSelectionViewModel, self)._initialize()
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('totalVehiclesCount', 0)
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('tabs', Array())
        self._addArrayProperty('types', Array())
        self._addArrayProperty('nations', Array())
        self.onGoBack = self._addCommand('onGoBack')
        self.onShowVehicle = self._addCommand('onShowVehicle')
        self.onCompareVehicle = self._addCommand('onCompareVehicle')
        self.onResetFilter = self._addCommand('onResetFilter')
        self.onSelectTab = self._addCommand('onSelectTab')

# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tankman_container_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.crew.common.base_crew_view_model import BaseCrewViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_container_tab_model import TankmanContainerTabModel

class TankmanContainerViewModel(BaseCrewViewModel):
    __slots__ = ('onTabChange',)

    def __init__(self, properties=9, commands=5):
        super(TankmanContainerViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(2)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getCurrentTabId(self):
        return self._getNumber(3)

    def setCurrentTabId(self, value):
        self._setNumber(3, value)

    def getBackground(self):
        return self._getString(4)

    def setBackground(self, value):
        self._setString(4, value)

    def getTabs(self):
        return self._getArray(5)

    def setTabs(self, value):
        self._setArray(5, value)

    @staticmethod
    def getTabsType():
        return TankmanContainerTabModel

    def getNation(self):
        return self._getString(6)

    def setNation(self, value):
        self._setString(6, value)

    def getBackButtonLabel(self):
        return self._getResource(7)

    def setBackButtonLabel(self, value):
        self._setResource(7, value)

    def getIsContentVisible(self):
        return self._getBool(8)

    def setIsContentVisible(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(TankmanContainerViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('currentTabId', 0)
        self._addStringProperty('background', '')
        self._addArrayProperty('tabs', Array())
        self._addStringProperty('nation', '')
        self._addResourceProperty('backButtonLabel', R.invalid())
        self._addBoolProperty('isContentVisible', True)
        self.onTabChange = self._addCommand('onTabChange')

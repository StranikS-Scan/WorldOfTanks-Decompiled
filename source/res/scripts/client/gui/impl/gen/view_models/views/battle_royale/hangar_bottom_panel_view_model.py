# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/hangar_bottom_panel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class HangarBottomPanelViewModel(ViewModel):
    __slots__ = ('onRentBtnClicked', 'onRepairBtnClicked')

    def __init__(self, properties=11, commands=2):
        super(HangarBottomPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def ammunition(self):
        return self._getViewModel(0)

    @property
    def abilities(self):
        return self._getViewModel(1)

    @property
    def rentPrice(self):
        return self._getViewModel(2)

    def getVehName(self):
        return self._getString(3)

    def setVehName(self, value):
        self._setString(3, value)

    def getVehType(self):
        return self._getString(4)

    def setVehType(self, value):
        self._setString(4, value)

    def getRentState(self):
        return self._getString(5)

    def setRentState(self, value):
        self._setString(5, value)

    def getRentDays(self):
        return self._getNumber(6)

    def setRentDays(self, value):
        self._setNumber(6, value)

    def getRentTime(self):
        return self._getString(7)

    def setRentTime(self, value):
        self._setString(7, value)

    def getIsRepairBtnVisible(self):
        return self._getBool(8)

    def setIsRepairBtnVisible(self, value):
        self._setBool(8, value)

    def getIsVehicleInBattle(self):
        return self._getBool(9)

    def setIsVehicleInBattle(self, value):
        self._setBool(9, value)

    def getIsEnoughMoney(self):
        return self._getBool(10)

    def setIsEnoughMoney(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(HangarBottomPanelViewModel, self)._initialize()
        self._addViewModelProperty('ammunition', ListModel())
        self._addViewModelProperty('abilities', ListModel())
        self._addViewModelProperty('rentPrice', ListModel())
        self._addStringProperty('vehName', '')
        self._addStringProperty('vehType', '')
        self._addStringProperty('rentState', '')
        self._addNumberProperty('rentDays', 0)
        self._addStringProperty('rentTime', '')
        self._addBoolProperty('isRepairBtnVisible', False)
        self._addBoolProperty('isVehicleInBattle', False)
        self._addBoolProperty('isEnoughMoney', True)
        self.onRentBtnClicked = self._addCommand('onRentBtnClicked')
        self.onRepairBtnClicked = self._addCommand('onRepairBtnClicked')

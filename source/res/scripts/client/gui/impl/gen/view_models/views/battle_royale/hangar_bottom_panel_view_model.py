# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/hangar_bottom_panel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class HangarBottomPanelViewModel(ViewModel):
    __slots__ = ('onModuleBtnClicked', 'onRepairBtnClicked')

    def __init__(self, properties=8, commands=2):
        super(HangarBottomPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def ammunition(self):
        return self._getViewModel(0)

    @property
    def abilities(self):
        return self._getViewModel(1)

    @property
    def repairPrice(self):
        return self._getViewModel(2)

    def getVehStatus(self):
        return self._getString(3)

    def setVehStatus(self, value):
        self._setString(3, value)

    def getIsModuleFirstEnter(self):
        return self._getBool(4)

    def setIsModuleFirstEnter(self, value):
        self._setBool(4, value)

    def getIsRepairBtnVisible(self):
        return self._getBool(5)

    def setIsRepairBtnVisible(self, value):
        self._setBool(5, value)

    def getIsRepairBtnDisabled(self):
        return self._getBool(6)

    def setIsRepairBtnDisabled(self, value):
        self._setBool(6, value)

    def getIsVehicleInBattle(self):
        return self._getBool(7)

    def setIsVehicleInBattle(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(HangarBottomPanelViewModel, self)._initialize()
        self._addViewModelProperty('ammunition', ListModel())
        self._addViewModelProperty('abilities', ListModel())
        self._addViewModelProperty('repairPrice', ListModel())
        self._addStringProperty('vehStatus', '')
        self._addBoolProperty('isModuleFirstEnter', False)
        self._addBoolProperty('isRepairBtnVisible', False)
        self._addBoolProperty('isRepairBtnDisabled', False)
        self._addBoolProperty('isVehicleInBattle', False)
        self.onModuleBtnClicked = self._addCommand('onModuleBtnClicked')
        self.onRepairBtnClicked = self._addCommand('onRepairBtnClicked')

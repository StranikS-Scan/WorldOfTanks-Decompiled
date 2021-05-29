# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_widget_3d_style_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class BattlePassWidget3DStyleViewModel(ViewModel):
    __slots__ = ('onSelectStyle', 'onPreviewClick')

    def __init__(self, properties=5, commands=2):
        super(BattlePassWidget3DStyleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    def getStyleName(self):
        return self._getString(1)

    def setStyleName(self, value):
        self._setString(1, value)

    def getStyleId(self):
        return self._getNumber(2)

    def setStyleId(self, value):
        self._setNumber(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getIsUnselectedPrevStyle(self):
        return self._getBool(4)

    def setIsUnselectedPrevStyle(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BattlePassWidget3DStyleViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addStringProperty('styleName', '')
        self._addNumberProperty('styleId', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isUnselectedPrevStyle', False)
        self.onSelectStyle = self._addCommand('onSelectStyle')
        self.onPreviewClick = self._addCommand('onPreviewClick')

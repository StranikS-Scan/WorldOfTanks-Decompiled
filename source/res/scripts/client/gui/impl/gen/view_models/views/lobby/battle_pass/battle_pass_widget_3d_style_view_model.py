# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_widget_3d_style_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_vehicle_widget_view_model import BattlePassVehicleWidgetViewModel

class BattlePassWidget3DStyleViewModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onMarathonPreviewClick', 'onSoundClick')

    def __init__(self, properties=6, commands=3):
        super(BattlePassWidget3DStyleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return BattlePassVehicleWidgetViewModel

    def getStyleName(self):
        return self._getString(1)

    def setStyleName(self, value):
        self._setString(1, value)

    def getStyleId(self):
        return self._getNumber(2)

    def setStyleId(self, value):
        self._setNumber(2, value)

    def getMarathonRewardId(self):
        return self._getString(3)

    def setMarathonRewardId(self, value):
        self._setString(3, value)

    def getIntCD(self):
        return self._getNumber(4)

    def setIntCD(self, value):
        self._setNumber(4, value)

    def getIsPaidReward(self):
        return self._getBool(5)

    def setIsPaidReward(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BattlePassWidget3DStyleViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', BattlePassVehicleWidgetViewModel())
        self._addStringProperty('styleName', '')
        self._addNumberProperty('styleId', 0)
        self._addStringProperty('marathonRewardId', '')
        self._addNumberProperty('intCD', 0)
        self._addBoolProperty('isPaidReward', False)
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onMarathonPreviewClick = self._addCommand('onMarathonPreviewClick')
        self.onSoundClick = self._addCommand('onSoundClick')

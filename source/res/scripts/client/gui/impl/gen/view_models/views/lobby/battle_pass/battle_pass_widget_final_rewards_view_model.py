# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_widget_final_rewards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.battle_pass.character_widget_view_model import CharacterWidgetViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.style_info_model import StyleInfoModel

class BattlePassWidgetFinalRewardsViewModel(ViewModel):
    __slots__ = ('showTankmen', 'onRewardPreviewClick')

    def __init__(self, properties=4, commands=2):
        super(BattlePassWidgetFinalRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    @property
    def tankmanInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getTankmanInfoType():
        return CharacterWidgetViewModel

    @property
    def styleInfo(self):
        return self._getViewModel(2)

    @staticmethod
    def getStyleInfoType():
        return StyleInfoModel

    def getBattleQuest(self):
        return self._getString(3)

    def setBattleQuest(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BattlePassWidgetFinalRewardsViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('tankmanInfo', CharacterWidgetViewModel())
        self._addViewModelProperty('styleInfo', StyleInfoModel())
        self._addStringProperty('battleQuest', '')
        self.showTankmen = self._addCommand('showTankmen')
        self.onRewardPreviewClick = self._addCommand('onRewardPreviewClick')

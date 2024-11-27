# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootbox_video_reward_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class LootboxVideoRewardViewModel(ViewModel):
    __slots__ = ('onClose', 'onVideoStarted')

    def __init__(self, properties=7, commands=2):
        super(LootboxVideoRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def reward(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardType():
        return BonusModel

    def getIsWindowAccessible(self):
        return self._getBool(1)

    def setIsWindowAccessible(self, value):
        self._setBool(1, value)

    def getVideoRes(self):
        return self._getString(2)

    def setVideoRes(self, value):
        self._setString(2, value)

    def getIsGuaranteedReward(self):
        return self._getBool(3)

    def setIsGuaranteedReward(self, value):
        self._setBool(3, value)

    def getIsElite(self):
        return self._getBool(4)

    def setIsElite(self, value):
        self._setBool(4, value)

    def getVehicleType(self):
        return self._getString(5)

    def setVehicleType(self, value):
        self._setString(5, value)

    def getVehicleLvl(self):
        return self._getNumber(6)

    def setVehicleLvl(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(LootboxVideoRewardViewModel, self)._initialize()
        self._addViewModelProperty('reward', UserListModel())
        self._addBoolProperty('isWindowAccessible', True)
        self._addStringProperty('videoRes', '')
        self._addBoolProperty('isGuaranteedReward', False)
        self._addBoolProperty('isElite', False)
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLvl', 0)
        self.onClose = self._addCommand('onClose')
        self.onVideoStarted = self._addCommand('onVideoStarted')

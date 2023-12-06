# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootbox_video_reward_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class LootboxVideoRewardViewModel(VehicleInfoModel):
    __slots__ = ('onClose', 'onVideoStarted')

    def __init__(self, properties=11, commands=2):
        super(LootboxVideoRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWindowAccessible(self):
        return self._getBool(8)

    def setIsWindowAccessible(self, value):
        self._setBool(8, value)

    def getVideoRes(self):
        return self._getResource(9)

    def setVideoRes(self, value):
        self._setResource(9, value)

    def getIsGuaranteedReward(self):
        return self._getBool(10)

    def setIsGuaranteedReward(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(LootboxVideoRewardViewModel, self)._initialize()
        self._addBoolProperty('isWindowAccessible', True)
        self._addResourceProperty('videoRes', R.invalid())
        self._addBoolProperty('isGuaranteedReward', False)
        self.onClose = self._addCommand('onClose')
        self.onVideoStarted = self._addCommand('onVideoStarted')
